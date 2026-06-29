"""Incident database model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database.base import TimestampedModel
from app.models.enums import AlertSeverity, IncidentStatus

if TYPE_CHECKING:
    from app.models.database.alert import Alert
    from app.models.database.remediation_log import RemediationLog


class Incident(TimestampedModel):
    """An incident correlated from one or more alerts, enriched by agent RCA."""

    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    service: Mapped[str] = mapped_column(String, nullable=False, index=True)
    incident_type: Mapped[str] = mapped_column(String, default="unknown", nullable=False)
    severity: Mapped[str] = mapped_column(
        String, default=AlertSeverity.WARNING.value, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String, default=IncidentStatus.OPEN.value, nullable=False, index=True
    )

    # --- Agent RCA output ---
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    rca_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    recommended_action: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Resolution ---
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    alerts: Mapped[list[Alert]] = relationship(
        back_populates="incident", cascade="save-update, merge"
    )
    remediations: Mapped[list[RemediationLog]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Incident {self.incident_id} {self.service} {self.status}>"
