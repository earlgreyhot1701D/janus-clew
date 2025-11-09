"""Repository analysis engine using Git and AST parsing."""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from git import Repo

from exceptions import GitParseError, InvalidRepositoryError, AnalysisError
from logger import get_logger

logger = get_logger(__name__)


class AnalysisEngine:
    """Analyzes Git repositories for complexity, technologies, and patterns."""

    @staticmethod
    def run(repos: List[str]) -> Dict[str, Any]:
        """Analyze multiple repositories with comprehensive error handling.

        Args:
            repos: List of repository paths to analyze

        Returns:
            Dictionary with projects and overall metrics

        Raises:
            AnalysisError: If analysis fails
            InvalidRepositoryError: If repo is invalid
        """
        projects = []
        errors = []

        for repo_path in repos:
            try:
                # ✅ Security: Sanitize path for logging (prevent log injection)
                safe_path = Path(repo_path).name or str(repo_path).replace("\n", "\\n")
                logger.debug(f"Analyzing repository: {safe_path}")
                analysis = AnalysisEngine.analyze_repo(repo_path)
                projects.append(analysis)
                logger.info(f"✓ {analysis['name']}: {analysis['complexity_score']:.1f} complexity")
            except (InvalidRepositoryError, GitParseError, AnalysisError) as e:
                # ✅ Security: Sanitize error message (prevent log injection)
                safe_path = Path(repo_path).name or str(repo_path).replace("\n", "\\n")
                safe_error = str(e).replace("\n", " ")
                logger.warning(f"Skipping {safe_path}: {safe_error}")
                errors.append({"repo": repo_path, "error": str(e)})
            except Exception as e:
                # ✅ Security: Sanitize path and error
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
        """Analyze a single git repository.

        Args:
            repo_path: Path to repository

        Returns:
            Analysis dictionary for the repository

        Raises:
            InvalidRepositoryError: If not a valid git repo
            GitParseError: If git parsing fails
        """
        try:
            repo = Repo(repo_path)
        except Exception as e:
            raise InvalidRepositoryError(repo_path)

        try:
            complexity = AnalysisEngine._calculate_complexity(repo_path)
            techs = AnalysisEngine._detect_technologies(repo_path)
            commit_count = len(list(repo.iter_commits()))
            first_commit = None

            try:
                first_commit = repo.iter_commits().__next__().committed_datetime.isoformat()
            except (StopIteration, Exception):
                pass

            return {
                "name": Path(repo_path).name,
                "path": repo_path,
                "commits": commit_count,
                "complexity_score": complexity,
                "technologies": techs,
                "first_commit": first_commit,
                "q_analysis": None,  # Will be populated by AWS Q
            }
        except Exception as e:
            raise GitParseError(repo_path, str(e))

    @staticmethod
    def _calculate_complexity(repo_path: str) -> float:
        """Calculate multi-factor complexity score (0-10).

        Factors considered:
        - Number of files (0-3 points)
        - Function density (0-4 points)
        - Class count (0-2 points)
        - Nesting depth (0-1 point)

        Args:
            repo_path: Path to repository

        Returns:
            Complexity score 0-10
        """
        metrics = {
            "total_lines": 0,
            "functions": 0,
            "classes": 0,
            "nested_depth": 0,
            "files": 0,
        }

        try:
            for py_file in Path(repo_path).rglob("*.py"):
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

        # Multi-factor scoring
        if metrics["total_lines"] == 0:
            return 0.0

        file_score = min(3.0, metrics["files"] / 5.0)
        function_density = metrics["functions"] / max(metrics["total_lines"] / 100.0, 1.0)
        function_score = min(4.0, function_density)
        class_score = min(2.0, metrics["classes"] / 3.0)
        nesting_score = min(1.0, metrics["nested_depth"] / 20.0)

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
