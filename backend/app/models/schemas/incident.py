"""Incident request/response schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ActionType, AlertSeverity, IncidentStatus
from app.models.schemas.alert import AlertOut
from app.models.schemas.remediation import RemediationOut


class RecommendedAction(BaseModel):
    """A remediation action recommended by the RCA agent."""

    action_type: ActionType
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    rationale: str | None = None


class IncidentCreate(BaseModel):
    """Manually create an incident from existing alerts."""

    alert_ids: list[str] = Field(default_factory=list)
    title: str | None = None
    service: str | None = None
    incident_type: str = "unknown"
    severity: AlertSeverity = AlertSeverity.WARNING


class IncidentUpdate(BaseModel):
    """Patch an incident's status/resolution."""

    status: IncidentStatus | None = None
    resolution: str | None = Field(default=None, max_length=4000)


class IncidentOut(BaseModel):
    """Incident summary as returned by list/detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    incident_id: str
    title: str
    service: str
    incident_type: str
    severity: str
    status: IncidentStatus
    root_cause: str | None = None
    rca_summary: dict[str, Any] | None = None
    recommended_action: dict[str, Any] | None = None
    confidence: float | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution: str | None = None
    created_at: datetime
    updated_at: datetime


class IncidentDetail(IncidentOut):
    """Incident detail including related alerts and remediations."""

    alerts: list[AlertOut] = Field(default_factory=list)
    remediations: list[RemediationOut] = Field(default_factory=list)
