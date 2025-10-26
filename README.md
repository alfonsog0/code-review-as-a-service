# Code Review-as-a-Service

Small FastAPI service that accepts code snippets and returns a structured LLM review. Stores snippet + review in SQLite.

## Run with Docker

1) Copy env template and set your OpenAI key:
```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
