"""Terraform integration for infrastructure changes (mock-mode by default)."""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TerraformClient:
    """Run terraform plan/apply (mock-mode simulates a successful apply)."""

    def __init__(self, workdir: str = "infra/terraform", mock: bool | None = None) -> None:
        self.workdir = workdir
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def apply(self, target: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        logger.info("terraform.apply", target=target, mock=self.mock)
        if not self.mock:  # pragma: no cover - requires terraform + cloud creds
            return await self._real_apply(target, variables or {})
        return {
            "action": "terraform_apply",
            "target": target,
            "variables": variables or {},
            "resources_changed": 1,
            "status": "applied",
            "mock": True,
        }

    async def _real_apply(self, target, variables):  # pragma: no cover
        raise NotImplementedError(
            "Real terraform apply requires the python-terraform optional dependency "
            "and configured cloud credentials."
        )
