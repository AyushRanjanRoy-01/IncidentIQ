"""Triage agent for alert filtering and actionability assessment.

Deterministic, fast first pass: decides whether an alert is actionable, how
urgent it is, and surfaces a dedup key. Runs with no LLM or network dependency.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.agents.state import AgentState
from app.models.enums import AlertSeverity

logger = structlog.get_logger(__name__)

# Severity -> urgency score.
_URGENCY = {
    AlertSeverity.CRITICAL.value: 1.0,
    AlertSeverity.WARNING.value: 0.6,
    AlertSeverity.INFO.value: 0.2,
}


class TriageAgent:
    """Filters noise and assesses alert actionability."""

    async def triage(self, state: AgentState) -> dict[str, Any]:
        breach_ratio = 0.0
        if state.threshold:
            breach_ratio = round(state.value / state.threshold, 3)

        # Info-severity alerts that only marginally breach the threshold are noise.
        is_noise = state.severity == AlertSeverity.INFO.value and 0 < breach_ratio < 1.1
        actionable = not is_noise
        urgency = _URGENCY.get(state.severity, 0.5)

        result = {
            "actionable": actionable,
            "is_noise": is_noise,
            "urgency": urgency,
            "breach_ratio": breach_ratio,
            "dedup_key": f"{state.service}:{state.metric}:{state.labels.get('env', 'unknown')}",
            "reason": (
                "Low-severity alert within tolerance — likely noise."
                if is_noise
                else f"{state.severity} breach of {state.metric} "
                f"({state.value} vs threshold {state.threshold})."
            ),
        }
        state.triage_result = result
        state.add_log("triage", result["reason"])
        logger.info("agent.triage", incident_id=state.incident_id, actionable=actionable)
        return result
