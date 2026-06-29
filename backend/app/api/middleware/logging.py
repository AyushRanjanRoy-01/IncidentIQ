"""Request logging middleware.

Assigns/propagates an ``X-Request-ID``, binds it (plus the principal) to the
structlog context so all logs in the request are correlated, and emits a single
structured access log with method, path, status, and duration.
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.observability.logging import (
    bind_request_id,
    clear_request_context,
    get_logger,
)

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        request.state.request_id = request_id
        bind_request_id(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "http.request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=elapsed_ms,
            )
            clear_request_context()
            raise
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=elapsed_ms,
            user=getattr(request.state, "username", None),
        )
        response.headers["X-Request-ID"] = request_id
        clear_request_context()
        return response
