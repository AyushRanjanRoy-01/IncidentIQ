"""Rate limiting middleware for FastAPI.

Provides rate limiting middleware to protect API endpoints
from abuse and ensure fair resource usage.
"""

from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.utils.rate_limiter import RateLimiter


class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI.
    
    Applies rate limiting to API requests based on client IP
    or authenticated user ID.
    """
    
    def __init__(
        self,
        max_requests: int = 100,
        time_window_seconds: int = 60,
    ) -> None:
        """Initialize rate limit middleware.
        
        Args:
            max_requests: Maximum requests per time window
            time_window_seconds: Time window in seconds
        """
        self.rate_limiter = RateLimiter(
            max_requests=max_requests,
            time_window_seconds=time_window_seconds,
        )
    
    def _get_client_key(self, request: Request) -> str:
        """Get client identifier for rate limiting.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client identifier (IP address or user ID)
        """
        # Try to get authenticated user ID first
        # TODO: Extract from JWT token if available
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable,
    ) -> JSONResponse:
        """Process request with rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint handler
            
        Returns:
            Response from next handler
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        client_key = self._get_client_key(request)
        
        if not await self.rate_limiter.is_allowed(client_key):
            remaining = await self.rate_limiter.get_remaining(client_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": self.rate_limiter.time_window_seconds,
                    "remaining": remaining,
                },
                headers={
                    "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "Retry-After": str(self.rate_limiter.time_window_seconds),
                },
            )
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = await self.rate_limiter.get_remaining(client_key)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


def create_rate_limit_middleware(
    max_requests: int = 100,
    time_window_seconds: int = 60,
) -> RateLimitMiddleware:
    """Create rate limit middleware instance.
    
    Args:
        max_requests: Maximum requests per window
        time_window_seconds: Time window in seconds
        
    Returns:
        Rate limit middleware instance
    """
    return RateLimitMiddleware(
        max_requests=max_requests,
        time_window_seconds=time_window_seconds,
    )

