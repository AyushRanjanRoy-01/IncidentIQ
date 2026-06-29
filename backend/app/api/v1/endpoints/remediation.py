"""Remediation endpoints: list, propose, approve (HITL), reject."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.enums import RemediationStatus
from app.models.schemas.approval import ApproveRequest, RejectRequest
from app.models.schemas.auth import CurrentUser
from app.models.schemas.remediation import RemediationCreate, RemediationOut
from app.observability import metrics
from app.security.auth import require_operator, require_viewer
from app.services.remediation_service import RemediationService

router = APIRouter(tags=["remediation"], prefix="/remediation")


@router.get("/", response_model=list[RemediationOut])
async def list_remediations(
    incident_id: str | None = Query(default=None),
    status: RemediationStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[RemediationOut]:
    rems = await RemediationService(db).list(
        incident_id=incident_id, status=status.value if status else None
    )
    return [RemediationOut.model_validate(r) for r in rems]


@router.get("/{remediation_id}", response_model=RemediationOut)
async def get_remediation(
    remediation_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> RemediationOut:
    rem = await RemediationService(db).get(remediation_id)
    return RemediationOut.model_validate(rem)


@router.post("/incidents/{incident_id}/propose", response_model=RemediationOut, status_code=201)
async def propose_remediation(
    incident_id: str,
    payload: RemediationCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_operator),
) -> RemediationOut:
    """Manually propose a remediation for an incident (operator+)."""
    rem = await RemediationService(db).propose(
        incident_id=incident_id,
        action_type=payload.action_type.value,
        target=payload.target,
        parameters=payload.parameters,
        rationale=payload.rationale,
        proposed_by=user.username,
        requires_approval=payload.requires_approval,
    )
    return RemediationOut.model_validate(rem)


@router.post("/{remediation_id}/approve", response_model=RemediationOut)
async def approve_remediation(
    remediation_id: str,
    payload: ApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_operator),
) -> RemediationOut:
    """Approve and execute a pending remediation (human-in-the-loop, operator+)."""
    rem = await RemediationService(db).approve(remediation_id, actor=user.username)
    metrics.record_remediation(rem.action_type, rem.status)
    return RemediationOut.model_validate(rem)


@router.post("/{remediation_id}/reject", response_model=RemediationOut)
async def reject_remediation(
    remediation_id: str,
    payload: RejectRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_operator),
) -> RemediationOut:
    """Reject a pending remediation (operator+)."""
    rem = await RemediationService(db).reject(
        remediation_id, actor=user.username, reason=payload.reason
    )
    metrics.record_remediation(rem.action_type, rem.status)
    return RemediationOut.model_validate(rem)
