"""Rate limiting middleware for FastAPI.

A lightweight, dependency-free sliding-window limiter (see
``app.utils.rate_limiter.RateLimiter``) applied per client (authenticated user
when available, otherwise client IP). Health/metrics/docs paths are exempt so
probes and dashboards are never throttled.

For multi-replica production deployments swap the in-process limiter for a
Redis-backed one (e.g. ``slowapi`` from requirements-optional.txt).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.utils.rate_limiter import RateLimiter

_EXEMPT_PREFIXES = ("/health", "/metrics", "/docs", "/redoc", "/openapi.json")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Throttle requests per client using a sliding window."""

    def __init__(self, app, max_requests: int = 120, time_window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limiter = RateLimiter(
            max_requests=max_requests, time_window_seconds=time_window_seconds
        )

    @staticmethod
    def _client_key(request: Request) -> str:
        user = getattr(request.state, "username", None)
        if user:
            return f"user:{user}"
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path.startswith(_EXEMPT_PREFIXES):
            return await call_next(request)

        key = self._client_key(request)
        if not await self.limiter.is_allowed(key):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Rate limit exceeded. Slow down.",
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(self.limiter.time_window_seconds),
                },
            )

        response = await call_next(request)
        remaining = await self.limiter.get_remaining(key)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
