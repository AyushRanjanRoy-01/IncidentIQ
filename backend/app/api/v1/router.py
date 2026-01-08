"""API v1 router configuration.

Combines all endpoint routers into the main v1 router.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# TODO: Include endpoint routers
# from .endpoints import alerts, incidents, metrics, remediation, health
