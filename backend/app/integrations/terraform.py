"""Terraform integration for infrastructure changes.

Mock mode simulates a successful apply. Live mode shells out to the ``terraform``
CLI (init + apply -auto-approve) in the target working directory. Live apply is
powerful and irreversible — keep it behind the human approval gate.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TerraformClient:
    name = "terraform"

    def __init__(self, workdir: str = "infra/terraform", mock: bool | None = None) -> None:
        self.workdir = workdir
        self.mock = settings.integrations_mock_mode if mock is None else mock

    async def apply(self, target: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        variables = variables or {}
        logger.info("terraform.apply", target=target, mock=self.mock)
        if not self.mock:
            return await self._real_apply(target, variables)
        return {
            "action": "terraform_apply",
            "target": target,
            "variables": variables,
            "resources_changed": 1,
            "status": "applied",
            "mock": True,
        }

    async def _real_apply(
        self, target: str, variables: dict[str, Any]
    ) -> dict[str, Any]:  # pragma: no cover
        if shutil.which("terraform") is None:
            raise RuntimeError("terraform CLI not found on PATH")
        cwd = str(Path(self.workdir) / target) if target else self.workdir
        var_args: list[str] = []
        for key, value in variables.items():
            var_args += ["-var", f"{key}={value}"]

        async def _run(*cmd: str) -> tuple[int, str]:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await proc.communicate()
            return proc.returncode or 0, out.decode(errors="replace")

        rc, init_out = await _run("terraform", "init", "-input=false", "-no-color")
        if rc != 0:
            raise RuntimeError(f"terraform init failed: {init_out[-500:]}")
        rc, apply_out = await _run(
            "terraform", "apply", "-auto-approve", "-input=false", "-no-color", *var_args
        )
        status = "applied" if rc == 0 else "failed"
        return {
            "action": "terraform_apply",
            "target": target,
            "variables": variables,
            "status": status,
            "mock": False,
            "output_tail": apply_out[-1000:],
        }

    async def healthcheck(self) -> dict[str, Any]:
        if self.mock:
            return {
                "name": self.name,
                "mode": "mock",
                "configured": True,
                "ok": True,
                "detail": "mock mode",
            }
        present = shutil.which("terraform") is not None
        wd = Path(self.workdir).exists()
        return {
            "name": self.name,
            "mode": "live",
            "configured": present,
            "ok": present and wd,
            "detail": ("terraform CLI ready" if present else "terraform CLI not on PATH")
            + ("" if wd else f"; workdir '{self.workdir}' missing"),
        }
