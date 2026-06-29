"""Remediation request/response schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ActionType, RemediationStatus


class RemediationCreate(BaseModel):
    """Manually propose a remediation for an incident."""

    action_type: ActionType
    target: str = Field(..., min_length=1, max_length=256)
    parameters: dict[str, Any] = Field(default_factory=dict)
    rationale: str | None = Field(default=None, max_length=2000)
    requires_approval: bool = True


class RemediationOut(BaseModel):
    """Remediation action with full audit trail."""

    model_config = ConfigDict(from_attributes=True)

    remediation_id: str
    incident_id: str
    action_type: str
    target: str
    parameters: dict[str, Any] = {}
    status: RemediationStatus
    confidence: float | None = None
    rationale: str | None = None
    requires_approval: bool
    proposed_by: str
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejected_by: str | None = None
    rejection_reason: str | None = None
    result: dict[str, Any] | None = None
    executed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
