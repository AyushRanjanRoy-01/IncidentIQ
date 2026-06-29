"""Integration hub.

A single entry point that wires together all external-system clients and exposes
the convenience methods the agents and remediation executor need. Mock mode is the
default; set ``INTEGRATIONS_MOCK_MODE=false`` (plus per-integration credentials) to
go live. See ``docs/ONBOARDING.md`` for the connection guide.
"""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Any

import structlog

from app.core.config import settings
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

    # --- notifications (ChatOps / paging) — best-effort, never block the flow ---
    async def notify(
        self, message: str, severity: str = "warning", channel: str | None = None
    ) -> None:
        channel = channel or settings.slack_channel
        try:
            await self.slack.post_message(channel, message)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("notify.slack_failed", error=str(exc))
        if severity == "critical":
            try:
                await self.pagerduty.trigger(message, severity)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("notify.pagerduty_failed", error=str(exc))

    # --- connection validation (powers onboarding + the status endpoint) ---
    async def status(self) -> dict[str, Any]:
        clients = [
            self.kubernetes,
            self.prometheus,
            self.github,
            self.slack,
            self.pagerduty,
            self.terraform,
        ]
        results = await asyncio.gather(*(c.healthcheck() for c in clients), return_exceptions=True)
        checks = []
        for client, res in zip(clients, results, strict=False):
            if isinstance(res, Exception):
                checks.append({"name": client.name, "ok": False, "detail": str(res)})
            else:
                checks.append(res)
        return {
            "mock_mode": settings.integrations_mock_mode,
            "all_ok": all(c.get("ok") for c in checks),
            "integrations": checks,
        }


@lru_cache
def get_integration_hub() -> IntegrationHub:
    """Return the cached IntegrationHub singleton."""
    return IntegrationHub()
