"""Authentication schemas (Pydantic v2)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=256)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str = ""
    email: str = ""
    role: str
    disabled: bool = False


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=256)
    full_name: str = ""
    email: str = ""
    role: UserRole = UserRole.VIEWER


class CurrentUser(BaseModel):
    """Lightweight authenticated principal resolved from a JWT."""

    username: str
    role: str
    disabled: bool = False
