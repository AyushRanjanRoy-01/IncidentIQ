"""Incident endpoints: list, detail, update, and (re)analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.enums import IncidentStatus
from app.models.schemas.auth import CurrentUser
from app.models.schemas.incident import IncidentDetail, IncidentOut, IncidentUpdate
from app.models.schemas.remediation import RemediationOut
from app.security.auth import require_operator, require_viewer
from app.services.incident_service import IncidentService

router = APIRouter(tags=["incidents"], prefix="/incidents")


@router.get("/", response_model=list[IncidentOut])
async def list_incidents(
    status: IncidentStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[IncidentOut]:
    incidents = await IncidentService(db).list(
        status=status.value if status else None, limit=limit, offset=offset
    )
    return [IncidentOut.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> IncidentDetail:
    incident = await IncidentService(db).get_detail(incident_id)
    return IncidentDetail.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_operator),
) -> IncidentOut:
    incident = await IncidentService(db).update(
        incident_id,
        status=payload.status.value if payload.status else None,
        resolution=payload.resolution,
        resolved_by=user.username,
    )
    return IncidentOut.model_validate(incident)


@router.post("/{incident_id}/analyze", response_model=IncidentOut)
async def analyze_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_operator),
) -> IncidentOut:
    """Re-run the multi-agent RCA pipeline for an incident."""
    incident = await IncidentService(db).analyze(incident_id)
    return IncidentOut.model_validate(incident)


@router.get("/{incident_id}/remediations", response_model=list[RemediationOut])
async def incident_remediations(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[RemediationOut]:
    incident = await IncidentService(db).get_detail(incident_id)
    return [RemediationOut.model_validate(r) for r in incident.remediations]
