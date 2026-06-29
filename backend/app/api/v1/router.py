"""API v1 router configuration.

Combines all endpoint routers into the main v1 router (mounted under /api/v1).
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    alerts,
    auth,
    incidents,
    integrations,
    knowledge,
    metrics,
    remediation,
)

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(alerts.router)
router.include_router(incidents.router)
router.include_router(remediation.router)
router.include_router(knowledge.router)
router.include_router(metrics.router)
router.include_router(integrations.router)
