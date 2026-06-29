"""FastAPI application entry point.

Wires together logging, middleware, exception handling, metrics, routes, and a
lifespan that prepares the database, seeds demo users, and indexes the knowledge
base — so a fresh `uvicorn app.main:app` is immediately usable end-to-end.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.api.middleware.auth import AuthContextMiddleware
from app.api.middleware.logging import RequestLoggingMiddleware
from app.api.v1.endpoints import health
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.exceptions import IncidentIQError
from app.db.postgres import AsyncSessionLocal, dispose_engine, init_models
from app.db.redis import cache
from app.observability.logging import configure_logging, get_logger
from app.observability.metrics import MetricsMiddleware
from app.observability.tracing import setup_tracing
from app.security.auth import seed_default_users
from app.security.rate_limit import RateLimitMiddleware
from app.services.knowledge_service import KnowledgeService

configure_logging()
logger = get_logger("app")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


async def _bootstrap() -> None:
    """Prepare DB schema, demo users, and the knowledge base on startup."""
    await init_models()
    await cache.connect()
    async with AsyncSessionLocal() as db:
        try:
            if settings.seed_demo_users:
                await seed_default_users(db)
            ks = KnowledgeService(db)
            if await ks.count() == 0 and DATA_DIR.exists():
                indexed = await ks.index_directory(DATA_DIR)
                await db.commit()
                logger.info("startup.knowledge_indexed", documents=indexed)
        except Exception as exc:  # pragma: no cover - defensive startup
            await db.rollback()
            logger.warning("startup.bootstrap_warning", error=str(exc))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", environment=settings.environment, version=settings.api_version)
    await _bootstrap()
    yield
    await cache.close()
    await dispose_engine()
    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=(
            "AI-powered SRE platform: alert ingestion, multi-agent root-cause "
            "analysis, and human-approved self-healing."
        ),
        lifespan=lifespan,
    )

    # Middleware. Added inner-to-outer; CORS is outermost, request logging next,
    # then auth-context (sets principal) before rate limiting reads it.
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_requests,
        time_window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers -> consistent JSON error envelope.
    @app.exception_handler(IncidentIQError)
    async def _domain_error(request: Request, exc: IncidentIQError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": exc.errors()}},
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
        )

    # Routes.
    app.include_router(health.router)
    app.include_router(api_v1_router)

    @app.get("/", tags=["meta"])
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.api_version,
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    # Prometheus scrape endpoint.
    app.mount("/metrics", make_asgi_app())

    setup_tracing(app)
    return app


app = create_app()
