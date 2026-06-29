"""Tests for authentication and authorization primitives."""

import pytest

from app.core.exceptions import AuthenticationError
from app.models.enums import UserRole, role_satisfies
from app.security.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret-pass")
    assert hashed != "s3cret-pass"
    assert verify_password("s3cret-pass", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_password_hashes_are_salted():
    assert hash_password("same") != hash_password("same")


def test_jwt_roundtrip():
    token, expires_in = create_access_token("alice", UserRole.OPERATOR.value)
    assert expires_in > 0
    payload = decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["role"] == UserRole.OPERATOR.value


def test_invalid_token_raises():
    with pytest.raises(AuthenticationError):
        decode_token("not-a-real-token")


def test_role_hierarchy():
    assert role_satisfies(UserRole.ADMIN.value, UserRole.OPERATOR.value)
    assert role_satisfies(UserRole.OPERATOR.value, UserRole.VIEWER.value)
    assert not role_satisfies(UserRole.VIEWER.value, UserRole.OPERATOR.value)
