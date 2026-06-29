"""Authentication endpoints: login + current-user."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.db.postgres import get_db
from app.models.database.user import User
from app.models.schemas.auth import CurrentUser, LoginRequest, Token, UserOut
from app.security.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(creds: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    """Exchange username/password for a JWT access token.

    Demo users (local/dev): ``admin/admin123``, ``operator/operator123``,
    ``viewer/viewer123``.
    """
    user = await authenticate_user(db, creds.username, creds.password)
    if user is None:
        raise AuthenticationError("Invalid username or password")
    token, expires_in = create_access_token(user.username, user.role)
    return Token(
        access_token=token,
        expires_in=expires_in,
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=UserOut)
async def read_me(
    current: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> User:
    user = await db.get(User, current.username)
    assert user is not None  # guaranteed by get_current_user
    return user
