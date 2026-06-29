"""Tests for rate limiting."""

import pytest

from app.utils.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests():
    """Test rate limiter allows requests within limit."""
    limiter = RateLimiter(max_requests=10, time_window_seconds=60)

    for _ in range(10):
        allowed = await limiter.is_allowed("test-key")
        assert allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_blocks_excess():
    """Test rate limiter blocks requests exceeding limit."""
    limiter = RateLimiter(max_requests=5, time_window_seconds=60)

    # Allow 5 requests
    for _ in range(5):
        await limiter.is_allowed("test-key")

    # 6th request should be blocked
    allowed = await limiter.is_allowed("test-key")
    assert allowed is False


@pytest.mark.asyncio
async def test_rate_limiter_remaining():
    """Test rate limiter remaining count."""
    limiter = RateLimiter(max_requests=10, time_window_seconds=60)

    await limiter.is_allowed("test-key")
    remaining = await limiter.get_remaining("test-key")
    assert remaining == 9
