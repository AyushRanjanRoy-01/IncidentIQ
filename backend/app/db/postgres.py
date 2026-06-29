"""Async database engine, session factory, and FastAPI dependency.

Works transparently with SQLite (default, zero-config local/test) and PostgreSQL
(staging/production) via the async SQLAlchemy 2.0 engine. The module name is kept
as ``postgres`` for backwards compatibility with the original scaffold.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Import models package so every table is registered on Base.metadata.
import app.models.database  # noqa: F401
from app.core.config import settings
from app.models.database.base import Base


def _build_engine() -> AsyncEngine:
    kwargs: dict = {"echo": settings.database_echo, "future": True}
    if settings.is_sqlite:
        # SQLite needs check_same_thread disabled for async usage. NullPool avoids
        # reusing connections across event loops (important for per-test loops).
        from sqlalchemy.pool import NullPool

        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = NullPool
    else:
        kwargs["pool_size"] = settings.database_pool_size
        kwargs["max_overflow"] = 20
        kwargs["pool_pre_ping"] = True
    return create_async_engine(settings.database_url, **kwargs)


engine: AsyncEngine = _build_engine()

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a transactional session.

    Commits on success, rolls back on exception, always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_models() -> None:
    """Create all tables (used for local/SQLite and tests; prod uses Alembic)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_models() -> None:
    """Drop all tables (test teardown helper)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def dispose_engine() -> None:
    """Dispose the engine and its connection pool (shutdown)."""
    await engine.dispose()
