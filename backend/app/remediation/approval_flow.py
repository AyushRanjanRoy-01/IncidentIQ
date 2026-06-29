"""Human-in-the-loop approval workflow notifications.

The authoritative approval *state* lives on the ``RemediationLog`` row (managed by
``RemediationService``). This module handles the surrounding ChatOps/paging
notifications so on-call engineers are looped in when a fix needs approval or a
decision is made.
"""

from __future__ import annotations

import structlog

from app.integrations.hub import IntegrationHub, get_integration_hub
from app.models.database.remediation_log import RemediationLog

logger = structlog.get_logger(__name__)


class ApprovalFlow:
    """Sends notifications for the approval lifecycle."""

    def __init__(self, hub: IntegrationHub | None = None) -> None:
        self.hub = hub or get_integration_hub()

    async def request_approval(self, remediation: RemediationLog, confidence: float) -> None:
        await self.hub.notify(
            f"[ACTION NEEDED] Remediation {remediation.remediation_id} "
            f"({remediation.action_type} -> {remediation.target}) needs approval for "
            f"incident {remediation.incident_id} (confidence={confidence}).",
            severity="critical" if confidence >= 0.8 else "warning",
        )

    async def notify_decision(
        self, remediation: RemediationLog, approved: bool, actor: str
    ) -> None:
        verb = "approved" if approved else "rejected"
        await self.hub.notify(
            f"Remediation *{remediation.remediation_id}* {verb} by {actor} "
            f"(incident {remediation.incident_id}).",
            severity="warning",
        )
