"""Prometheus metrics integration.

Mock mode returns a synthetic series. Live mode queries a real Prometheus server
over its HTTP API.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PrometheusClient:
    name = "prometheus"

    def __init__(self, base_url: str | None = None, mock: bool | None = None) -> None:
        self.base_url = (base_url or settings.prometheus_url).rstrip("/")
        self.mock = settings.integrations_mock_mode if mock is None else mock

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    async def query(self, promql: str) -> list[dict[str, Any]]:
        if not self.mock:
            return await self._real_query(promql)
        return [{"metric": {"__query__": promql}, "value": [0, "1"]}]

    async def metric_snapshot(self, service: str, metric: str) -> dict[str, Any]:
        if not self.mock:  # pragma: no cover - requires Prometheus
            series = await self._real_query(f'{metric}{{service="{service}"}}')
            return {"service": service, "metric": metric, "series": series}
        return {
            "service": service,
            "metric": metric,
            "last_5m": [1.0, 1.1, 1.4, 1.9, 2.5],
            "trend": "rising",
        }

    async def _real_query(self, promql: str) -> list[dict[str, Any]]:  # pragma: no cover
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/api/v1/query", params={"query": promql})
            resp.raise_for_status()
            return resp.json().get("data", {}).get("result", [])

    async def healthcheck(self) -> dict[str, Any]:
        if self.mock:
            return {
                "name": self.name,
                "mode": "mock",
                "configured": self.configured,
                "ok": True,
                "detail": "mock mode",
            }
        try:  # pragma: no cover - network dependent
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/-/healthy")
            ok = resp.status_code == 200
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": ok,
                "detail": f"{self.base_url} ({resp.status_code})",
            }
        except Exception as exc:  # pragma: no cover
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": False,
                "detail": f"{self.base_url}: {exc}",
            }
