"""Slack integration for ChatOps (mock-mode by default)."""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SlackClient:
    """Post incident/approval notifications to Slack (mock logs the message)."""

    def __init__(self, token: str | None = None, mock: bool | None = None) -> None:
        self.token = token or settings.slack_bot_token
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def post_message(self, channel: str, text: str) -> dict[str, Any]:
        if not self.mock and self.token:  # pragma: no cover - requires Slack
            return await self._real_post(channel, text)
        logger.info("slack.mock_post", channel=channel, text=text)
        return {"ok": True, "channel": channel, "text": text, "mock": True}

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
