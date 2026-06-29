"""Kubernetes integration.

Mock mode (default) simulates operations. Live mode (``KUBERNETES_ENABLED=true``
and ``INTEGRATIONS_MOCK_MODE=false``) uses the official ``kubernetes`` client
against the cluster reachable via in-cluster config or the local kubeconfig.

Implemented live actions: list deployments, rolling restart, scale, and rollback
(reverts the Deployment's pod template to the previous ReplicaSet revision —
equivalent to ``kubectl rollout undo``).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class KubernetesClient:
    name = "kubernetes"

    def __init__(self, enabled: bool | None = None, mock: bool | None = None) -> None:
        self.enabled = settings.kubernetes_enabled if enabled is None else enabled
        self.mock = settings.integrations_mock_mode if mock is None else mock
        self.default_namespace = settings.kubernetes_namespace

    @property
    def live(self) -> bool:
        return self.enabled and not self.mock

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def _ns(self, namespace: str | None) -> str:
        return namespace or self.default_namespace

    # --------------------------------------------------------------- operations
    async def get_deployments(self, namespace: str | None = None) -> list[dict[str, Any]]:
        ns = self._ns(namespace)
        if self.live:  # pragma: no cover - requires cluster
            return await self._real_get_deployments(ns)
        return [
            {"name": "checkout-api", "namespace": ns, "replicas": 4, "ready": 4},
            {"name": "payment-api", "namespace": ns, "replicas": 3, "ready": 3},
        ]

    async def restart(
        self, service: str, namespace: str | None = None, strategy: str = "rolling"
    ) -> dict[str, Any]:
        ns = self._ns(namespace)
        logger.info("k8s.restart", service=service, namespace=ns, live=self.live)
        if self.live:  # pragma: no cover - requires cluster
            return await self._real_restart(service, ns)
        return {
            "action": "restart",
            "service": service,
            "namespace": ns,
            "strategy": strategy,
            "restarted_pods": 4,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    async def scale(
        self,
        service: str,
        namespace: str | None = None,
        replicas: int | None = None,
        replicas_delta: int | None = None,
    ) -> dict[str, Any]:
        ns = self._ns(namespace)
        logger.info("k8s.scale", service=service, namespace=ns, live=self.live)
        if self.live:  # pragma: no cover - requires cluster
            return await self._real_scale(service, ns, replicas, replicas_delta)
        current = 4
        target = replicas if replicas is not None else current + (replicas_delta or 1)
        return {
            "action": "scale",
            "service": service,
            "namespace": ns,
            "from_replicas": current,
            "to_replicas": target,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    async def rollback(
        self, service: str, namespace: str | None = None, to_version: str = "previous"
    ) -> dict[str, Any]:
        ns = self._ns(namespace)
        logger.info("k8s.rollback", service=service, namespace=ns, live=self.live)
        if self.live:  # pragma: no cover - requires cluster
            return await self._real_rollback(service, ns)
        return {
            "action": "rollback",
            "service": service,
            "namespace": ns,
            "to_version": to_version,
            "status": "completed",
            "at": self._now(),
            "mock": True,
        }

    # ----------------------------------------------- live cluster (optional dep)
    def _apps_api(self):  # pragma: no cover - requires cluster
        from kubernetes import client, config

        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()
        return client.AppsV1Api()

    async def _real_get_deployments(self, namespace: str):  # pragma: no cover
        api = self._apps_api()
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
        api = self._apps_api()
        body = {
            "spec": {
                "template": {"metadata": {"annotations": {"incidentiq/restartedAt": self._now()}}}
            }
        }
        api.patch_namespaced_deployment(service, namespace, body)
        return {
            "action": "restart",
            "service": service,
            "namespace": namespace,
            "status": "patched",
            "mock": False,
            "at": self._now(),
        }

    async def _real_scale(self, service, namespace, replicas, replicas_delta):  # pragma: no cover
        api = self._apps_api()
        if replicas is None:
            current = api.read_namespaced_deployment_scale(service, namespace).spec.replicas or 0
            replicas = current + (replicas_delta or 1)
        api.patch_namespaced_deployment_scale(service, namespace, {"spec": {"replicas": replicas}})
        return {
            "action": "scale",
            "service": service,
            "namespace": namespace,
            "to_replicas": replicas,
            "mock": False,
            "at": self._now(),
        }

    async def _real_rollback(self, service: str, namespace: str):  # pragma: no cover
        """Revert the deployment to its previous ReplicaSet revision (rollout undo)."""
        api = self._apps_api()
        dep = api.read_namespaced_deployment(service, namespace)
        current_rev = int(
            (dep.metadata.annotations or {}).get("deployment.kubernetes.io/revision", "0")
        )

        rs_items = api.list_namespaced_replica_set(namespace).items

        def _rev(rs) -> int:
            return int(
                (rs.metadata.annotations or {}).get("deployment.kubernetes.io/revision", "0")
            )

        owned = [
            rs
            for rs in rs_items
            if any(o.uid == dep.metadata.uid for o in (rs.metadata.owner_references or []))
        ]
        candidates = sorted((rs for rs in owned if _rev(rs) < current_rev), key=_rev)
        if not candidates:
            raise RuntimeError(f"No previous revision found for {service} to roll back to")
        target = candidates[-1]

        template = target.spec.template
        if template.metadata and template.metadata.labels:
            template.metadata.labels.pop("pod-template-hash", None)
        api.patch_namespaced_deployment(service, namespace, {"spec": {"template": template}})
        return {
            "action": "rollback",
            "service": service,
            "namespace": namespace,
            "from_revision": current_rev,
            "to_revision": _rev(target),
            "mock": False,
            "at": self._now(),
        }

    async def healthcheck(self) -> dict[str, Any]:
        if self.mock:
            return {
                "name": self.name,
                "mode": "mock",
                "configured": self.enabled,
                "ok": True,
                "detail": "mock mode",
            }
        if not self.enabled:
            return {
                "name": self.name,
                "mode": "live",
                "configured": False,
                "ok": False,
                "detail": "KUBERNETES_ENABLED is false",
            }
        try:  # pragma: no cover - requires cluster
            api = self._apps_api()
            deps = api.list_namespaced_deployment(self.default_namespace)
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": True,
                "detail": f"{len(deps.items)} deployments in {self.default_namespace}",
            }
        except Exception as exc:  # pragma: no cover
            return {
                "name": self.name,
                "mode": "live",
                "configured": True,
                "ok": False,
                "detail": str(exc),
            }
