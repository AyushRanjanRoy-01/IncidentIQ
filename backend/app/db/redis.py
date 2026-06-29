"""Cache abstraction with Redis backend and in-process fallback.

When ``settings.redis_url`` is configured and reachable, a real Redis client is
used. Otherwise (the default for local/test) the client transparently degrades to
an in-process TTL cache so the rest of the application is agnostic to deployment.
"""

from __future__ import annotations

import json
import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class CacheClient:
    """Async cache client: Redis when available, in-process dict otherwise."""

    def __init__(self, redis_url: str = "") -> None:
        self.redis_url = redis_url
        self._redis: Any | None = None
        self._local: dict[str, tuple[float, str]] = {}
        self._use_redis = False

    async def connect(self) -> None:
        """Attempt to connect to Redis; fall back to local cache on failure."""
        if not self.redis_url:
            logger.info("cache.local", reason="no redis_url configured")
            return
        try:
            import redis.asyncio as aioredis  # lazy import; optional dependency

            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            self._use_redis = True
            logger.info("cache.redis_connected", url=self.redis_url)
        except Exception as exc:  # pragma: no cover - depends on environment
            self._redis = None
            self._use_redis = False
            logger.warning("cache.redis_unavailable", error=str(exc), fallback="in-process")

    async def get(self, key: str) -> Any | None:
        if self._use_redis and self._redis is not None:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw is not None else None
        entry = self._local.get(key)
        if entry is None:
            return None
        expires_at, raw = entry
        if expires_at and expires_at < time.time():
            self._local.pop(key, None)
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        raw = json.dumps(value, default=str)
        if self._use_redis and self._redis is not None:
            await self._redis.set(key, raw, ex=ttl)
            return
        self._local[key] = (time.time() + ttl if ttl else 0.0, raw)

    async def delete(self, key: str) -> None:
        if self._use_redis and self._redis is not None:
            await self._redis.delete(key)
            return
        self._local.pop(key, None)

    async def publish(self, channel: str, message: str) -> None:
        """Publish a message (no-op for the in-process fallback)."""
        if self._use_redis and self._redis is not None:
            await self._redis.publish(channel, message)
        else:
            logger.debug("cache.publish_noop", channel=channel)

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
        self._use_redis = False


# Backwards-compatible alias for the original scaffold name.
RedisClient = CacheClient

# Module-level singleton (connected during app startup).
cache = CacheClient()
