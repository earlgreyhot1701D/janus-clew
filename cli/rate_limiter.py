import time
import logging
from collections import deque


logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_calls_per_minute: int = 3):
        self.max_calls = max_calls_per_minute
        self.call_times = deque(maxlen=max_calls_per_minute)
        self.total_tokens = 0
        self.total_calls = 0

    def wait_if_needed(self):
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

    def record_tokens(self, token_count: int):
        self.total_tokens += token_count
