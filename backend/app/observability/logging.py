"""Structured logging configuration (structlog).

JSON logs by default (``LOG_JSON=true``) for machine ingestion; switch to a
human-friendly console renderer for local dev. A per-request ``request_id`` is
bound via contextvars so every log line in a request is correlated.
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.core.config import settings

_CONFIGURED = False


def configure_logging() -> None:
    """Configure structlog + stdlib logging. Idempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer(colors=False)
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logging (uvicorn, sqlalchemy) through a basic handler.
    logging.basicConfig(
        format="%(message)s", level=level, handlers=[logging.StreamHandler(sys.stdout)]
    )
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def bind_request_id(request_id: str) -> None:
    structlog.contextvars.bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
    structlog.contextvars.clear_contextvars()
