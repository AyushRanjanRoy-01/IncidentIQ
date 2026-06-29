"""Pod scaling action."""

from __future__ import annotations

from typing import Any

from app.integrations.kubernetes import KubernetesClient


class ScaleAction:
    """Scales a service up or down."""

    action_type = "scale"

    def __init__(self, k8s: KubernetesClient) -> None:
        self.k8s = k8s

    async def execute(self, target: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return await self.k8s.scale(
            service=target,
            namespace=parameters.get("namespace", "production"),
            replicas=parameters.get("replicas"),
            replicas_delta=parameters.get("replicas_delta"),
        )

    async def verify(self, target: str, parameters: dict[str, Any]) -> bool:
        return True
