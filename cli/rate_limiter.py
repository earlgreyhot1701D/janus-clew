"""Rate limiting for external API calls.

Implements token-bucket-style rate limiting with call tracking and usage metrics.
"""

import time
import logging
from collections import deque
from typing import Dict, Any


logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with token tracking and usage metrics.

    ✅ GUARDRAIL: Prevents hammering external APIs (AWS Q, Bedrock, etc.)
    """

    def __init__(self, max_calls_per_minute: int = 3):
        """Initialize rate limiter.

        Args:
            max_calls_per_minute: Maximum API calls allowed per minute (default: 3)
        """
        self.max_calls = max_calls_per_minute
        self.call_times = deque(maxlen=max_calls_per_minute)
        self.total_tokens = 0
        self.total_calls = 0

    def wait_if_needed(self) -> None:
        """Wait if rate limit reached, otherwise allow call to proceed.

        Blocks execution if max_calls_per_minute exceeded.
        """
        now = time.time()
        while self.call_times and (now - self.call_times[0] > 60):
            self.call_times.popleft()

        if len(self.call_times) >= self.max_calls:
            wait_time = 60 - (now - self.call_times[0])
            logger.warning(f"⏳ Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            self.call_times.clear()

        self.call_times.append(time.time())
        self.total_calls += 1

    def record_tokens(self, token_count: int) -> None:
        """Record token usage for tracking.

        Args:
            token_count: Number of tokens consumed by API call
        """
        self.total_tokens += token_count

    def summary(self) -> Dict[str, Any]:
        """Get usage summary statistics.

        Returns:
            Dictionary with call count, token usage, and rate limit

        Example:
            limiter = RateLimiter(max_calls_per_minute=3)
            limiter.wait_if_needed()
            limiter.record_tokens(100)
            limiter.summary()  # Returns {'total_calls': 1, 'total_tokens': 100, ...}
        """
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "max_calls_per_minute": self.max_calls,
        }
