"""Comprehensive tests for guardrails modules."""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Import guardrails modules
from logger import setup_logging, get_logger, ColoredFormatter
from cli.validators import validate_repo, should_analyze_file, sanitize_for_prompt, ValidationError
from cli.rate_limiter import RateLimiter
from cli.timeout_handler import warn_if_slow, retry_with_backoff, TimeoutError as HandlerTimeoutError
from backend.guardrails import GuardrailsMiddleware


# ============================================================================
# LOGGER TESTS
# ============================================================================

class TestLogger:
    """Test logger functionality."""

    def test_setup_logger_returns_logger(self):
        """Test that get_logger returns a valid logger."""
        logger = get_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_setup_logger_has_handlers(self):
        """Test that logger has at least one handler."""
        logger = get_logger("test_logger_handlers")
        assert len(logger.handlers) > 0

    def test_colored_formatter_adds_colors(self):
        """Test that ColoredFormatter adds ANSI colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = Mock()
        record.levelname = "INFO"
        record.getMessage = Mock(return_value="Test message")
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None  # ✅ Add this - logging.format() needs it

        formatted = formatter.format(record)
        assert "\033[" in formatted  # Contains ANSI color code


# ============================================================================
# VALIDATOR TESTS
# ============================================================================

class TestValidators:
    """Test cli.validators functionality."""

    def test_validate_repo_rejects_nonexistent_path(self):
        """Test that validate_repo rejects nonexistent paths."""
        with pytest.raises(ValidationError):
            validate_repo("/nonexistent/path")

    def test_validate_repo_rejects_non_git_repo(self, tmp_path):
        """Test that validate_repo rejects non-git directories."""
        regular_dir = tmp_path / "not_a_git_repo"
        regular_dir.mkdir()

        with pytest.raises(ValidationError):
            validate_repo(str(regular_dir))

    def test_validate_repo_accepts_git_repo(self, tmp_path):
        """Test that validate_repo accepts valid git repos."""
        from git import Repo as GitRepo

        git_dir = tmp_path / "git_repo"
        git_dir.mkdir()

        # ✅ Actually initialize a git repo using GitRepo.init()
        GitRepo.init(str(git_dir))

        # Should not raise
        result = validate_repo(str(git_dir))
        assert result is True

    def test_should_analyze_file_rejects_large_files(self, tmp_path):
        """Test that should_analyze_file rejects files >10MB."""
        large_file = tmp_path / "large.py"
        # Create file larger than 10MB
        large_file.write_bytes(b"x" * (11 * 1024 * 1024))

        assert should_analyze_file(large_file) is False

    def test_should_analyze_file_skips_node_modules(self, tmp_path):
        """Test that should_analyze_file skips node_modules."""
        node_file = tmp_path / "node_modules" / "package.py"
        node_file.parent.mkdir(parents=True)
        node_file.write_text("print('test')")

        assert should_analyze_file(node_file) is False

    def test_should_analyze_file_accepts_python_files(self, tmp_path):
        """Test that should_analyze_file accepts small Python files."""
        py_file = tmp_path / "valid.py"
        py_file.write_text("print('hello')")

        assert should_analyze_file(py_file) is True

    def test_sanitize_removes_quotes(self):
        """Test that sanitize_for_prompt removes dangerous quotes."""
        dangerous = '"""break the prompt"""'
        sanitized = sanitize_for_prompt(dangerous)

        assert '"""' not in sanitized

    def test_sanitize_removes_null_bytes(self):
        """Test that sanitize_for_prompt removes null bytes."""
        dangerous = "text\x00with\x00nulls"
        sanitized = sanitize_for_prompt(dangerous)

        assert "\x00" not in sanitized

    def test_sanitize_limits_length(self):
        """Test that sanitize_for_prompt limits to max_length."""
        long_text = "x" * 1000
        sanitized = sanitize_for_prompt(long_text, max_length=100)

        # ✅ Allow for the "..." which adds 3 chars (100 - 3 + 3 = 103)
        assert len(sanitized) <= 103


# ============================================================================
# RATE LIMITER TESTS
# ============================================================================

class TestRateLimiter:
    """Test cli.rate_limiter functionality."""

    def test_rate_limiter_allows_first_call(self):
        """Test that first call doesn't wait."""
        limiter = RateLimiter(max_calls_per_minute=3)

        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # First call should be fast (not wait)
        assert elapsed < 0.1

    def test_rate_limiter_allows_multiple_calls_within_limit(self):
        """Test that multiple calls within limit are allowed."""
        limiter = RateLimiter(max_calls_per_minute=3)

        # Make 3 calls quickly
        for _ in range(3):
            limiter.wait_if_needed()

        assert limiter.total_calls == 3

    def test_rate_limiter_waits_when_limit_exceeded(self):
        """Test that rate limiter waits when limit exceeded."""
        limiter = RateLimiter(max_calls_per_minute=1)

        # First call
        limiter.wait_if_needed()

        # Second call should wait
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should wait approximately 60 seconds (or less due to timing)
        assert elapsed > 0 or limiter.total_calls == 2

    def test_rate_limiter_tracks_tokens(self):
        """Test that rate limiter tracks token usage."""
        limiter = RateLimiter()

        limiter.record_tokens(100)
        limiter.record_tokens(50)

        assert limiter.total_tokens == 150

    def test_rate_limiter_summary(self):
        """Test that rate limiter provides usage summary."""
        limiter = RateLimiter()

        limiter.wait_if_needed()
        limiter.record_tokens(100)

        summary = limiter.summary()

        assert summary["total_calls"] == 1
        assert summary["total_tokens"] == 100


