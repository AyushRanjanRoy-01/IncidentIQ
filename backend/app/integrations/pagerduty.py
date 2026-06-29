"""PagerDuty integration (Events API v2).

Mock mode logs the event. Live mode enqueues a real PagerDuty event using a
routing/integration key (``PAGERDUTY_ROUTING_KEY`` or ``PAGERDUTY_API_KEY``).
"""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PagerDutyClient:
    name = "pagerduty"

    def __init__(self, routing_key: str | None = None, mock: bool | None = None) -> None:
        self.routing_key = (
            routing_key or settings.pagerduty_routing_key or settings.pagerduty_api_key
        )
        self.mock = settings.integrations_mock_mode if mock is None else mock

    @property
    def configured(self) -> bool:
        return bool(self.routing_key)

    async def trigger(self, summary: str, severity: str = "critical") -> dict[str, Any]:
        if self.mock:
            logger.info("pagerduty.mock_trigger", summary=summary, severity=severity)
            return {"status": "triggered", "summary": summary, "severity": severity, "mock": True}
        if not self.configured:
            logger.warning("pagerduty.not_configured", hint="set PAGERDUTY_ROUTING_KEY")
            return {"status": "skipped", "error": "PAGERDUTY_ROUTING_KEY not set"}
        try:
            return await self._real_trigger(summary, severity)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("pagerduty.trigger_failed", error=str(exc))
            return {"status": "error", "error": str(exc)}

    async def _real_trigger(
        self, summary: str, severity: str
    ) -> dict[str, Any]:  # pragma: no cover
        import httpx

        # PagerDuty severity vocabulary: critical|error|warning|info
        pd_sev = severity if severity in {"critical", "error", "warning", "info"} else "warning"
        payload = {
            "routing_key": self.routing_key,
            "event_action": "trigger",
            "payload": {"summary": summary, "severity": pd_sev, "source": "IncidentIQ"},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://events.pagerduty.com/v2/enqueue", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def healthcheck(self) -> dict[str, Any]:
        if self.mock:
            return {
                "name": self.name,
                "mode": "mock",
                "configured": self.configured,
                "ok": True,
                "detail": "mock mode",
            }
        # No safe read-only validation endpoint; report based on key presence.
        return {
            "name": self.name,
            "mode": "live",
            "configured": self.configured,
            "ok": self.configured,
            "detail": "routing key present" if self.configured else "PAGERDUTY_ROUTING_KEY not set",
        }
