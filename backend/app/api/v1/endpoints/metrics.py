"""Dashboard statistics endpoints.

Aggregate counts powering the frontend dashboard. (Prometheus scrape metrics are
served separately at ``/metrics`` on the app root.)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.database.alert import Alert
from app.models.database.incident import Incident
from app.models.database.remediation_log import RemediationLog
from app.models.enums import IncidentStatus, RemediationStatus
from app.security.auth import require_viewer

router = APIRouter(tags=["stats"], prefix="/stats")

_OPEN_STATUSES = (
    IncidentStatus.OPEN.value,
    IncidentStatus.ANALYZING.value,
    IncidentStatus.AWAITING_APPROVAL.value,
    IncidentStatus.REMEDIATING.value,
)


@router.get("/summary")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
) -> dict[str, Any]:
    """High-level counts for the dashboard."""
    # Incident counts grouped by status.
    rows = (await db.execute(select(Incident.status, func.count()).group_by(Incident.status))).all()
    by_status = dict(rows)
    incidents_total = sum(by_status.values())
    incidents_open = sum(by_status.get(s, 0) for s in _OPEN_STATUSES)

    alerts_total = int((await db.execute(select(func.count(Alert.alert_id)))).scalar_one())
    rem_total = int(
        (await db.execute(select(func.count(RemediationLog.remediation_id)))).scalar_one()
    )
    rem_succeeded = await _count_status(db, RemediationStatus.SUCCEEDED.value)
    rem_pending = await _count_status(db, RemediationStatus.PENDING_APPROVAL.value)

    return {
        "incidents": {
            "total": incidents_total,
            "open": incidents_open,
            "resolved": by_status.get(IncidentStatus.RESOLVED.value, 0)
            + by_status.get(IncidentStatus.CLOSED.value, 0),
            "by_status": by_status,
        },
        "alerts": {"total": alerts_total},
        "remediations": {
            "total": rem_total,
            "succeeded": rem_succeeded,
            "pending_approval": rem_pending,
        },
    }


async def _count_status(db: AsyncSession, status: str) -> int:
    stmt = select(func.count(RemediationLog.remediation_id)).where(RemediationLog.status == status)
    return int((await db.execute(stmt)).scalar_one())
