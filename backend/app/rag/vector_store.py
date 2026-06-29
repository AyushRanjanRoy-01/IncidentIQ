"""Vector similarity primitives + DB-backed knowledge store.

The default store keeps chunk embeddings as JSON float arrays in the relational
database (``knowledge_chunks``) and performs cosine-similarity ranking in-process
with numpy. This is portable (SQLite or PostgreSQL), correct, and fast enough for
the knowledge-base corpus.

For large corpora, switch to a pgvector-backed index (PostgreSQL + the ``pgvector``
extension); the ``PgVectorStore`` class documents that upgrade path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import structlog
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.knowledge_doc import KnowledgeChunk

logger = structlog.get_logger(__name__)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors (0.0 if either is zero)."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


@dataclass
class ScoredChunk:
    chunk_id: str
    doc_id: str
    content: str
    score: float
    meta: dict[str, Any]


class KnowledgeVectorStore:
    """DB-backed vector store over the ``knowledge_chunks`` table."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        self.db.add_all(chunks)
        await self.db.flush()

    async def delete_document_chunks(self, doc_id: str) -> None:
        await self.db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.doc_id == doc_id))

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[ScoredChunk]:
        """Rank all stored chunks by cosine similarity to the query vector."""
        rows = (await self.db.execute(select(KnowledgeChunk))).scalars().all()
        if not rows:
            return []
        q = np.asarray(query_embedding, dtype=np.float32)
        scored: list[ScoredChunk] = []
        for chunk in rows:
            emb = chunk.embedding or []
            if not emb or len(emb) != len(q):
                continue
            score = cosine_similarity(q, np.asarray(emb, dtype=np.float32))
            scored.append(
                ScoredChunk(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    content=chunk.content,
                    score=score,
                    meta=chunk.meta or {},
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]


class PgVectorStore:  # pragma: no cover - documented production upgrade path
    """Placeholder for a pgvector-backed store.

    Production deployments can store embeddings in a ``vector`` column and let
    PostgreSQL perform ANN search:

        CREATE EXTENSION IF NOT EXISTS vector;
        ALTER TABLE knowledge_chunks ADD COLUMN embedding_vec vector(1536);
        CREATE INDEX ON knowledge_chunks USING ivfflat (embedding_vec vector_cosine_ops);

    then ``ORDER BY embedding_vec <=> :query LIMIT :k``. Install the ``pgvector``
    extra from requirements-optional.txt to enable this.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "PgVectorStore is a documented upgrade path; the default "
            "KnowledgeVectorStore is used out of the box."
        )


# Backwards-compatible alias for the original scaffold name.
VectorStore = KnowledgeVectorStore
