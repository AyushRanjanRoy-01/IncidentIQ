"""Knowledge agent using RAG for solution retrieval.

Searches the knowledge base (runbooks, postmortems) via the hybrid
``KnowledgeRetriever`` to surface the most relevant remediation guidance for the
incident at hand.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.agents.state import AgentState
from app.rag.retriever import KnowledgeRetriever

logger = structlog.get_logger(__name__)


class KnowledgeAgent:
    """Retrieves relevant knowledge from the RAG system."""

    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self.retriever = retriever

    def _query(self, state: AgentState) -> str:
        parts = [state.service, state.metric, state.severity, state.summary]
        if state.context_data and state.context_data.get("had_recent_deploy"):
            parts.append("recent deployment rollback")
        return " ".join(p for p in parts if p)

    async def retrieve_knowledge(self, state: AgentState, top_k: int = 4) -> list[dict[str, Any]]:
        query = self._query(state)
        chunks = await self.retriever.retrieve(query, top_k=top_k)
        results = [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "score": c.score,
                "content": c.content,
            }
            for c in chunks
        ]
        state.knowledge_results = results
        state.add_log("knowledge", f"Retrieved {len(results)} knowledge chunks for: {query!r}")
        logger.info(
            "agent.knowledge", incident_id=state.incident_id, hits=len(results), query=query
        )
        return results
