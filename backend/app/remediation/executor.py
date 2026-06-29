"""Remediation action execution engine.

Dispatches a validated remediation action to the appropriate handler (which wraps
a Kubernetes/Terraform client). All execution is auditable and, in the default
mock mode, fully simulated — so the self-healing flow is safe to demo end-to-end.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.integrations.hub import IntegrationHub, get_integration_hub
from app.models.enums import ActionType
from app.remediation.actions.restart import RestartAction
from app.remediation.actions.rollback import RollbackAction
from app.remediation.actions.scale import ScaleAction
from app.remediation.actions.terraform_apply import TerraformApplyAction

logger = structlog.get_logger(__name__)


class RemediationExecutor:
    """Executes remediation actions via per-action handlers."""

    def __init__(self, hub: IntegrationHub | None = None) -> None:
        self.hub = hub or get_integration_hub()
        self._handlers = {
            ActionType.RESTART.value: RestartAction(self.hub.kubernetes),
            ActionType.SCALE.value: ScaleAction(self.hub.kubernetes),
            ActionType.ROLLBACK.value: RollbackAction(self.hub.kubernetes),
            ActionType.TERRAFORM_APPLY.value: TerraformApplyAction(self.hub.terraform),
        }

    async def execute(
        self, action_type: str, target: str, parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute an action; returns ``{success, detail|error, verified?}``."""
        parameters = parameters or {}
        if action_type == ActionType.NOOP.value:
            return {"success": True, "detail": {"action": "noop", "status": "skipped"}}

        handler = self._handlers.get(action_type)
        if handler is None:
            logger.warning("remediation.unknown_action", action_type=action_type)
            return {"success": False, "error": f"Unknown action type: {action_type}"}

        try:
            detail = await handler.execute(target, parameters)
            verified = await handler.verify(target, parameters)
            logger.info(
                "remediation.executed", action_type=action_type, target=target, verified=verified
            )
            return {"success": True, "detail": detail, "verified": verified}
        except Exception as exc:
            logger.exception("remediation.failed", action_type=action_type, target=target)
            return {"success": False, "error": str(exc)}
