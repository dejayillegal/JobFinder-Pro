
"""
Async rate limiter for API requests.
"""
import asyncio
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AsyncRateLimiter:
    """Token bucket rate limiter for async operations."""
    
    def __init__(self, rate: float = 2.0, burst: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            rate: Requests per second
            burst: Maximum burst size (defaults to rate * 2)
        """
        self.rate = rate
        self.interval = 1.0 / rate
        self.burst = burst or int(rate * 2)
        self.tokens = self.burst
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # Wait for next token
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
            self.last_update = time.monotonic()
