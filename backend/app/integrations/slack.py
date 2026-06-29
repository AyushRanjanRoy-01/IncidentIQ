"""Slack integration for ChatOps.

Mock mode (default) logs messages. Live mode posts to the Slack Web API. In live
mode with no token configured, posting is a no-op warning (notifications must never
block the incident flow) and ``healthcheck`` reports the integration as unconfigured.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SlackClient:
    name = "slack"

    def __init__(
        self, token: str | None = None, channel: str | None = None, mock: bool | None = None
    ) -> None:
        self.token = token if token is not None else settings.slack_bot_token
        self.channel = channel or settings.slack_channel
        self.mock = settings.integrations_mock_mode if mock is None else mock

    @property
    def configured(self) -> bool:
        return bool(self.token)

    async def post_message(self, channel: str, text: str) -> dict[str, Any]:
        if self.mock:
            logger.info("slack.mock_post", channel=channel, text=text)
            return {"ok": True, "channel": channel, "text": text, "mock": True}
        if not self.configured:
            logger.warning("slack.not_configured", hint="set SLACK_BOT_TOKEN")
            return {"ok": False, "error": "SLACK_BOT_TOKEN not set"}
        try:
            return await self._real_post(channel, text)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("slack.post_failed", error=str(exc))
            return {"ok": False, "error": str(exc)}

    async def _real_post(self, channel: str, text: str) -> dict[str, Any]:  # pragma: no cover
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"channel": channel, "text": text},
            )
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
        if not self.configured:
            return {
                "name": self.name,
                "mode": "live",
                "configured": False,
                "ok": False,
                "detail": "SLACK_BOT_TOKEN not set",
            }
        try:  # pragma: no cover - network dependent
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
            data = resp.json()
            ok = bool(data.get("ok"))
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": ok,
                "detail": f"team={data.get('team')}" if ok else data.get("error", "auth failed"),
            }
        except Exception as exc:  # pragma: no cover
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": False,
                "detail": str(exc),
            }
