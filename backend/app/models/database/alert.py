"""Alert database model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database.base import TimestampedModel, utcnow
from app.models.enums import AlertSeverity, AlertStatus

if TYPE_CHECKING:
    from app.models.database.incident import Incident


class Alert(TimestampedModel):
    """A single monitoring alert ingested from Prometheus/Alertmanager etc."""

    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String, primary_key=True)
    service: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String, default=AlertSeverity.WARNING.value, nullable=False, index=True
    )
    metric: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    labels: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    # Stable dedup key derived from service+metric+labels.
    fingerprint: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String, default=AlertStatus.FIRING.value, nullable=False, index=True
    )
    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    incident_id: Mapped[str | None] = mapped_column(
        ForeignKey("incidents.incident_id", ondelete="SET NULL"), nullable=True, index=True
    )
    incident: Mapped[Incident | None] = relationship(back_populates="alerts")

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Alert {self.alert_id} {self.service}/{self.metric} {self.severity}>"
