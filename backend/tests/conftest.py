"""Pytest configuration and shared fixtures.

Test environment is configured *before* importing the app so settings (cached at
import) pick up a file-backed SQLite DB, the mock LLM provider, and JSON logging.
Each test gets a freshly migrated schema, seeded demo users, and an indexed
knowledge base, exercised through an httpx ASGI client.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Configure environment BEFORE importing application modules ---
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_incidentiq.db")
os.environ.setdefault("LOG_JSON", "true")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_PROVIDER", "local")
os.environ.setdefault("INTEGRATIONS_MOCK_MODE", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.db.postgres import AsyncSessionLocal, drop_models, init_models  # noqa: E402
from app.main import app  # noqa: E402
from app.security.auth import seed_default_users  # noqa: E402
from app.services.knowledge_service import KnowledgeService  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest_asyncio.fixture
async def db_session():
    """Fresh schema + seeded users/knowledge; yields a session."""
    await drop_models()
    await init_models()
    async with AsyncSessionLocal() as session:
        await seed_default_users(session)
        await KnowledgeService(session).index_directory(DATA_DIR)
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Async HTTP client bound to the app (schema already prepared)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def operator_headers(client) -> dict[str, str]:
    token = await _token(client, "operator", "operator123")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def viewer_headers(client) -> dict[str, str]:
    token = await _token(client, "viewer", "viewer123")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client) -> dict[str, str]:
    token = await _token(client, "admin", "admin123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_alert() -> dict:
    return {
        "alert_id": "test-alert-001",
        "service": "checkout-api",
        "severity": "critical",
        "metric": "api_latency_p95",
        "value": 2500,
        "threshold": 1000,
        "labels": {"env": "production"},
    }
