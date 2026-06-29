"""Kubernetes API integration.

Runs in **mock mode** by default (``settings.integrations_mock_mode`` /
``kubernetes_enabled=false``): operations are simulated and return realistic
results so the self-healing flow is fully demonstrable without a cluster. When
``kubernetes_enabled=true`` the methods use the official ``kubernetes`` client
(install the optional dependency) — those branches are clearly marked.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class KubernetesClient:
    """Client for Kubernetes operations (mock-mode by default)."""

    def __init__(self, enabled: bool | None = None, mock: bool | None = None) -> None:
        self.enabled = settings.kubernetes_enabled if enabled is None else enabled
        self.mock = settings.integrations_mock_mode if mock is None else mock

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    async def get_deployments(self, namespace: str = "production") -> list[dict[str, Any]]:
        if self.enabled and not self.mock:  # pragma: no cover - requires cluster
            return await self._real_get_deployments(namespace)
        return [
            {"name": "checkout-api", "namespace": namespace, "replicas": 4, "ready": 4},
            {"name": "payment-api", "namespace": namespace, "replicas": 3, "ready": 3},
        ]

    async def restart(
        self, service: str, namespace: str = "production", strategy: str = "rolling"
    ) -> dict[str, Any]:
        logger.info("k8s.restart", service=service, namespace=namespace, mock=self.mock)
        if self.enabled and not self.mock:  # pragma: no cover - requires cluster
            return await self._real_restart(service, namespace)
        return {
            "action": "restart",
            "service": service,
            "namespace": namespace,
            "strategy": strategy,
            "restarted_pods": 4,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    async def scale(
        self,
        service: str,
        namespace: str = "production",
        replicas: int | None = None,
        replicas_delta: int | None = None,
    ) -> dict[str, Any]:
        current = 4
        target = replicas if replicas is not None else current + (replicas_delta or 1)
        logger.info("k8s.scale", service=service, target=target, mock=self.mock)
        if self.enabled and not self.mock:  # pragma: no cover - requires cluster
            return await self._real_scale(service, namespace, target)
        return {
            "action": "scale",
            "service": service,
            "namespace": namespace,
            "from_replicas": current,
            "to_replicas": target,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    async def rollback(
        self, service: str, namespace: str = "production", to_version: str = "previous"
    ) -> dict[str, Any]:
        logger.info("k8s.rollback", service=service, to_version=to_version, mock=self.mock)
        if self.enabled and not self.mock:  # pragma: no cover - requires cluster
            return await self._real_rollback(service, namespace, to_version)
        return {
            "action": "rollback",
            "service": service,
            "namespace": namespace,
            "to_version": to_version,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    # ----------------------------------------------- real cluster (optional dep)
    def _api(self):  # pragma: no cover - requires cluster
        from kubernetes import client, config

        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()
        return client.AppsV1Api()

    async def _real_get_deployments(self, namespace: str):  # pragma: no cover
        api = self._api()
        deps = api.list_namespaced_deployment(namespace)
        return [
            {
                "name": d.metadata.name,
                "namespace": namespace,
                "replicas": d.spec.replicas,
                "ready": d.status.ready_replicas or 0,
            }
            for d in deps.items
        ]

    async def _real_restart(self, service: str, namespace: str):  # pragma: no cover
        api = self._api()
        body = {
            "spec": {
                "template": {"metadata": {"annotations": {"incidentiq/restartedAt": self._now()}}}
            }
        }
        api.patch_namespaced_deployment(service, namespace, body)
        return {"action": "restart", "service": service, "status": "patched", "mock": False}

    async def _real_scale(self, service: str, namespace: str, replicas: int):  # pragma: no cover
        api = self._api()
        api.patch_namespaced_deployment_scale(service, namespace, {"spec": {"replicas": replicas}})
        return {"action": "scale", "service": service, "to_replicas": replicas, "mock": False}

    async def _real_rollback(self, service, namespace, to_version):  # pragma: no cover
        # Real rollback typically uses `kubectl rollout undo`; left as an exercise.
        raise NotImplementedError("Real rollback requires rollout history handling.")
