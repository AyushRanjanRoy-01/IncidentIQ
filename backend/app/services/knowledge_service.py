"""Knowledge service: ingest documents into the vector store and search them."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.knowledge_doc import KnowledgeChunk, KnowledgeDocument
from app.models.schemas.knowledge import KnowledgeSearchResult
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import get_embedder
from app.rag.retriever import KnowledgeRetriever
from app.rag.vector_store import KnowledgeVectorStore

logger = structlog.get_logger(__name__)


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "doc"


class KnowledgeService:
    """Indexes runbooks/postmortems and serves semantic search over them."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.embedder = get_embedder()
        self.chunker = DocumentChunker()
        self.store = KnowledgeVectorStore(db)

    async def index_document(
        self,
        *,
        title: str,
        content: str,
        source_type: str = "runbook",
        source_url: str | None = None,
        meta: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> KnowledgeDocument:
        doc_id = doc_id or _slug(title)
        # Re-index: drop any existing document + chunks with this id.
        existing = await self.db.get(KnowledgeDocument, doc_id)
        if existing is not None:
            await self.store.delete_document_chunks(doc_id)
            await self.db.delete(existing)
            await self.db.flush()

        doc = KnowledgeDocument(
            doc_id=doc_id,
            title=title,
            source_type=source_type,
            source_url=source_url,
            content=content,
            embedding_model=self.embedder.name,
            meta=meta or {},
        )
        self.db.add(doc)

        chunks = self.chunker.chunk_markdown(content, {"title": title})
        embeddings = self.embedder.embed_batch([c.content for c in chunks])
        chunk_rows = [
            KnowledgeChunk(
                chunk_id=f"{doc_id}::{c.index}",
                doc_id=doc_id,
                chunk_index=c.index,
                content=c.content,
                embedding=emb,
                meta=c.meta,
            )
            for c, emb in zip(chunks, embeddings, strict=False)
        ]
        await self.store.add_chunks(chunk_rows)
        logger.info("knowledge.indexed", doc_id=doc_id, chunks=len(chunk_rows))
        return doc

    async def index_directory(self, directory: str | Path) -> int:
        """Index all markdown files under ``directory`` (recursively)."""
        root = Path(directory)
        if not root.exists():
            logger.warning("knowledge.dir_missing", directory=str(root))
            return 0
        count = 0
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = self._title_from_markdown(text, fallback=path.stem)
            source_type = (
                "postmortem"
                if "postmortem" in path.parts or "postmortems" in path.parts
                else "runbook"
            )
            await self.index_document(
                title=title,
                content=text,
                source_type=source_type,
                source_url=str(path),
                doc_id=_slug(f"{source_type}-{path.stem}"),
            )
            count += 1
        return count

    @staticmethod
    def _title_from_markdown(text: str, fallback: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return fallback.replace("_", " ").title()

    async def search(self, query: str, top_k: int = 5) -> list[KnowledgeSearchResult]:
        retriever = KnowledgeRetriever(self.db, self.embedder)
        chunks = await retriever.retrieve(query, top_k=top_k)
        if not chunks:
            return []
        doc_ids = {c.doc_id for c in chunks}
        docs = (
            (
                await self.db.execute(
                    select(KnowledgeDocument).where(KnowledgeDocument.doc_id.in_(doc_ids))
                )
            )
            .scalars()
            .all()
        )
        titles = {d.doc_id: d.title for d in docs}
        types = {d.doc_id: d.source_type for d in docs}
        return [
            KnowledgeSearchResult(
                chunk_id=c.chunk_id,
                doc_id=c.doc_id,
                title=titles.get(c.doc_id, c.doc_id),
                source_type=types.get(c.doc_id, "doc"),
                content=c.content,
                score=c.score,
            )
            for c in chunks
        ]

    async def list_documents(self) -> list[KnowledgeDocument]:
        return list(
            (await self.db.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.title)))
            .scalars()
            .all()
        )

    async def count(self) -> int:
        return int(
            (await self.db.execute(select(func.count(KnowledgeDocument.doc_id)))).scalar_one()
        )
