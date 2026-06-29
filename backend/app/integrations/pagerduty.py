"""PagerDuty integration for incident management (mock-mode by default)."""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PagerDutyClient:
    """Trigger/resolve PagerDuty incidents (mock logs the event)."""

    def __init__(self, api_key: str | None = None, mock: bool | None = None) -> None:
        self.api_key = api_key or settings.pagerduty_api_key
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def trigger(self, summary: str, severity: str = "critical") -> dict[str, Any]:
        if not self.mock and self.api_key:  # pragma: no cover - requires PagerDuty
            return await self._real_trigger(summary, severity)
        logger.info("pagerduty.mock_trigger", summary=summary, severity=severity)
        return {"status": "triggered", "summary": summary, "severity": severity, "mock": True}

    async def _real_trigger(
        self, summary: str, severity: str
    ) -> dict[str, Any]:  # pragma: no cover
        import httpx

        payload = {
            "routing_key": self.api_key,
            "event_action": "trigger",
            "payload": {"summary": summary, "severity": severity, "source": "IncidentIQ"},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://events.pagerduty.com/v2/enqueue", json=payload)
            resp.raise_for_status()
            return resp.json()
