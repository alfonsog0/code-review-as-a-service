from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db import init_db

from fastapi import Depends, HTTPException
from sqlmodel import Session
from app.db import get_session
from app.models import Snippet
from app.schemas import SnippetCreate, SnippetOut, CreateResponse, ReviewPayload
import app.llm as llm


app = FastAPI(title="Code Review-as-a-Service", version="0.1.0")

# Optional: permissive CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = os.path.dirname(os.getenv("DB_PATH", "/data/app.db"))
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    init_db()
    yield  # runs while app is active

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"service": "code-review-as-a-service", "docs": "/docs", "health": "/healthz"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/snippets", response_model=CreateResponse, status_code=201)
def create_snippet(payload: SnippetCreate, session: Session = Depends(get_session)):
    snippet = Snippet(language=payload.language, code=payload.code, lines=payload.lines)
    session.add(snippet)
    session.commit()
    session.refresh(snippet)

    try:
        review = llm.review_code(snippet.language, snippet.code, snippet.lines)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    snippet.review = review
    session.add(snippet)
    session.commit()
    session.refresh(snippet)

    return CreateResponse(id=snippet.id, review=ReviewPayload(**review))


@app.get("/snippets/{snippet_id}", response_model=SnippetOut)
def get_snippet(snippet_id: str, session: Session = Depends(get_session)):
    snippet = session.get(Snippet, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return SnippetOut(
        id=snippet.id,
        language=snippet.language,
        code=snippet.code,
        lines=snippet.lines,
        review=snippet.review,
    )

