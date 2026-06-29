"""Authentication & authorization.

- Password hashing with PBKDF2-HMAC-SHA256 (Python stdlib — no native build deps).
- Stateless JWT access tokens (PyJWT).
- DB-backed ``get_current_user`` dependency and hierarchical ``require_role`` RBAC.

Demo users are seeded on startup in local/dev (see ``seed_default_users``).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import structlog
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.postgres import get_db
from app.models.database.user import User
from app.models.enums import UserRole, role_satisfies
from app.models.schemas.auth import CurrentUser

logger = structlog.get_logger(__name__)

_PBKDF2_ROUNDS = 240_000
bearer_scheme = HTTPBearer(auto_error=False)


# --------------------------------------------------------------------- passwords
def hash_password(password: str) -> str:
    """Return a ``pbkdf2_sha256$rounds$salt$hash`` encoded password hash."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)
    return "pbkdf2_sha256${}${}${}".format(
        _PBKDF2_ROUNDS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verification of a password against a stored hash."""
    try:
        algo, rounds_s, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds_s))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# -------------------------------------------------------------------------- JWT
def create_access_token(
    username: str, role: str, expires_minutes: int | None = None
) -> tuple[str, int]:
    """Create a signed JWT. Returns ``(token, expires_in_seconds)``."""
    minutes = expires_minutes or settings.jwt_access_token_expire_minutes
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=minutes)
    payload: dict[str, Any] = {"sub": username, "role": role, "iat": now, "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, minutes * 60


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, raising ``AuthenticationError`` on failure."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid authentication token") from exc


# ------------------------------------------------------------------- user lookup
async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """Return the user if credentials are valid and the account is enabled."""
    user = await db.get(User, username)
    if user is None or user.disabled:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Resolve the authenticated principal from the bearer token (DB-backed)."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated")
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    if not username:
        raise AuthenticationError("Invalid token subject")
    user = await db.get(User, username)
    if user is None or user.disabled:
        raise AuthenticationError("User no longer active")
    return CurrentUser(username=user.username, role=user.role, disabled=user.disabled)


def require_role(min_role: UserRole):
    """Dependency factory enforcing a minimum RBAC role (admin>=operator>=viewer)."""

    async def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not role_satisfies(user.role, min_role.value):
            raise AuthorizationError(
                f"Requires role '{min_role.value}' or higher (you are '{user.role}')"
            )
        return user

    return _checker


# Convenience dependencies for common access levels.
require_viewer = require_role(UserRole.VIEWER)
require_operator = require_role(UserRole.OPERATOR)
require_admin = require_role(UserRole.ADMIN)


# --------------------------------------------------------------------- bootstrap
DEFAULT_USERS = [
    ("admin", "admin123", "Platform Admin", UserRole.ADMIN),
    ("operator", "operator123", "On-call Operator", UserRole.OPERATOR),
    ("viewer", "viewer123", "Read-only Viewer", UserRole.VIEWER),
]


async def seed_default_users(db: AsyncSession) -> int:
    """Create demo users if they don't exist. Returns the number created.

    Intended for local/dev only (gated by ``settings.seed_demo_users``).
    """
    existing = {row[0] for row in (await db.execute(select(User.username))).all()}
    created = 0
    for username, password, full_name, role in DEFAULT_USERS:
        if username in existing:
            continue
        db.add(
            User(
                username=username,
                full_name=full_name,
                email=f"{username}@incidentiq.local",
                hashed_password=hash_password(password),
                role=role.value,
            )
        )
        created += 1
    if created:
        await db.commit()
        logger.info("auth.seeded_demo_users", count=created)
    return created
