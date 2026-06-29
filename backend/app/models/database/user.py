"""User database model (authentication + RBAC)."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database.base import TimestampedModel
from app.models.enums import UserRole


class User(TimestampedModel):
    """An authenticated user with an RBAC role.

    Passwords are stored as PBKDF2-HMAC-SHA256 hashes (see ``app.security.auth``);
    the plaintext is never persisted.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, default="", nullable=False)
    email: Mapped[str] = mapped_column(String, default="", nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default=UserRole.VIEWER.value, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<User {self.username} ({self.role})>"
