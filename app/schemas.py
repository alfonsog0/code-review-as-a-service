from typing import List, Optional
from pydantic import BaseModel, Field


class ReviewPayload(BaseModel):
    summary: str = Field(..., description="Short human-readable overview")
    suggestions: List[str] = Field(default_factory=list)
    findings: List[dict] = Field(default_factory=list, description="Structured items like {type, detail, line?}")
    rating: int = Field(..., ge=0, le=10)


class SnippetCreate(BaseModel):
    language: str
    code: str
    lines: Optional[str] = None


class SnippetOut(BaseModel):
    id: str
    language: str
    code: str
    lines: Optional[str] = None
    review: Optional[ReviewPayload] = None


class CreateResponse(BaseModel):
    id: str
    review: ReviewPayload