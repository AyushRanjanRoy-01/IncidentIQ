"""Knowledge base schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_type: str
    content: str
    score: float


class KnowledgeDocOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doc_id: str
    title: str
    source_type: str
    source_url: str | None = None
    embedding_model: str
    indexed_at: datetime
