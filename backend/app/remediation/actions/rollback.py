"""Deployment rollback action."""

from __future__ import annotations

from typing import Any

from app.integrations.kubernetes import KubernetesClient


class RollbackAction:
    """Rolls a service back to a previous known-good version."""

    action_type = "rollback"

    def __init__(self, k8s: KubernetesClient) -> None:
        self.k8s = k8s

    async def execute(self, target: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return await self.k8s.rollback(
            service=target,
            namespace=parameters.get("namespace", "production"),
            to_version=parameters.get("to_version", "previous"),
        )

    async def verify(self, target: str, parameters: dict[str, Any]) -> bool:
        return True
