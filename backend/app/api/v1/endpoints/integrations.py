"""Integration connection-status endpoint (admin).

Powers the onboarding "connect & verify" experience: returns per-integration
mode (mock/live), whether it's configured, and a live reachability/auth check.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.integrations.hub import get_integration_hub
from app.security.auth import require_admin

router = APIRouter(tags=["integrations"], prefix="/integrations")


@router.get("/status")
async def integrations_status(_=Depends(require_admin)) -> dict[str, Any]:
    """Validate every configured integration and report green/red status."""
    return await get_integration_hub().status()
