"""Pytest configuration and fixtures.

Provides shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.
    
    Returns:
        TestClient instance
    """
    return TestClient(app)


@pytest.fixture
async def db_session() -> AsyncGenerator:
    """Create database session for tests.
    
    Yields:
        Database session
    """
    # TODO: Create test database session
    # from app.db.postgres import get_db
    # async with get_db() as session:
    #     yield session
    yield None


@pytest.fixture
async def redis_client() -> AsyncGenerator:
    """Create Redis client for tests.
    
    Yields:
        Redis client
    """
    # TODO: Create test Redis client
    # from app.db.redis import get_redis
    # async with get_redis() as client:
    #     yield client
    yield None


@pytest.fixture
def mock_llm_response() -> dict:
    """Mock LLM API response.
    
    Returns:
        Mock response dictionary
    """
    return {
        "content": "Mock LLM response",
        "tokens_used": 100,
        "model": "gpt-4",
    }


@pytest.fixture
def sample_alert() -> dict:
    """Sample alert data for tests.
    
    Returns:
        Sample alert dictionary
    """
    return {
        "alert_id": "test-alert-001",
        "severity": "critical",
        "service": "checkout-api",
        "metric": "api_latency_p95",
        "value": 2500,
        "threshold": 1000,
    }


@pytest.fixture
def sample_incident() -> dict:
    """Sample incident data for tests.
    
    Returns:
        Sample incident dictionary
    """
    return {
        "incident_id": "test-incident-001",
        "title": "High API Latency",
        "severity": "critical",
        "status": "open",
        "service": "checkout-api",
    }

