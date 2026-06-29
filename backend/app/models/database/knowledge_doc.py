"""Knowledge base database models.

A document (runbook, postmortem, ...) is split into chunks; each chunk stores its
embedding as a JSON float array. Similarity search is performed in-process with
numpy (portable across SQLite/PostgreSQL). A pgvector-backed store is available as
a production upgrade — see ``app.rag.vector_store``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database.base import TimestampedModel, utcnow


class KnowledgeDocument(TimestampedModel):
    """A source document in the knowledge base."""

    __tablename__ = "knowledge_documents"

    doc_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(
        String, default="runbook", nullable=False
    )  # runbook|postmortem|doc
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String, default="local-hashing", nullable=False)
    # Renamed from reserved attribute name ``metadata`` (column kept as "meta").
    meta: Mapped[dict[str, Any]] = mapped_column("meta", JSON, default=dict, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class KnowledgeChunk(TimestampedModel):
    """A chunk of a document plus its embedding vector (stored as JSON floats)."""

    __tablename__ = "knowledge_chunks"

    chunk_id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.doc_id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column("meta", JSON, default=dict, nullable=False)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")
