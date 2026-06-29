"""Supervisor agent orchestrating the specialist agents.

Coordinates the pipeline: triage -> context -> knowledge (RAG) -> RCA, then
aggregates the result. Dependencies (DB session, LLM provider, integrations) are
injected so the pipeline is easy to unit-test in isolation.
"""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.context_agent import ContextAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.llm import LLMProvider, get_llm_provider
from app.agents.rca_agent import RCAAgent
from app.agents.state import AgentState
from app.agents.triage_agent import TriageAgent
from app.models.database.alert import Alert
from app.models.database.incident import Incident
from app.rag.retriever import KnowledgeRetriever

logger = structlog.get_logger(__name__)


class SupervisorAgent:
    """Orchestrates execution of specialist agents for incident analysis."""

    def __init__(
        self,
        db: AsyncSession,
        llm: LLMProvider | None = None,
        integrations: Any | None = None,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self.db = db
        self.llm = llm or get_llm_provider()
        self.retriever = retriever or KnowledgeRetriever(db)
        self.triage = TriageAgent()
        self.context = ContextAgent(integrations=integrations)
        self.knowledge = KnowledgeAgent(self.retriever)
        self.rca = RCAAgent(self.llm)

    @staticmethod
    def _primary_alert(alerts: list[Alert]) -> Alert | None:
        if not alerts:
            return None
        order = {"critical": 0, "warning": 1, "info": 2}
        return sorted(alerts, key=lambda a: (order.get(a.severity, 9), -a.value))[0]

    def _build_state(self, incident: Incident, alerts: list[Alert]) -> AgentState:
        primary = self._primary_alert(alerts)
        state = AgentState(incident_id=incident.incident_id, service=incident.service)
        if primary is not None:
            state.alert_id = primary.alert_id
            state.metric = primary.metric
            state.severity = primary.severity
            state.value = primary.value
            state.threshold = primary.threshold
            state.labels = primary.labels or {}
            state.summary = primary.summary or incident.title
        else:
            state.severity = incident.severity
            state.summary = incident.title
        return state

    async def orchestrate(self, state: AgentState) -> AgentState:
        """Run the full agent pipeline over a prepared state."""
        await self.triage.triage(state)
        await self.context.build_context(state)
        await self.knowledge.retrieve_knowledge(state)
        await self.rca.analyze(state)
        return state

    async def run(self, incident: Incident, alerts: list[Alert]) -> dict[str, Any]:
        """Analyse an incident; returns the aggregated RCA result dict."""
        state = self._build_state(incident, alerts)
        logger.info("supervisor.start", incident_id=incident.incident_id, alerts=len(alerts))
        await self.orchestrate(state)
        result = dict(state.rca_result or {})
        result["agent_logs"] = state.agent_logs
        result["triage"] = state.triage_result
        result["errors"] = state.errors
        logger.info(
            "supervisor.done",
            incident_id=incident.incident_id,
            confidence=result.get("confidence"),
            action=(result.get("recommended_action") or {}).get("action_type"),
        )
        return result

    async def determine_confidence(self, analysis: dict[str, Any]) -> float:
        """Confidence for the aggregated analysis (mean of agent agreement scores)."""
        if not analysis:
            return 0.0
        scores = [v for v in analysis.values() if isinstance(v, int | float)]
        if not scores:
            return float(analysis.get("confidence", 0.0))
        return round(sum(scores) / len(scores), 3)
