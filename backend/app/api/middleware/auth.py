"""Authentication context middleware.

Best-effort extraction of the authenticated principal from the bearer token onto
``request.state`` (``username`` / ``role``). This is NON-enforcing — it only
enriches logging and rate-limiting context. Endpoint authorization is enforced by
the ``get_current_user`` / ``require_role`` dependencies in ``app.security.auth``.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.security.auth import decode_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Populate request.state.username/role from a valid bearer token, if present."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request.state.username = None
        request.state.role = None
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
            try:
                payload = decode_token(token)
                request.state.username = payload.get("sub")
                request.state.role = payload.get("role")
            except Exception:
                # Invalid/expired token: leave context empty; dependencies will 401.
                pass
        return await call_next(request)
