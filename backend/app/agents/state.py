"""Shared state for agent communication.

A single mutable object that flows through the agent pipeline: each agent reads
the fields it needs and writes its results back. All fields have defaults so an
empty ``AgentState()`` is valid (useful for tests).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AgentState:
    """Shared state object for all agents."""

    # --- Identity ---
    incident_id: str = ""
    alert_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # --- Incident signal (populated from the triggering alert/incident) ---
    service: str = ""
    metric: str = ""
    severity: str = "warning"
    value: float = 0.0
    threshold: float = 0.0
    summary: str = ""
    labels: dict[str, Any] = field(default_factory=dict)

    # --- Context gathered by the context agent ---
    relevant_logs: list[str] = field(default_factory=list)
    recent_metrics: dict[str, Any] = field(default_factory=dict)
    recent_deployments: list[dict[str, Any]] = field(default_factory=list)

    # --- Analysis results ---
    triage_result: dict[str, Any] | None = None
    context_data: dict[str, Any] | None = None
    knowledge_results: list[dict[str, Any]] = field(default_factory=list)
    rca_result: dict[str, Any] | None = None

    # --- Recommended actions ---
    recommended_actions: list[dict[str, Any]] = field(default_factory=list)
    primary_action: dict[str, Any] | None = None
    confidence_score: float = 0.0

    # --- Metadata ---
    agent_logs: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def add_log(self, agent_name: str, message: str) -> None:
        self.agent_logs.setdefault(agent_name, []).append(message)

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-friendly dict (datetimes -> ISO strings)."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
