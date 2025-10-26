from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import JSON as SAJSON
import uuid


class Snippet(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    language: str
    code: str
    lines: Optional[str] = None
    # Store structured review as JSON; works on SQLite (text) and Postgres (native JSON)
    review: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(SAJSON))
