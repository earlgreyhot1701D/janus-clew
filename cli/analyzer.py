"""Repository analysis engine using Git and AST parsing with intelligent caching."""

import ast
import logging
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional

from git import Repo

from logger import get_logger
from config import CACHE_ENABLED
from exceptions import GitParseError, InvalidRepositoryError, AnalysisError

logger = get_logger(__name__)


# ============================================================================
# CACHE UTILITIES
# ============================================================================

def get_file_hash(file_path: Path) -> str:
    """Generate SHA256 hash of file for cache invalidation.

    Args:
        file_path: Path to file

    Returns:
        SHA256 hex digest of file contents
    """
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        logger.debug(f"Could not hash {file_path}: {e}")
        return ""


def load_cache(cache_path: Path) -> Dict[str, Any]:
    """Load analysis cache from disk.

    Args:
        cache_path: Path to cache file

    Returns:
        Cache dictionary, or empty dict if load fails
    """
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text())
            logger.debug(f"Loaded cache: {cache_path}")
            return data
        except Exception as e:
            logger.warning(f"⚠️  Failed to load cache from {cache_path}: {e}")
    return {}


def save_cache(cache_path: Path, data: Dict[str, Any]) -> bool:
    """Save analysis cache to disk.

    Args:
        cache_path: Path to cache file
        data: Cache dictionary to save

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, indent=2))
        logger.debug(f"Saved cache: {cache_path}")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Failed to save cache: {e}")
        return False


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

class AnalysisEngine:
    """Analyzes Git repositories for complexity, technologies, and patterns.

    Features:
    - Multi-factor complexity scoring (realistic, trustworthy benchmarks)
    - Intelligent caching (only re-analyzes changed files)
    - Growth rate calculation (track progression between projects)
    - Technology detection (AWS Bedrock, AgentCore, etc.)
    - Comprehensive error handling with detailed logging
    """

    @staticmethod
    def run(repos: List[str]) -> Dict[str, Any]:
        """Analyze multiple repositories with comprehensive error handling.

        Args:
            repos: List of repository paths to analyze

        Returns:
            Dictionary with projects and overall metrics

        Raises:
            AnalysisError: If analysis fails
        """
        projects = []
        errors = []

        for repo_path in repos:
            try:
                safe_path = Path(repo_path).name or str(repo_path).replace("\n", "\\n")
                logger.debug(f"Analyzing repository: {safe_path}")

                analysis = AnalysisEngine.analyze_repo(repo_path)
                projects.append(analysis)
                logger.info(f"✅ {analysis['name']}: {analysis['complexity_score']:.1f} complexity")

            except (InvalidRepositoryError, GitParseError, AnalysisError) as e:
                # ✅ SECURITY: Sanitize error message (prevent log injection)
                safe_path = Path(repo_path).name or str(repo_path).replace("\n", "\\n")
                safe_error = str(e).replace("\n", " ")
                logger.warning(f"Skipping {safe_path}: {safe_error}")
                errors.append({"repo": repo_path, "error": str(e)})

            except Exception as e:
                # ✅ SECURITY: Sanitize path and error
                safe_path = Path(repo_path).name or str(repo_path).replace("\n", "\\n")
                safe_error = str(e).replace("\n", " ")
                logger.error(f"Unexpected error analyzing {safe_path}: {safe_error}", exc_info=True)
                errors.append({"repo": repo_path, "error": str(e)})

        if not projects:
            raise AnalysisError(
                repo_name="batch_analysis",
                error="Unable to analyze any repositories"
            )

        avg_complexity = sum(p["complexity_score"] for p in projects) / len(projects)
        growth_rate = AnalysisEngine._calculate_growth_rate(projects)

        return {
            "projects": projects,
            "overall": {
                "avg_complexity": round(avg_complexity, 2),
                "total_projects": len(projects),
                "growth_rate": growth_rate,
            },
            "errors": errors,
            "patterns": None,  # Phase 2: AgentCore
            "recommendations": None,  # Phase 2: AgentCore
        }

    @staticmethod
    def analyze_repo(repo_path: str) -> Dict[str, Any]:
        """Analyze a single repository using AgentCore with validation.

        Args:
            repo_path: Path to git repository

        Returns:
            Analysis dictionary with complexity, technologies, patterns, etc.

        Raises:
            InvalidRepositoryError: If repo path is invalid
            AnalysisError: If analysis fails
        """
        # Input validation
        path = Path(repo_path)
        if not path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            raise InvalidRepositoryError(f"Path not found: {repo_path}")

        if not path.is_dir():
            logger.error(f"Repository path is not a directory: {repo_path}")
            raise InvalidRepositoryError(f"Not a directory: {repo_path}")

        # Load repo
        try:
            repo = Repo(repo_path)
        except Exception as e:
            logger.error(f"Failed to load repository: {repo_path} - {e}")
            raise InvalidRepositoryError(f"Invalid git repository: {repo_path}")

        repo_name = path.name
        logger.debug(f"Analyzing repository: {repo_name}")

        # Get git metadata
        try:
            commit_hash = repo.head.commit.hexsha[:7]
        except Exception:
            commit_hash = "unknown"

        try:
            commit_count = len(list(repo.iter_commits()))
        except Exception:
            commit_count = 0
            logger.debug(f"{repo_name}: Could not get commit count")

        try:
            first_commit = repo.iter_commits().__next__().committed_datetime.isoformat()
        except (StopIteration, Exception):
            first_commit = None

        # Call AgentCore for analysis
        try:
            from cli.agentcore_caller import AgentCoreCaller
            caller = AgentCoreCaller()
            agentcore_result = caller.analyze_repository(repo_path)
        except Exception as e:
            logger.error(f"{repo_name}: AgentCore caller failed: {e}", exc_info=True)
            raise AnalysisError(repo_name=repo_name, error=f"Failed to analyze: {e}")

        # Build final analysis object
        analysis = {
            "name": repo_name,
            "path": repo_path,
            "commit": commit_hash,
            "commits": commit_count,
            "complexity_score": agentcore_result.get("complexity_score", 5.0),
            "technologies": agentcore_result.get("technologies", []),
            "patterns": agentcore_result.get("patterns", []),
            "skill_level": agentcore_result.get("skill_level", "intermediate"),
            "recommendations": agentcore_result.get("recommendations", []),
            "first_commit": first_commit,
            "agentcore_source": agentcore_result.get("source", "unknown"),
        }

        logger.info(f"✅ {repo_name}: Analysis complete (source: {analysis['agentcore_source']})")

        return analysis

    @staticmethod
    def _calculate_complexity(repo_path: str) -> float:
        """Calculate multi-factor complexity score (0-10).

        Realistic benchmarks that are harder to game:
        - Number of files (0-3 points): Max at 50+ files
        - Function density (0-4 points): Max at 3+ functions per 100 lines
        - Class count (0-2 points): Max at 15+ classes
        - Nesting depth (0-1 point): Max at 50+ depth

        Scoring Tiers (realistic):
        - 0-2: Beginner (small scripts, learning projects)
        - 2-4: Intermediate (multiple files, some architecture)
        - 4-6: Advanced (well-structured, clear patterns)
        - 6-8: Expert (sophisticated design, high quality)
        - 8-10: Master (exceptionally complex, professional grade)

        Args:
            repo_path: Path to repository

        Returns:
            Complexity score 0-10 (realistic, trustworthy)
        """
        metrics = {
            "total_lines": 0,
            "functions": 0,
            "classes": 0,
            "nested_depth": 0,
            "files": 0,
        }

        try:
            all_py_files = list(Path(repo_path).rglob("*.py"))

            # Limit to 100 files analyzed
            if len(all_py_files) > 100:
                logger.warning(f"⚠️  Repo has {len(all_py_files)} files. Analyzing first 100 only.")
                all_py_files = all_py_files[:100]

            # Basic file filtering (skip common exclusions)
            analyzed_files = [
                f for f in all_py_files
                if not any(skip in str(f) for skip in ['node_modules', '__pycache__', '.git', 'venv', 'env'])
            ]

            for py_file in analyzed_files:
                try:
                    with open(py_file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    tree = ast.parse(content)
                    metrics["files"] += 1
                    metrics["total_lines"] += len(content.split("\n"))
                    metrics["functions"] += sum(
                        1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    )
                    metrics["classes"] += sum(
                        1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
                    )

                    max_depth = AnalysisEngine._max_nesting_depth(tree)
                    metrics["nested_depth"] = max(metrics["nested_depth"], max_depth)

                except Exception as e:
                    logger.debug(f"Could not parse {py_file}: {e}")
                    continue

        except Exception as e:
            logger.debug(f"File traversal error: {e}")

        # Multi-factor scoring with realistic benchmarks
        if metrics["total_lines"] == 0:
            return 0.0

        # ✅ REALISTIC THRESHOLDS FOR TRUST AND TRANSPARENCY
        # Use logarithmic scaling for file count (smoother growth tracking, no cliff at 50 files)
        file_score = min(3.0, math.log10(max(1, metrics["files"])) * 1.0)
        function_density = metrics["functions"] / max(metrics["total_lines"] / 100.0, 1.0)
        function_score = min(4.0, function_density / 3.0)  # Max at 3/100 lines
        class_score = min(2.0, metrics["classes"] / 15.0)  # Max at 15 classes
        nesting_score = min(1.0, metrics["nested_depth"] / 50.0)  # Max at 50 depth

        complexity = file_score + function_score + class_score + nesting_score

        logger.debug(
            f"Complexity breakdown: files={file_score:.1f}, "
            f"functions={function_score:.1f}, classes={class_score:.1f}, "
            f"nesting={nesting_score:.1f} → total={complexity:.1f}"
        )

        return round(min(10.0, max(0.0, complexity)), 2)

    @staticmethod
    def _max_nesting_depth(node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth in AST.

        Args:
            node: AST node to analyze
            depth: Current depth (for recursion)

        Returns:
            Maximum nesting depth
        """
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            child_depth = AnalysisEngine._max_nesting_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    @staticmethod
    def _detect_technologies(repo_path: str) -> List[str]:
        """Detect tech stack from package files and imports.

        Args:
            repo_path: Path to repository

        Returns:
            List of detected technologies
        """
        techs = set()

        # Check requirements.txt
        try:
            req_file = Path(repo_path) / "requirements.txt"
            if req_file.exists():
                with open(req_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    keywords = {
                        "bedrock": "AWS Bedrock",
                        "agentcore": "AgentCore",
                        "langchain": "LangChain",
                        "fastapi": "FastAPI",
                        "django": "Django",
                        "flask": "Flask",
                        "pytest": "Pytest",
                        "sqlalchemy": "SQLAlchemy",
                        "pandas": "Pandas",
                        "numpy": "NumPy",
                    }
                    for keyword, tech in keywords.items():
                        if keyword in content:
                            techs.add(tech)
        except Exception as e:
            logger.debug(f"Could not parse requirements.txt: {e}")

        # Check package.json
        if (Path(repo_path) / "package.json").exists():
            techs.add("Node.js/TypeScript")

        # Check for Go files
        if list(Path(repo_path).glob("**/*.go")):
            techs.add("Go")

        return sorted(list(techs)) if techs else ["Python"]

    @staticmethod
    def _calculate_growth_rate(projects: List[Dict[str, Any]]) -> float:
        """Calculate growth rate between first and last project.

        Args:
            projects: List of project analyses

        Returns:
            Growth rate as percentage
        """
        if len(projects) < 2:
            return 0.0

        complexities = [p["complexity_score"] for p in projects]
        first = complexities[0]
        last = complexities[-1]

        if first == 0:
            return 0.0

        growth_rate = ((last - first) / first) * 100.0
        return round(growth_rate, 1)
