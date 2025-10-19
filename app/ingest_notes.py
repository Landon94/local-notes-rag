import requests
import psycopg
from pgvector.psycopg import register_vector
import json
import os
import re

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"


def get_embed(text: str):
    data = {"model": EMBED_MODEL, "input": text}
    response = requests.post(f"{OLLAMA_URL}/api/embed", json=data)
    # data = response.json()

    return response.json()["embeddings"][0]

    # print(data)
    # print(type(data['embeddings'][0]))


def text_splitter(text: str, tokens: int=700, overlap: int=120):
    chunks = []
    start = 0
    text_end = len(text)

    while start <= text_end:
        end = min(start + tokens, text_end)
        chunk = text[start:end]
        chunks.append(chunk)
        start += end - overlap
    
    return chunks


def embed_chunks(doc_title: str, chunks: list[str]):
    with psycopg.connect("postgresql://localhost/notes") as conn:
        register_vector(conn)
        with conn.cursor() as cur:

            for chunk in chunks:

                statement = """ 
                                INSERT INTO notes (title, content, embedding)
                                VALUES (%s, %s, %s)
                            """
                cur.execute(statement, (doc_title, chunk, get_embed(chunk)))
            
        conn.commit() 


def remove_extra_spaces(text):
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def reset_table():
    """TRUNCATE TABLE notes RESTART IDENTITY;"""
    pass


def ingest_folder(rootdir="data"):
    for _, _, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".md"):

                file_path = os.path.join(rootdir, file)
                print(file)

                with open(file_path, 'r', encoding="utf-8") as f:
                    data = f.read()
                    text = remove_extra_spaces(data)
                    chunks = text_splitter(text,750,100)
                    embed_chunks(file, chunks)
                    

if __name__ == "__main__":
    ingest_folder()
