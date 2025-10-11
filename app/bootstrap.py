import psycopg
import requests
import sys
import json


EMBED_PULL = "http://localhost:11434/api/pull"

OLLAMA_URL = "http://localhost:11434"

EMBED_MODEL = "nomic-embed-text"

class OllamaUnavailable(Exception):
    pass

def test_ollama_running():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/version")
        r.raise_for_status()
        json_data = r.json()
        print(f"Ollama running version {json_data['version']}")
    except requests.exceptions.ConnectionError:
        msg = (
            "Ollama is currently not running\n"
            "Run the following command in the cli\n"
            "ollama serve"  
        )
        raise OllamaUnavailable(msg)


def pull_embed_model():
    data = {"model": "nomic-embed-text", "stream": True}
    response = requests.post(EMBED_PULL, json=data,stream=True)

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("status", data))


def vector_creation():

    with psycopg.connect("postgresql://localhost/notes") as conn:

        with conn.cusor() as cur:

            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            cur.execute("""
                        CREATE TABLE notes IF NOTE EXISTS (
                            document_id PRIMARY KEY,
                            content TEXT,
                            embeding VECTOR(2000)

                        )""")


if __name__ == "__main__":
    try:
        test_ollama_running()
        pull_embed_model()
    except OllamaUnavailable as e:
        print(str(e))
        sys.exit(1)