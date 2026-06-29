"""Tests for the RAG layer: embeddings, chunking, and knowledge search."""

import numpy as np
import pytest

from app.rag.chunker import DocumentChunker
from app.rag.embeddings import LocalHashingEmbedder
from app.rag.vector_store import cosine_similarity
from app.services.knowledge_service import KnowledgeService


def test_embedder_is_deterministic_and_sized():
    emb = LocalHashingEmbedder(dim=128)
    v1 = emb.embed("connection pool exhausted")
    v2 = emb.embed("connection pool exhausted")
    assert v1 == v2
    assert len(v1) == 128


def test_embedder_discriminates_topics():
    emb = LocalHashingEmbedder(dim=256)
    q = np.array(emb.embed("high api latency after recent deployment rollback"))
    latency = np.array(emb.embed("runbook high api latency deployment rollback connection pool"))
    oom = np.array(emb.embed("runbook out of memory oom killed pods heap restart"))
    assert cosine_similarity(q, latency) > cosine_similarity(q, oom)


def test_chunker_splits_markdown_sections():
    md = "# Title\n\n## Symptoms\nlatency is high\n\n## Resolution\nrollback the deployment"
    chunks = DocumentChunker(chunk_size=50, overlap=5).chunk_markdown(md, {"title": "Title"})
    sections = {c.meta.get("section") for c in chunks}
    assert {"Symptoms", "Resolution"}.issubset(sections)


@pytest.mark.asyncio
async def test_knowledge_search_returns_relevant_runbook(db_session):
    results = await KnowledgeService(db_session).search(
        "high api latency after deployment", top_k=3
    )
    assert results
    assert results[0].score > 0
    # The latency runbook should be among the top hits.
    assert any("latency" in r.title.lower() for r in results)
