import logging
import time
from functools import wraps
import random


logger = logging.getLogger(__name__)


class TimeoutError(Exception):
    pass


def warn_if_slow(func, timeout_seconds=60):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ {func.__name__} failed: {e}")
            raise

        elapsed = time.time() - start
        if elapsed > timeout_seconds:
            logger.warning(f"⏱️  {func.__name__} took {elapsed:.1f}s (timeout was {timeout_seconds}s)")
        return result
    return wrapper


def retry_with_backoff(func, max_retries=3, base_delay=1):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                logger.warning(f"⚠️ Retry {attempt + 1}/{max_retries} after error: {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
        raise TimeoutError(f"❌ All {max_retries} retries failed for {func.__name__}")
    return wrapper
