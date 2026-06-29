"""Integration hub.

A single entry point that wires together all external-system clients and exposes
the convenience methods the agents and remediation executor need. Everything runs
in mock mode by default, so the platform is fully functional with no external
accounts or clusters.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import structlog

from app.integrations.github import GitHubClient
from app.integrations.kubernetes import KubernetesClient
from app.integrations.pagerduty import PagerDutyClient
from app.integrations.prometheus import PrometheusClient
from app.integrations.slack import SlackClient
from app.integrations.terraform import TerraformClient

logger = structlog.get_logger(__name__)


class IntegrationHub:
    """Aggregates external integrations behind a single, mockable surface."""

    def __init__(self) -> None:
        self.kubernetes = KubernetesClient()
        self.prometheus = PrometheusClient()
        self.github = GitHubClient()
        self.slack = SlackClient()
        self.pagerduty = PagerDutyClient()
        self.terraform = TerraformClient()

    # --- methods consumed by the ContextAgent ---
    async def get_recent_deployments(self, service: str) -> list[dict[str, Any]]:
        return await self.github.get_recent_deployments(service)

    async def get_metric_snapshot(self, service: str, metric: str) -> dict[str, Any]:
        return await self.prometheus.metric_snapshot(service, metric)

    async def get_logs(self, service: str) -> list[str]:
        # Logs aren't a first-class integration here; synthesise a representative sample.
        return [
            f"[{service}] ERROR upstream timeout (5xx) rate climbing",
            f"[{service}] WARN p95 latency above SLO after recent change",
        ]

    # --- notifications (ChatOps / paging) ---
    async def notify(self, message: str, severity: str = "warning", channel: str = "#sre") -> None:
        await self.slack.post_message(channel, message)
        if severity == "critical":
            await self.pagerduty.trigger(message, severity)


@lru_cache
def get_integration_hub() -> IntegrationHub:
    """Return the cached IntegrationHub singleton."""
    return IntegrationHub()
