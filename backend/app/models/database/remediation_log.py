"""Remediation log database model.

Captures the full lifecycle of a self-healing action: proposed by the agents,
gated by human approval (HITL), executed via an adapter, and optionally rolled back.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database.base import TimestampedModel
from app.models.enums import RemediationStatus

if TYPE_CHECKING:
    from app.models.database.incident import Incident


class RemediationLog(TimestampedModel):
    """A proposed/executed remediation action with audit trail."""

    __tablename__ = "remediation_logs"

    remediation_id: Mapped[str] = mapped_column(String, primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.incident_id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    target: Mapped[str] = mapped_column(String, nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(
        String, default=RemediationStatus.PROPOSED.value, nullable=False, index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(default=True, nullable=False)

    # --- Audit: who proposed / approved / rejected ---
    proposed_by: Mapped[str] = mapped_column(String, default="rca-agent", nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_by: Mapped[str | None] = mapped_column(String, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Execution result ---
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    incident: Mapped[Incident] = relationship(back_populates="remediations")

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<RemediationLog {self.remediation_id} {self.action_type} {self.status}>"
