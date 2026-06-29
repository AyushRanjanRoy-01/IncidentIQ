"""Health check endpoints (mounted at the app root, not under /api/v1)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.postgres import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Liveness probe — process is up."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.api_version,
        "environment": settings.environment,
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Readiness probe — dependencies (database) are reachable."""
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "ready" if db_ok else "degraded",
        "checks": {"database": "ok" if db_ok else "error"},
    }
