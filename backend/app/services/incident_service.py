"""Incident service: creation, retrieval, and agent-driven RCA + auto-remediation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.supervisor import SupervisorAgent
from app.core.config import settings
from app.core.exceptions import IncidentNotFoundError
from app.models.database.alert import Alert
from app.models.database.incident import Incident
from app.models.enums import ActionType, AlertSeverity, IncidentStatus
from app.services.remediation_service import RemediationService

logger = structlog.get_logger(__name__)

_SEVERITY_ORDER = {
    AlertSeverity.CRITICAL.value: 0,
    AlertSeverity.WARNING.value: 1,
    AlertSeverity.INFO.value: 2,
}


def _now() -> datetime:
    return datetime.now(UTC)


def _incident_type_for(metric: str) -> str:
    m = metric.lower()
    if any(t in m for t in ("latency", "error", "5xx", "request")):
        return "performance"
    if any(t in m for t in ("memory", "oom", "cpu", "disk", "heap")):
        return "resource"
    return "unknown"


class IncidentService:
    """Manages incidents and orchestrates their analysis."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ---------------------------------------------------------------- creation
    async def create_from_alerts(
        self,
        alerts: list[Alert],
        *,
        title: str | None = None,
        incident_type: str | None = None,
        severity: str | None = None,
    ) -> Incident:
        if not alerts:
            raise ValueError("Cannot create an incident without alerts")
        primary = sorted(alerts, key=lambda a: _SEVERITY_ORDER.get(a.severity, 9))[0]
        sev = severity or primary.severity
        inc_type = incident_type or _incident_type_for(primary.metric)
        inc_title = title or f"{sev.title()} {primary.metric} on {primary.service}"

        incident = Incident(
            incident_id=f"inc-{uuid.uuid4().hex[:12]}",
            title=inc_title,
            service=primary.service,
            incident_type=inc_type,
            severity=sev,
            status=IncidentStatus.OPEN.value,
        )
        self.db.add(incident)
        for alert in alerts:
            alert.incident_id = incident.incident_id
        await self.db.flush()
        logger.info("incident.created", incident_id=incident.incident_id, service=incident.service)
        return incident

    # ---------------------------------------------------------------- retrieval
    async def get(self, incident_id: str) -> Incident:
        incident = await self.db.get(Incident, incident_id)
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        return incident

    async def get_detail(self, incident_id: str) -> Incident:
        stmt = (
            select(Incident)
            .where(Incident.incident_id == incident_id)
            .options(selectinload(Incident.alerts), selectinload(Incident.remediations))
        )
        incident = (await self.db.execute(stmt)).scalar_one_or_none()
        if incident is None:
            raise IncidentNotFoundError(incident_id)
        return incident

    async def list(
        self, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Incident]:
        stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit).offset(offset)
        if status:
            stmt = stmt.where(Incident.status == status)
        return list((await self.db.execute(stmt)).scalars().all())

    async def find_active_for_service(self, service: str) -> Incident | None:
        active = (
            IncidentStatus.OPEN.value,
            IncidentStatus.ANALYZING.value,
            IncidentStatus.AWAITING_APPROVAL.value,
            IncidentStatus.REMEDIATING.value,
        )
        stmt = (
            select(Incident)
            .where(Incident.service == service, Incident.status.in_(active))
            .order_by(Incident.created_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def alerts_for(self, incident_id: str) -> list[Alert]:
        stmt = select(Alert).where(Alert.incident_id == incident_id)
        return list((await self.db.execute(stmt)).scalars().all())

    # ----------------------------------------------------------------- updates
    async def update(
        self,
        incident_id: str,
        *,
        status: str | None = None,
        resolution: str | None = None,
        resolved_by: str | None = None,
    ) -> Incident:
        incident = await self.get(incident_id)
        if status is not None:
            incident.status = status
            if status in (IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value):
                incident.resolved_at = _now()
                incident.resolved_by = resolved_by
        if resolution is not None:
            incident.resolution = resolution
        await self.db.flush()
        return incident

    # ---------------------------------------------------------------- analysis
    async def analyze(self, incident_id: str) -> Incident:
        """Run the multi-agent RCA and (optionally) auto-propose a remediation."""
        incident = await self.get(incident_id)
        alerts = await self.alerts_for(incident_id)

        incident.status = IncidentStatus.ANALYZING.value
        await self.db.flush()

        supervisor = SupervisorAgent(self.db)
        result = await supervisor.run(incident, alerts)

        action = result.get("recommended_action") or {}
        confidence = float(result.get("confidence") or 0.0)
        incident.root_cause = result.get("root_cause")
        incident.rca_summary = result
        incident.recommended_action = action
        incident.confidence = confidence

        should_propose = (
            confidence >= settings.rca_auto_propose_threshold
            and action.get("action_type")
            and action["action_type"] != ActionType.NOOP.value
        )
        if should_propose:
            rem_service = RemediationService(self.db)
            await rem_service.propose(
                incident_id=incident.incident_id,
                action_type=action["action_type"],
                target=action.get("target", incident.service),
                parameters=action.get("parameters", {}),
                rationale=action.get("rationale"),
                confidence=confidence,
                proposed_by="rca-agent",
                requires_approval=True,
            )
            incident.status = IncidentStatus.AWAITING_APPROVAL.value
        else:
            incident.status = IncidentStatus.OPEN.value
        await self.db.flush()
        logger.info(
            "incident.analyzed",
            incident_id=incident_id,
            confidence=confidence,
            proposed=should_propose,
        )
        return incident

    async def count(self, status: str | None = None) -> int:
        stmt = select(func.count(Incident.incident_id))
        if status:
            stmt = stmt.where(Incident.status == status)
        return int((await self.db.execute(stmt)).scalar_one())
