"""Human-in-the-loop approval schemas (Pydantic v2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ApproveRequest(BaseModel):
    """Approve a pending remediation (optional note for the audit trail)."""

    note: str | None = Field(default=None, max_length=1000)


class RejectRequest(BaseModel):
    """Reject a pending remediation with a reason."""

    reason: str = Field(..., min_length=1, max_length=1000)
