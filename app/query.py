import psycopg
import requests
import json
from colorama import Fore, Style, init
from pgvector.psycopg import register_vector
from ingest_notes import get_embed


OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2:3b"

def pull_llm_model():
    data = {"model": LLM_MODEL, "stream": True}
    response = requests.post("http://localhost:11434/api/pull", json=data,stream=True)

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print('\033[96m' + data.get("status", data) + '\033[0m')


def generate_response(document_text, user_question):
    PROMPT = f"""
            DOCUMENT:
            {document_text}

            QUESTION:
            {user_question}

            INSTRUCTIONS:
            Answer the QUESTION **using only the information in the DOCUMENT**.
            - If the DOCUMENT does not contain enough facts to answer, reply exactly with: NONE
            - Do not guess, infer, or use outside knowledge.
            - If you provide an answer, end with the DOCUMENT's title in parentheses, like this: (Document Title)
            Return only the final answer, nothing else.
            """

    data = {"model": LLM_MODEL, "prompt": PROMPT, "stream": True}
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=data, stream=True)
    acc = []
    for line in response.iter_lines():
        if not line:
            continue
        chunk = json.loads(line.decode("utf-8"))
        if "response" in chunk:
            piece = chunk["response"]
            acc.append(piece)
            # Live console stream:
            print(piece, end="", flush=True)
        if chunk.get("done"):
            break

            # chunk = json.loads(line)
            # print(chunk.message.content, end='', flush=True)
            # # print(data.get("response", data))
    print()
    return



def retrieve_context(query_embedding):
    
    with psycopg.connect("postgresql://localhost/notes") as conn:
        
        register_vector(conn)
        
        with conn.cursor() as cur:
            statement = """ 
                            SELECT title, content, 1- (embedding <=> %s::vector) as similarity
                            FROM notes
                            ORDER BY similarity DESC                               
                            LIMIT 5;
                        """
            cur.execute(statement, (query_embedding,))

            rows = cur.fetchall()

    return rows
            

def run():
    print("Ask a question (type 'q' to quit):")

    while True:
        user_question = input("> ").strip()
        if user_question == 'q':
            break
        
        print("\n" + Fore.CYAN + "═" * 50)
        context = retrieve_context(get_embed(user_question))
        generate_response(context, user_question)
        print(Fore.GREEN + Style.BRIGHT + "✅  ANSWER")
        print(Fore.CYAN + "═" * 50 + "\n" + Style.RESET_ALL)


if __name__ == "__main__":
    run()