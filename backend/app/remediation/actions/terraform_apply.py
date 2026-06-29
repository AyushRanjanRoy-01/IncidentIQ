"""Terraform apply action for infrastructure changes."""

from __future__ import annotations

from typing import Any

from app.integrations.terraform import TerraformClient


class TerraformApplyAction:
    """Applies an infrastructure change via Terraform."""

    action_type = "terraform_apply"

    def __init__(self, terraform: TerraformClient) -> None:
        self.terraform = terraform

    async def execute(self, target: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return await self.terraform.apply(target=target, variables=parameters)

    async def verify(self, target: str, parameters: dict[str, Any]) -> bool:
        return True
