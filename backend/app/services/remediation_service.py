"""Remediation service: propose, approve (execute), and reject remediations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, RemediationNotFoundError
from app.models.database.incident import Incident
from app.models.database.remediation_log import RemediationLog
from app.models.enums import IncidentStatus, RemediationStatus
from app.remediation.approval_flow import ApprovalFlow
from app.remediation.executor import RemediationExecutor

logger = structlog.get_logger(__name__)

_DECIDABLE = {RemediationStatus.PENDING_APPROVAL.value, RemediationStatus.PROPOSED.value}


def _now() -> datetime:
    return datetime.now(UTC)


class RemediationService:
    """Manages the remediation lifecycle and its execution."""

    def __init__(
        self,
        db: AsyncSession,
        executor: RemediationExecutor | None = None,
        approval: ApprovalFlow | None = None,
    ) -> None:
        self.db = db
        self.executor = executor or RemediationExecutor()
        self.approval = approval or ApprovalFlow()

    async def propose(
        self,
        *,
        incident_id: str,
        action_type: str,
        target: str,
        parameters: dict[str, Any] | None = None,
        rationale: str | None = None,
        confidence: float | None = None,
        proposed_by: str = "rca-agent",
        requires_approval: bool = True,
    ) -> RemediationLog:
        status = (
            RemediationStatus.PENDING_APPROVAL.value
            if requires_approval
            else RemediationStatus.APPROVED.value
        )
        rem = RemediationLog(
            remediation_id=f"rem-{uuid.uuid4().hex[:12]}",
            incident_id=incident_id,
            action_type=action_type,
            target=target,
            parameters=parameters or {},
            status=status,
            confidence=confidence,
            rationale=rationale,
            requires_approval=requires_approval,
            proposed_by=proposed_by,
        )
        self.db.add(rem)
        await self.db.flush()
        if requires_approval:
            await self.approval.request_approval(rem, confidence or 0.0)
        logger.info("remediation.proposed", remediation_id=rem.remediation_id, action=action_type)
        return rem

    async def get(self, remediation_id: str) -> RemediationLog:
        rem = await self.db.get(RemediationLog, remediation_id)
        if rem is None:
            raise RemediationNotFoundError(remediation_id)
        return rem

    async def list(
        self, incident_id: str | None = None, status: str | None = None
    ) -> list[RemediationLog]:
        stmt = select(RemediationLog).order_by(RemediationLog.created_at.desc())
        if incident_id:
            stmt = stmt.where(RemediationLog.incident_id == incident_id)
        if status:
            stmt = stmt.where(RemediationLog.status == status)
        return list((await self.db.execute(stmt)).scalars().all())

    async def approve(self, remediation_id: str, actor: str) -> RemediationLog:
        rem = await self.get(remediation_id)
        if rem.status not in _DECIDABLE:
            raise ConflictError(
                f"Remediation {remediation_id} is '{rem.status}' and cannot be approved"
            )
        rem.approved_by = actor
        rem.approved_at = _now()
        rem.status = RemediationStatus.EXECUTING.value
        await self.db.flush()

        result = await self.executor.execute(rem.action_type, rem.target, rem.parameters)
        rem.result = result
        rem.executed_at = _now()
        rem.status = (
            RemediationStatus.SUCCEEDED.value
            if result.get("success")
            else RemediationStatus.FAILED.value
        )

        incident = await self.db.get(Incident, rem.incident_id)
        if incident is not None:
            incident.status = (
                IncidentStatus.REMEDIATING.value
                if result.get("success")
                else IncidentStatus.AWAITING_APPROVAL.value
            )
        await self.db.flush()
        await self.approval.notify_decision(rem, approved=True, actor=actor)
        logger.info(
            "remediation.approved",
            remediation_id=remediation_id,
            actor=actor,
            success=result.get("success"),
        )
        return rem

    async def reject(self, remediation_id: str, actor: str, reason: str) -> RemediationLog:
        rem = await self.get(remediation_id)
        if rem.status not in _DECIDABLE:
            raise ConflictError(
                f"Remediation {remediation_id} is '{rem.status}' and cannot be rejected"
            )
        rem.rejected_by = actor
        rem.rejection_reason = reason
        rem.status = RemediationStatus.REJECTED.value
        await self.db.flush()
        await self.approval.notify_decision(rem, approved=False, actor=actor)
        logger.info("remediation.rejected", remediation_id=remediation_id, actor=actor)
        return rem
