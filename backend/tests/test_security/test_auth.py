"""Tests for authentication and authorization."""

import pytest
from app.security.auth import AuthService, RBAC


def test_auth_service_initialization():
    """Test auth service initialization."""
    auth_service = AuthService()
    assert auth_service is not None


def test_create_access_token():
    """Test JWT token creation."""
    auth_service = AuthService(secret_key="test-secret-key")
    token = auth_service.create_access_token(
        subject="test-user",
        roles=["admin"],
    )
    assert token is not None
    assert isinstance(token, str)


def test_decode_token():
    """Test JWT token decoding."""
    auth_service = AuthService(secret_key="test-secret-key")
    token = auth_service.create_access_token(
        subject="test-user",
        roles=["admin"],
    )
    payload = auth_service.decode_token(token)
    assert payload["sub"] == "test-user"
    assert "admin" in payload["roles"]


def test_invalid_token():
    """Test invalid token handling."""
    auth_service = AuthService(secret_key="test-secret-key")
    
    with pytest.raises(Exception):  # TODO: Use specific exception
        auth_service.decode_token("invalid-token")

