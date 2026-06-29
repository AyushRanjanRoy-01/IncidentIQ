"""GitHub integration for deployment and PR info (mock-mode by default)."""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class GitHubClient:
    """Fetch recent deployments/commits (mock-mode returns synthetic data)."""

    def __init__(self, token: str | None = None, mock: bool | None = None) -> None:
        self.token = token or settings.github_token
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def get_recent_deployments(self, service: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.mock and self.token:  # pragma: no cover - requires GitHub
            return await self._real_recent_deployments(service, limit)
        # Mock: a deployment ~12 minutes ago, a plausible RCA trigger.
        return [
            {
                "service": service,
                "version": "v2.4.1",
                "sha": "a1b2c3d",
                "deployed_minutes_ago": 12,
                "change": "Release v2.4.1 (connection pool + query changes)",
            }
        ]

    async def _real_recent_deployments(self, service, limit):  # pragma: no cover
        import httpx

        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            resp = await client.get(
                f"https://api.github.com/repos/{service}/deployments",
                params={"per_page": limit},
            )
            resp.raise_for_status()
            return resp.json()
