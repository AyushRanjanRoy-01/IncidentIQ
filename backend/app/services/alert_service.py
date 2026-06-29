"""Alert service: ingestion, dedup fingerprinting, correlation, and analysis trigger."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlertNotFoundError
from app.models.database.alert import Alert
from app.models.schemas.alert import AlertIngest
from app.services.incident_service import IncidentService

logger = structlog.get_logger(__name__)


def _now() -> datetime:
    return datetime.now(UTC)


def fingerprint(service: str, metric: str, labels: dict) -> str:
    """Stable dedup key from service + metric + the environment label."""
    env = (labels or {}).get("env", "unknown")
    raw = f"{service}|{metric}|{env}".lower()
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


class AlertService:
    """Handles inbound alerts and links them to incidents."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.incidents = IncidentService(db)

    async def ingest(self, payload: AlertIngest) -> tuple[Alert, str, bool]:
        """Ingest an alert; correlate to (or create) an incident and analyse it.

        Returns ``(alert, incident_id, incident_created)``.
        """
        alert_id = payload.alert_id or f"alert-{uuid.uuid4().hex[:12]}"
        fp = fingerprint(payload.service, payload.metric, payload.labels)

        alert = await self.db.get(Alert, alert_id)
        if alert is None:
            alert = Alert(alert_id=alert_id, fingerprint=fp)
            self.db.add(alert)
        # Upsert fields from the payload.
        alert.service = payload.service
        alert.severity = payload.severity.value
        alert.metric = payload.metric
        alert.value = payload.value
        alert.threshold = payload.threshold
        alert.summary = payload.summary
        alert.labels = payload.labels
        alert.fingerprint = fp
        alert.fired_at = payload.fired_at or _now()
        await self.db.flush()

        # Correlate: attach to an active incident for the service, else create one.
        incident = await self.incidents.find_active_for_service(payload.service)
        created = False
        if incident is None:
            incident = await self.incidents.create_from_alerts([alert])
            created = True
        else:
            alert.incident_id = incident.incident_id
            await self.db.flush()

        # Run the multi-agent analysis (deterministic + fast in mock mode).
        await self.incidents.analyze(incident.incident_id)
        await self.db.refresh(alert)
        logger.info(
            "alert.ingested",
            alert_id=alert_id,
            incident_id=incident.incident_id,
            created=created,
        )
        return alert, incident.incident_id, created

    async def get(self, alert_id: str) -> Alert:
        alert = await self.db.get(Alert, alert_id)
        if alert is None:
            raise AlertNotFoundError(alert_id)
        return alert

    async def list(
        self, service: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Alert]:
        stmt = select(Alert).order_by(Alert.fired_at.desc()).limit(limit).offset(offset)
        if service:
            stmt = stmt.where(Alert.service == service)
        return list((await self.db.execute(stmt)).scalars().all())
