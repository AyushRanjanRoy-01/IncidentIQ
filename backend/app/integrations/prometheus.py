"""Prometheus metrics integration (mock-mode by default)."""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PrometheusClient:
    """Query Prometheus (mock-mode returns synthetic series for demos)."""

    def __init__(self, base_url: str | None = None, mock: bool | None = None) -> None:
        self.base_url = base_url or settings.prometheus_url
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def query(self, promql: str) -> list[dict[str, Any]]:
        if not self.mock:  # pragma: no cover - requires Prometheus
            return await self._real_query(promql)
        return [{"metric": {"__query__": promql}, "value": [0, "1"]}]

    async def metric_snapshot(self, service: str, metric: str) -> dict[str, Any]:
        """A small synthetic snapshot showing recent degradation for the metric."""
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
