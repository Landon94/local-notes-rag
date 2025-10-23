# local-notes-rag

![status](https://img.shields.io/badge/status-work--in--progress-yellow)

## Overview



**WARNING: This Project is Not Finished**

This is a local RAG system built with Python, Postgres, pgvector, and Ollama.
It emebeds Markdown notes into a vector database, then retrieves the most relevant
chunk using cosine similarity, and uses a local llm to answer querys with context.

##  To Do's

- [x] Basic ingestion + query flow working  
- [ ] Dockerized stack (Postgres + Ollama + app)  
- [ ] FastAPI service layer  
- [ ] Streamlit UI  
