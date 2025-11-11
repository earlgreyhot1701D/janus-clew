"""Timeout handling and retry logic with decorators.

Provides decorators for warning on slow operations and retrying with exponential backoff.
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, TypeVar, Any


logger = logging.getLogger(__name__)

T = TypeVar('T')


class TimeoutError(Exception):
    """Custom timeout error for retry logic."""
    pass


def warn_if_slow(timeout_seconds: int = 60) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that warns if function takes too long.

    ✅ GUARDRAIL: Monitors long-running operations

    Usage:
        @warn_if_slow(timeout_seconds=30)
        def my_function():
            pass

    Args:
        timeout_seconds: Warning threshold in seconds (default: 60)

    Returns:
        Decorator function

    Example:
        @warn_if_slow(timeout_seconds=5)
        def slow_task():
            time.sleep(10)
            return "done"
        slow_task()  # Logs warning after 5s, returns 'done'
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ {func.__name__} failed: {e}")
                raise

            elapsed = time.time() - start
            if elapsed > timeout_seconds:
                logger.warning(
                    f"⏱️  {func.__name__} took {elapsed:.1f}s (warning threshold: {timeout_seconds}s)"
                )
            return result
        return wrapper
    return decorator


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries function with exponential backoff.

    ✅ GUARDRAIL: Handles transient failures gracefully

    Usage:
        @retry_with_backoff(max_retries=3, base_delay=0.5)
        def flaky_function():
            pass

    Args:
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)

    Returns:
        Decorator function

    Example:
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def flaky():
            # Fails twice, succeeds on third attempt
            return "success"
        flaky()  # Returns 'success' after retries
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    if attempt < max_retries - 1:  # Don't sleep on last attempt
                        # Exponential backoff + random jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                        logger.warning(
                            f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"❌ Final attempt failed: {e}")

            # All retries exhausted
            raise TimeoutError(
                f"All {max_retries} retries failed for {func.__name__}: {last_error}"
            )
        return wrapper
    return decorator
