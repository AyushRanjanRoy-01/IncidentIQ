"""Alert request/response schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AlertSeverity, AlertStatus


class AlertIngest(BaseModel):
    """Inbound alert payload (e.g. from Alertmanager webhook or simulator).

    Field names match ``backend/data/sample_alerts.json``. ``alert_id`` is optional
    and generated when omitted.
    """

    alert_id: str | None = None
    service: str = Field(..., min_length=1, max_length=128)
    severity: AlertSeverity = AlertSeverity.WARNING
    metric: str = Field(..., min_length=1, max_length=128)
    value: float = 0.0
    threshold: float = 0.0
    summary: str | None = Field(default=None, max_length=1000)
    labels: dict[str, Any] = Field(default_factory=dict)
    fired_at: datetime | None = None


class AlertOut(BaseModel):
    """Alert as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    service: str
    severity: str
    metric: str
    value: float
    threshold: float
    summary: str | None = None
    labels: dict[str, Any] = {}
    status: AlertStatus
    fingerprint: str
    fired_at: datetime
    incident_id: str | None = None
    created_at: datetime


class AlertIngestResult(BaseModel):
    """Result of ingesting an alert: the stored alert + correlated incident id."""

    alert: AlertOut
    incident_id: str
    incident_created: bool
