"""Rate limiting utilities.

Provides rate limiting functionality to prevent API abuse
and ensure fair resource usage.
"""

from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class RateLimiter:
    """Token bucket rate limiter implementation.
    
    Implements token bucket algorithm for rate limiting.
    Tokens are added at a fixed rate, requests consume tokens.
    """
    
    def __init__(
        self,
        max_requests: int = 100,
        time_window_seconds: int = 60,
    ) -> None:
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        
        # Track requests per key (e.g., IP address, user ID)
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for given key.
        
        Args:
            key: Unique identifier (IP, user ID, etc.)
            
        Returns:
            True if request is allowed, False otherwise
        """
        async with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window_seconds)
            
            # Remove old requests outside time window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            return False
    
    async def get_remaining(self, key: str) -> int:
        """Get remaining requests allowed for key.
        
        Args:
            key: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        async with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window_seconds)
            
            # Remove old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            return max(0, self.max_requests - len(self.requests[key]))
    
    async def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limiter for key or all keys.
        
        Args:
            key: Key to reset, or None to reset all
        """
        async with self._lock:
            if key:
                self.requests.pop(key, None)
            else:
                self.requests.clear()


class SlidingWindowRateLimiter:
    """Sliding window rate limiter.
    
    More accurate than token bucket but uses more memory.
    Tracks exact request timestamps within sliding window.
    """
    
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> None:
        """Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed.
        
        Args:
            key: Unique identifier
            
        Returns:
            True if allowed, False otherwise
        """
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Remove requests outside window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            return False

