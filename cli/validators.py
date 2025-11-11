import logging
from pathlib import Path
from git import Repo, InvalidGitRepositoryError


logger = logging.getLogger(__name__)


MAX_REPO_SIZE_GB = 1.0
MAX_FILE_SIZE_MB = 10
SKIP_DIRS = {"node_modules", "__pycache__", ".git"}


class ValidationError(Exception):
    pass


def validate_repo(repo_path: str) -> bool:
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
    if file_path.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False

    if any(skip in file_path.parts for skip in SKIP_DIRS):
        return False

    return file_path.suffix in {".py", ".ts", ".tsx", ".js", ".json", ".html", ".css"}
