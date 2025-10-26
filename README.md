# Code Review-as-a-Service

A **FastAPI** service that accepts code snippets and returns a **structured LLM review**.  
Each snippet and its review are stored in a lightweight **SQLite** database (`app.db`).

---

## Features

- `POST /snippets` — submit code for automated review  
- `GET /snippets/{id}` — retrieve a stored snippet and its review  
- Built-in Swagger UI at [http://localhost:8000/docs]
- Persistent storage using SQLite  
- Ready to run with Docker or locally  
- Includes unit and integration tests (with a stubbed LLM)

---

## Environment Setup

Copy the example environment file and set your OpenAI API key.

```bash
cp .env.example .env
# then edit .env
OPENAI_API_KEY=sk-...
# optional
DATABASE_URL=sqlite:///app.db

## Run with Docker Compose
docker compose up --build

Service available at:
http://localhost:8000

Docs available at:
http://localhost:8000/docs

## Run Locally (without Docker)
pip install -r requirements.txt
uvicorn app.main:app --reload

## API Examples

**Submit a Snippet for Review**
jq -n --arg language python \
      --rawfile code app/llm.py \
      --arg lines "28-57" \
      '{language:$language, code:$code, lines:$lines}' \
| curl -s http://localhost:8000/snippets \
    -H 'Content-Type: application/json' \
    --data @- | jq

**Retrieve a Snippet and Its Review**
curl -s http://localhost:8000/snippets/<ID> | jq

**Test Using Swagger UI**
Go to:
http://localhost:8000/docs

Select POST /snippets → Try it out and use a body like:
{
  "language": "python",
  "code": "def review_code(language: str, code: str, lines: Optional[str]) -> Dict:\\n    return {}",
  "lines": "28-57"
}

---

## Database (SQLite)

Schema (from PRAGMA table_info(snippet);):
id (VARCHAR, PK)
language (VARCHAR, required)
code (VARCHAR, required)
lines (VARCHAR, optional)
review (JSON, optional)

Inspect locally (host)

sqlite3 app.db ".tables"
sqlite3 app.db "PRAGMA table_info(snippet);"

# Recent rows (adjust LIMIT as desired)
sqlite3 app.db "SELECT id, language, substr(code,1,80) || '…' AS code, COALESCE(lines,'(none)') AS lines FROM snippet ORDER BY rowid DESC LIMIT 5;"

# Show the stored review JSON for a specific id
sqlite3 app.db "SELECT id, json_extract(review,'$.summary') AS summary, json_extract(review,'$.rating') AS rating FROM snippet ORDER BY rowid DESC LIMIT 5;"

---

## Testing

Run all unit and integration tests:

pytest -q

**Testing Specific Code Snippets**
You can send:

A small snippet file containing only one function, or

A full file with lines="start-end" to focus the review.

Example:
cat > snippet_tmp.py <<'PY'
def review_code(language: str, code: str, lines: str | None) -> dict:
    return {"ok": True}
PY

jq -n --arg language python \
      --rawfile code snippet_tmp.py \
      --arg lines "(none)" \
      '{language:$language, code:$code, lines:$lines}' \
| curl -s http://localhost:8000/snippets \
    -H 'Content-Type: application/json' \
    --data @- | jq

---

## Design Choices
FastAPI + Pydantic for typed, ergonomic APIs.

SQLite for zero-setup persistence.

OpenAI with response_format={"type":"json_object"} for robust parsing.

Graceful fallback when LLM returns non-JSON (summary only, sensible defaults).

---

## Future Additions (1-week plan)
Auth + rate limiting.
Inline, line-anchored comments in the response.
Static linters (flake8/mypy/go vet) merged into review.
GitHub PR webhook/CLI integration.
Retry/backoff/circuit-breaker around LLM calls.
Metrics + tracing (Prometheus, OpenTelemetry).

---

## AI Usage Statement

I used ChatGPT extensively to scaffold and iterate on this project.
Initially, AI-generated code often skipped intermediate testing and jumped to conclusions.
To mitigate that, I prompted it step-by-step, verified each step manually with curl, Swagger, and pytest, and ensured that every component (API, DB, Docker setup) was validated before integration.

---

## Time spent
2:15 for the code itself, 1 additional hour for review and creafting the README.md a re-testing