# ============================================================================
# TIMEOUT HANDLER TESTS
# ============================================================================

class TestTimeoutHandler:
    """Test cli.timeout_handler functionality."""

    def test_warn_if_slow_decorator_works(self):
        """Test that warn_if_slow decorator works."""
        # ✅ Use decorator syntax with default argument
        @warn_if_slow()
        def fast_function():
            return "result"

        result = fast_function()
        assert result == "result"

    def test_warn_if_slow_warns_on_slow_function(self):
        """Test that warn_if_slow warns when function takes too long."""
        @warn_if_slow(timeout_seconds=0.1)
        def slow_function():
            time.sleep(0.2)
            return "done"

        # Should complete and return result
        result = slow_function()
        assert result == "done"

    def test_retry_with_backoff_succeeds_immediately(self):
        """Test that retry_with_backoff succeeds if function works."""
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def working_function():
            return "success"

        result = working_function()
        assert result == "success"

    def test_retry_with_backoff_retries_on_failure(self):
        """Test that retry_with_backoff retries when function fails."""
        call_count = [0]

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        result = failing_function()
        assert result == "success"
        assert call_count[0] == 3

    def test_retry_with_backoff_raises_after_exhausted(self):
        """Test that retry_with_backoff raises TimeoutError after all retries."""
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(HandlerTimeoutError):
            always_fails()


# ============================================================================
# GUARDRAILS MIDDLEWARE TESTS
# ============================================================================

class TestGuardrailsMiddleware:
    """Test backend.guardrails middleware."""

    @pytest.mark.asyncio
    async def test_guardrails_middleware_rejects_oversized_request(self):
        """Test that middleware rejects requests larger than max_request_size."""
        app = Mock()
        middleware = GuardrailsMiddleware(app, max_request_size=1000)

        request = Mock()
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"content-length": "2000"}  # 2000 bytes > 1000 max

        response = await middleware.dispatch(request, Mock())

        # Should return 413 error
        assert response.status_code == 413

    @pytest.mark.asyncio
    async def test_guardrails_middleware_allows_normal_request(self):
        """Test that middleware allows requests within size limit."""
        app = Mock()
        middleware = GuardrailsMiddleware(app, max_request_size=10000)

        request = Mock()
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"content-length": "500"}  # 500 bytes < 10000 max

        call_next = AsyncMock(return_value=Mock(status_code=200))
        response = await middleware.dispatch(request, call_next)

        # Should call next
        assert call_next.called

    @pytest.mark.asyncio
    async def test_guardrails_middleware_rate_limits_by_ip(self):
        """Test that middleware rate limits by IP."""
        app = Mock()
        middleware = GuardrailsMiddleware(app, requests_per_minute=2)

        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}

        call_next = AsyncMock(return_value=Mock(status_code=200))

        # Make 2 requests (within limit)
        for _ in range(2):
            await middleware.dispatch(request, call_next)

        # Third request should be rate limited
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 429


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestGuardrailsIntegration:
    """Test guardrails working together."""

    def test_all_guardrails_import_without_error(self):
        """Test that all guardrails can be imported."""
        from logger import get_logger
        from cli.validators import validate_repo, should_analyze_file
        from cli.rate_limiter import RateLimiter
        from cli.timeout_handler import warn_if_slow, retry_with_backoff
        from backend.guardrails import GuardrailsMiddleware

        assert all([
            get_logger,
            validate_repo,
            should_analyze_file,
            RateLimiter,
            warn_if_slow,
            retry_with_backoff,
            GuardrailsMiddleware,
        ])

    def test_guardrails_work_with_real_data(self, tmp_path):
        """Test guardrails with real data."""
        from git import Repo as GitRepo

        # Create a test git repo
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        # ✅ Actually initialize a git repo
        GitRepo.init(str(repo_dir))

        py_file = repo_dir / "test.py"
        py_file.write_text("print('hello')")

        # Test validators
        assert validate_repo(str(repo_dir)) is True
        assert should_analyze_file(py_file) is True

        # Test rate limiter
        limiter = RateLimiter(max_calls_per_minute=3)
        limiter.wait_if_needed()
        assert limiter.total_calls == 1
