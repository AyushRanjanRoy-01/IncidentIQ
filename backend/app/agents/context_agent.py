"""Context builder agent for gathering incident context.

Collects recent deployments, a metric snapshot, and representative logs for the
affected service. When an ``IntegrationHub`` is supplied it queries the real (or
mock-mode) integrations; otherwise it synthesises deterministic context derived
from the alert so the pipeline always has something to reason over.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.agents.state import AgentState

logger = structlog.get_logger(__name__)

# Metrics whose breaches are commonly caused by a recent deployment.
_DEPLOY_SENSITIVE = ("latency", "error", "5xx", "request")


class ContextAgent:
    """Gathers incident context from integrations (or a deterministic fallback)."""

    def __init__(self, integrations: Any | None = None) -> None:
        self.integrations = integrations

    async def build_context(self, state: AgentState) -> dict[str, Any]:
        deployments = await self._recent_deployments(state.service, state.metric)
        metrics = await self._metric_snapshot(state)
        logs = await self._logs(state.service)

        had_recent_deploy = bool(deployments)
        context = {
            "service": state.service,
            "had_recent_deploy": had_recent_deploy,
            "recent_deployments": deployments,
            "metrics_snapshot": metrics,
            "log_sample": logs,
        }
        state.context_data = context
        state.recent_deployments = deployments
        state.recent_metrics = metrics
        state.relevant_logs = logs
        state.add_log(
            "context",
            f"Gathered context: recent_deploy={had_recent_deploy}, "
            f"{len(logs)} log lines, {len(metrics)} metrics.",
        )
        logger.info(
            "agent.context", incident_id=state.incident_id, had_recent_deploy=had_recent_deploy
        )
        return context

    async def _recent_deployments(self, service: str, metric: str) -> list[dict[str, Any]]:
        if self.integrations is not None:
            try:
                return await self.integrations.get_recent_deployments(service)
            except Exception as exc:  # pragma: no cover - integration dependent
                logger.warning("context.deploy_lookup_failed", error=str(exc))
        # Deterministic fallback: deploy-sensitive metrics imply a recent change.
        if any(token in metric.lower() for token in _DEPLOY_SENSITIVE):
            return [
                {
                    "service": service,
                    "version": "v2.4.1",
                    "deployed_minutes_ago": 12,
                    "change": "Release v2.4.1 (connection pool + query changes)",
                }
            ]
        return []

    async def _metric_snapshot(self, state: AgentState) -> dict[str, Any]:
        if self.integrations is not None:
            try:
                return await self.integrations.get_metric_snapshot(state.service, state.metric)
            except Exception as exc:  # pragma: no cover - integration dependent
                logger.warning("context.metric_lookup_failed", error=str(exc))
        return {
            state.metric: state.value,
            f"{state.metric}_threshold": state.threshold,
            "breach": state.value > state.threshold if state.threshold else False,
        }

    async def _logs(self, service: str) -> list[str]:
        if self.integrations is not None:
            try:
                return await self.integrations.get_logs(service)
            except Exception as exc:  # pragma: no cover - integration dependent
                logger.warning("context.log_lookup_failed", error=str(exc))
        return [
            f"[{service}] ERROR connection pool exhausted (active=200, max=200)",
            f"[{service}] WARN request latency degraded after deploy",
        ]
