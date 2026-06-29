"""Alert endpoints: ingestion and queries."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.schemas.alert import AlertIngest, AlertIngestResult, AlertOut
from app.observability import metrics
from app.security.auth import require_operator, require_viewer
from app.services.alert_service import AlertService

router = APIRouter(tags=["alerts"], prefix="/alerts")


@router.post("/ingest", response_model=AlertIngestResult, status_code=201)
async def ingest_alert(
    payload: AlertIngest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_operator),
) -> AlertIngestResult:
    """Ingest an alert, correlate it to an incident, and run multi-agent RCA.

    Requires the ``operator`` role (alert sources authenticate as operators).
    """
    service = AlertService(db)
    alert, incident_id, created = await service.ingest(payload)
    metrics.record_alert_ingested(alert.severity, alert.service)
    if created:
        metrics.record_incident_created(alert.service)
    return AlertIngestResult(
        alert=AlertOut.model_validate(alert),
        incident_id=incident_id,
        incident_created=created,
    )


@router.get("/", response_model=list[AlertOut])
async def list_alerts(
    service: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> list[AlertOut]:
    alerts = await AlertService(db).list(service=service, limit=limit, offset=offset)
    return [AlertOut.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> AlertOut:
    alert = await AlertService(db).get(alert_id)
    return AlertOut.model_validate(alert)
