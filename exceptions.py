"""Janus Clew Exceptions - Custom exception hierarchy."""


class JanusException(Exception):
    """Base exception for all Janus errors."""

    def __init__(self, message: str, code: str = "unknown_error", **context):
        """Initialize exception with message and context.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            **context: Additional context (repo_name, etc.)
        """
        self.message = message
        self.code = code
        self.context = context
        super().__init__(message)

    def __str__(self):
        return self.message


# ============================================================================
# CLI EXCEPTIONS
# ============================================================================


class CLIException(JanusException):
    """Base CLI exception."""

    pass


class NoRepositoriesError(CLIException):
    """Raised when no repositories provided."""

    def __init__(self):
        super().__init__(
            "No repositories provided. Usage: janus-clew analyze <repo1> <repo2> ...",
            code="no_repositories",
        )


class RepositoryNotFoundError(CLIException):
    """Raised when repository doesn't exist."""

    def __init__(self, repo_path: str):
        super().__init__(
            f"Repository not found: {repo_path}",
            code="repo_not_found",
            repo_path=repo_path,
        )


class AnalysisError(CLIException):
    """Raised when analysis fails."""

    def __init__(self, repo_name: str, error: str):
        super().__init__(
            f"Analysis failed for {repo_name}: {error}",
            code="analysis_error",
            repo_name=repo_name,
            error=error,
        )


# ============================================================================
# GIT EXCEPTIONS
# ============================================================================


class GitException(JanusException):
    """Base Git exception."""

    pass


class GitParseError(GitException):
    """Raised when Git parsing fails."""

    def __init__(self, repo_path: str, error: str):
        super().__init__(
            f"Git error in {repo_path}: {error}",
            code="git_parse_error",
            repo_path=repo_path,
            error=error,
        )


class InvalidRepositoryError(GitException):
    """Raised when repository is invalid."""

    def __init__(self, repo_path: str):
        super().__init__(
            f"Invalid Git repository: {repo_path}",
            code="invalid_repository",
            repo_path=repo_path,
        )


# ============================================================================
# AWS Q EXCEPTIONS
# ============================================================================


class AWSQException(JanusException):
    """Base AWS Q exception."""

    pass


class AWSQTimeoutError(AWSQException):
    """Raised when AWS Q request times out."""

    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"Amazon Q request timed out after {timeout_seconds}s",
            code="aws_q_timeout",
            timeout=timeout_seconds,
        )


class AWSQRetryError(AWSQException):
    """Raised when AWS Q retries are exhausted."""

    def __init__(self, attempts: int, last_error: str):
        super().__init__(
            f"Amazon Q failed after {attempts} attempts: {last_error}",
            code="aws_q_retry_exhausted",
            attempts=attempts,
            last_error=last_error,
        )


class AWSQNotAvailableError(AWSQException):
    """Raised when AWS Q CLI is not available."""

    def __init__(self):
        super().__init__(
            "Amazon Q CLI not found. Install with: pip install amazon-q",
            code="aws_q_not_available",
        )


# ============================================================================
# STORAGE EXCEPTIONS
# ============================================================================


class StorageException(JanusException):
    """Base storage exception."""

    pass


class StorageWriteError(StorageException):
    """Raised when storage write fails."""

    def __init__(self, path: str, error: str):
        super().__init__(
            f"Failed to write to {path}: {error}",
            code="storage_write_error",
            path=path,
            error=error,
        )


class StorageReadError(StorageException):
    """Raised when storage read fails."""

    def __init__(self, path: str, error: str):
        super().__init__(
            f"Failed to read from {path}: {error}",
            code="storage_read_error",
            path=path,
            error=error,
        )


# ============================================================================
# CONFIG EXCEPTIONS
# ============================================================================


class ConfigError(JanusException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, key: str = ""):
        super().__init__(
            f"Configuration error: {message}",
            code="config_error",
            key=key,
        )


# ============================================================================
# API EXCEPTIONS
# ============================================================================


class APIException(JanusException):
    """Base API exception."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, code="api_error")
        self.status_code = status_code


class NotFoundError(APIException):
    """Raised when resource not found."""

    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=404)


class ValidationError(APIException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}", status_code=400)
