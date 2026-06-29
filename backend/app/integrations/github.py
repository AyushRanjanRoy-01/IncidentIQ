"""GitHub integration for deployment/PR context.

Mock mode returns a synthetic recent deployment. Live mode reads the GitHub
Deployments API for the configured repo (``GITHUB_REPO`` = ``owner/repo``).
"""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class GitHubClient:
    name = "github"

    def __init__(
        self, token: str | None = None, repo: str | None = None, mock: bool | None = None
    ) -> None:
        self.token = token if token is not None else settings.github_token
        self.repo = repo or settings.github_repo
        self.mock = settings.integrations_mock_mode if mock is None else mock

    @property
    def configured(self) -> bool:
        return bool(self.token)

    async def get_recent_deployments(self, service: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.mock and self.configured:
            try:
                return await self._real_recent_deployments(service, limit)
            except Exception as exc:  # pragma: no cover - network dependent
                logger.warning("github.deploy_lookup_failed", error=str(exc))
                return []
        if not self.mock and not self.configured:
            return []
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

    async def _real_recent_deployments(self, service: str, limit: int):  # pragma: no cover
        import httpx

        repo = self.repo or service
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            resp = await client.get(
                f"https://api.github.com/repos/{repo}/deployments", params={"per_page": limit}
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
                "detail": "GITHUB_TOKEN not set",
            }
        try:  # pragma: no cover - network dependent
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
            ok = resp.status_code == 200
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": ok,
                "detail": f"login={resp.json().get('login')}" if ok else f"HTTP {resp.status_code}",
            }
        except Exception as exc:  # pragma: no cover
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": False,
                "detail": str(exc),
            }
