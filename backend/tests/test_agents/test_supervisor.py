"""Tests for the agent pipeline (triage, RCA, supervisor orchestration)."""

import pytest

from app.agents.llm import MockLLMProvider
from app.agents.rca_agent import RCAAgent
from app.agents.state import AgentState
from app.agents.supervisor import SupervisorAgent
from app.agents.triage_agent import TriageAgent
from app.models.database.alert import Alert
from app.models.database.incident import Incident
from app.models.enums import ActionType


@pytest.mark.asyncio
async def test_triage_flags_critical_actionable():
    state = AgentState(
        service="checkout-api",
        metric="api_latency_p95",
        severity="critical",
        value=2500,
        threshold=1000,
    )
    result = await TriageAgent().triage(state)
    assert result["actionable"] is True
    assert result["urgency"] == 1.0
    assert result["breach_ratio"] == 2.5


@pytest.mark.asyncio
async def test_rca_recommends_rollback_after_deploy():
    state = AgentState(
        service="checkout-api",
        metric="api_latency_p95",
        severity="critical",
        value=2500,
        threshold=1000,
    )
    state.context_data = {"had_recent_deploy": True}
    result = await RCAAgent(MockLLMProvider()).analyze(state)
    assert result["recommended_action"]["action_type"] == ActionType.ROLLBACK.value
    assert 0.0 < result["confidence"] <= 0.95
    assert result["provider"] == "deterministic"


@pytest.mark.asyncio
async def test_rca_recommends_restart_for_memory():
    state = AgentState(
        service="user-api", metric="memory_usage", severity="critical", value=92, threshold=85
    )
    result = await RCAAgent(MockLLMProvider()).analyze(state)
    assert result["recommended_action"]["action_type"] == ActionType.RESTART.value


@pytest.mark.asyncio
async def test_supervisor_full_pipeline(db_session):
    alert = Alert(
        alert_id="a-sup-1",
        service="checkout-api",
        severity="critical",
        metric="api_latency_p95",
        value=2500,
        threshold=1000,
        fingerprint="fp1",
        labels={"env": "production"},
    )
    incident = Incident(
        incident_id="inc-sup-1",
        title="High latency on checkout-api",
        service="checkout-api",
        severity="critical",
    )
    db_session.add_all([alert, incident])
    await db_session.flush()

    result = await SupervisorAgent(db_session).run(incident, [alert])

    assert result["recommended_action"]["action_type"] in {a.value for a in ActionType}
    assert result["confidence"] > 0
    assert "triage" in result["agent_logs"]
    assert result["knowledge_doc_ids"]  # RAG matched at least one runbook
