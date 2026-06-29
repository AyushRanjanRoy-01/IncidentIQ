"""RAG retriever combining vector similarity with a lexical keyword boost.

Hybrid scoring: ``final = vector_cosine + KEYWORD_WEIGHT * keyword_overlap``.
The keyword overlap (Jaccard over token sets) nudges results that share concrete
terms with the query (service names, metric names, error types) to the top — which
matters for short, jargon-heavy SRE queries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings import Embedder, get_embedder
from app.rag.vector_store import KnowledgeVectorStore

logger = structlog.get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
KEYWORD_WEIGHT = 0.25


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2}


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    content: str
    score: float


class KnowledgeRetriever:
    """Hybrid retriever over the knowledge base."""

    def __init__(self, db: AsyncSession, embedder: Embedder | None = None) -> None:
        self.db = db
        self.embedder = embedder or get_embedder()
        self.store = KnowledgeVectorStore(db)

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_vec = self.embedder.embed(query)
        # Over-fetch from the vector store, then re-rank with the keyword boost.
        candidates = await self.store.search(query_vec, top_k=max(top_k * 3, top_k))
        if not candidates:
            return []
        q_tokens = _tokens(query)
        reranked: list[RetrievedChunk] = []
        for cand in candidates:
            overlap = 0.0
            if q_tokens:
                c_tokens = _tokens(cand.content)
                if c_tokens:
                    overlap = len(q_tokens & c_tokens) / len(q_tokens | c_tokens)
            final = cand.score + KEYWORD_WEIGHT * overlap
            reranked.append(
                RetrievedChunk(
                    chunk_id=cand.chunk_id,
                    doc_id=cand.doc_id,
                    content=cand.content,
                    score=round(final, 4),
                )
            )
        reranked.sort(key=lambda c: c.score, reverse=True)
        return reranked[:top_k]


# Backwards-compatible alias for the original scaffold name.
RAGRetriever = KnowledgeRetriever
