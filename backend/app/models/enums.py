"""Shared domain enums.

Stored as plain strings in the database (portable across SQLite/PostgreSQL) and
reused by the Pydantic schemas so the API and persistence layers agree on values.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String-valued enum that serialises to its value."""

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


class AlertSeverity(StrEnum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(StrEnum):
    FIRING = "firing"
    RESOLVED = "resolved"


class IncidentStatus(StrEnum):
    OPEN = "open"
    ANALYZING = "analyzing"
    AWAITING_APPROVAL = "awaiting_approval"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RemediationStatus(StrEnum):
    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionType(StrEnum):
    """Self-healing actions the platform can propose/execute."""

    RESTART = "restart"
    SCALE = "scale"
    ROLLBACK = "rollback"
    TERRAFORM_APPLY = "terraform_apply"
    NOOP = "noop"


class UserRole(StrEnum):
    """RBAC roles, ordered from least to most privileged."""

    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


# Role privilege ordering for hierarchical checks (admin >= operator >= viewer).
ROLE_RANK: dict[str, int] = {
    UserRole.VIEWER.value: 0,
    UserRole.OPERATOR.value: 1,
    UserRole.ADMIN.value: 2,
}


def role_satisfies(user_role: str, required_role: str) -> bool:
    """Return True if ``user_role`` is at least as privileged as ``required_role``."""
    return ROLE_RANK.get(user_role, -1) >= ROLE_RANK.get(required_role, 999)
