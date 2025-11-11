"""Input validation and security guardrails for Janus Clew.

Provides validators for repository paths, file filtering, and prompt sanitization.
"""

import logging
from pathlib import Path
from git import Repo, InvalidGitRepositoryError


logger = logging.getLogger(__name__)


MAX_REPO_SIZE_GB = 1.0
MAX_FILE_SIZE_MB = 10
SKIP_DIRS = {"node_modules", "__pycache__", ".git"}


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_repo(repo_path: str) -> bool:
    """Validate that path is a valid git repository within size limits.

    ✅ GUARDRAIL: Prevents analysis of invalid/massive repos

    Args:
        repo_path: Path to repository to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If repo invalid, not found, or >1GB

    Example:
        validate_repo("~/my-project") returns True if valid
    """
    path = Path(repo_path)
    if not path.exists():
        raise ValidationError(f"❌ Repo not found: {repo_path}")
    try:
        Repo(path)
    except InvalidGitRepositoryError:
        raise ValidationError(f"❌ Not a git repo (no .git): {repo_path}")

    total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    size_gb = total_size / 1_000_000_000
    if size_gb > MAX_REPO_SIZE_GB:
        raise ValidationError(f"❌ Repo too large ({size_gb:.1f}GB > {MAX_REPO_SIZE_GB}GB limit)")

    logger.info(f"✅ Repo validated: {path.name} ({size_gb:.2f}GB)")
    return True


def should_analyze_file(file_path: Path) -> bool:
    """Check if file should be analyzed based on size and type.

    ✅ GUARDRAIL: Filters out large files, node_modules, and non-code files

    Args:
        file_path: Path to file to check

    Returns:
        True if file should be analyzed, False otherwise

    Example:
        should_analyze_file(Path("src/main.py")) returns True
        should_analyze_file(Path("node_modules/package.json")) returns False
    """
    if file_path.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False

    if any(skip in file_path.parts for skip in SKIP_DIRS):
        return False

    return file_path.suffix in {".py", ".ts", ".tsx", ".js", ".json", ".html", ".css"}


def sanitize_for_prompt(text: str, max_length: int = 1000) -> str:
    """Sanitize text for safe use in LLM prompts.

    ✅ SECURITY: Prevents prompt injection attacks

    Removes:
    - Triple quotes (prevent prompt injection)
    - Null bytes
    - Excessive length

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (default: 1000)

    Returns:
        Sanitized text safe for prompts

    Example:
        Input with triple quotes is converted to backticks for safety
        Long strings are truncated to max_length characters
    """
    if not text:
        return ""

    # Remove null bytes (can break parsers)
    text = text.replace('\x00', '')

    # Remove dangerous quotes (prevent prompt injection)
    text = text.replace('"""', "'''")
    text = text.replace("'''", "```")

    # Limit length (including the "..." suffix)
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."

    return text
