"""Pod restart action."""

from __future__ import annotations

from typing import Any

from app.integrations.kubernetes import KubernetesClient


class RestartAction:
    """Performs a rolling restart of a service's pods."""

    action_type = "restart"

    def __init__(self, k8s: KubernetesClient) -> None:
        self.k8s = k8s

    async def execute(self, target: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return await self.k8s.restart(
            service=target,
            namespace=parameters.get("namespace", "production"),
            strategy=parameters.get("strategy", "rolling"),
        )

    async def verify(self, target: str, parameters: dict[str, Any]) -> bool:
        deployments = await self.k8s.get_deployments(parameters.get("namespace", "production"))
        return any(d["name"] == target and d["ready"] == d["replicas"] for d in deployments)
