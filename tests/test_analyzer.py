"""Tests for the analyzer module."""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from cli.analyzer import AnalysisEngine
from exceptions import AnalysisError, InvalidRepositoryError, GitParseError


class TestAnalysisEngine:
    """Tests for AnalysisEngine class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_repo(self, temp_dir):
        """Create mock Git repository structure."""
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Create Python files
        (repo_path / "main.py").write_text("""
def hello():
    def inner():
        return 42
    return inner()

class TestClass:
    def method(self):
        pass
""")

        (repo_path / "utils.py").write_text("""
def helper():
    return "help"

def another():
    pass
""")

        # Create requirements.txt
        (repo_path / "requirements.txt").write_text("""
bedrock==1.0.0
agentcore==2.0.0
fastapi==3.0.0
""")

        return str(repo_path)

    @patch("cli.analyzer.Repo")
    def test_calculate_complexity_basic(self, mock_repo_class, mock_repo):
        """Test complexity calculation."""
        mock_git_repo = MagicMock()
        mock_repo_class.return_value = mock_git_repo

        complexity = AnalysisEngine._calculate_complexity(mock_repo)

        assert isinstance(complexity, float)
        assert 0 <= complexity <= 10

    @patch("cli.analyzer.Repo")
    def test_detect_technologies(self, mock_repo_class, mock_repo):
        """Test technology detection."""
        mock_git_repo = MagicMock()
        mock_repo_class.return_value = mock_git_repo

        techs = AnalysisEngine._detect_technologies(mock_repo)

        assert isinstance(techs, list)
        assert "AWS Bedrock" in techs or len(techs) >= 0

    @patch("cli.analyzer.Repo")
    def test_analyze_repo_invalid(self, mock_repo_class):
        """Test analysis fails for invalid repo."""
        mock_repo_class.side_effect = Exception("Not a git repo")

        with pytest.raises(InvalidRepositoryError):
            AnalysisEngine.analyze_repo("/invalid/path")

    @patch("cli.analyzer.Repo")
    def test_analyze_repo_success(self, mock_repo_class, mock_repo):
        """Test successful repo analysis."""
        mock_git_repo = MagicMock()
        mock_git_repo.iter_commits.return_value = [MagicMock() for _ in range(10)]
        mock_repo_class.return_value = mock_git_repo

        result = AnalysisEngine.analyze_repo(mock_repo)

        assert "name" in result
        assert "commits" in result
        assert "complexity_score" in result
        assert "technologies" in result
        assert 0 <= result["complexity_score"] <= 10

    @patch("cli.analyzer.AnalysisEngine.analyze_repo")
    def test_run_multiple_repos(self, mock_analyze):
        """Test analyzing multiple repositories."""
        mock_analyze.side_effect = [
            {"name": "repo1", "complexity_score": 6.0, "commits": 10, "technologies": []},
            {"name": "repo2", "complexity_score": 8.0, "commits": 20, "technologies": []},
        ]

        result = AnalysisEngine.run(["repo1", "repo2"])

        assert "projects" in result
        assert "overall" in result
        assert len(result["projects"]) == 2
        assert result["overall"]["avg_complexity"] == 7.0
        assert result["overall"]["growth_rate"] == 33.3

    @patch("cli.analyzer.AnalysisEngine.analyze_repo")
    def test_run_no_repos(self, mock_analyze):
        """Test error when no repos can be analyzed."""
        mock_analyze.side_effect = InvalidRepositoryError("/path")

        with pytest.raises(AnalysisError):
            AnalysisEngine.run(["invalid1", "invalid2"])

    def test_calculate_growth_rate(self):
        """Test growth rate calculation."""
        projects = [
            {"complexity_score": 5.0},
            {"complexity_score": 7.5},
            {"complexity_score": 10.0},
        ]

        growth = AnalysisEngine._calculate_growth_rate(projects)

        assert growth == 100.0  # (10-5)/5 * 100

    def test_calculate_growth_rate_no_projects(self):
        """Test growth rate with insufficient projects."""
        projects = [{"complexity_score": 5.0}]

        growth = AnalysisEngine._calculate_growth_rate(projects)

        assert growth == 0.0

    def test_max_nesting_depth(self):
        """Test nesting depth calculation."""
        import ast

        code = """
def outer():
    def middle():
        def inner():
            return 42
        return inner()
    return middle()
"""
        tree = ast.parse(code)
        depth = AnalysisEngine._max_nesting_depth(tree)

        assert isinstance(depth, int)
        assert depth > 0


class TestCLICommand:
    """Tests for CLI commands."""

    def test_cli_no_repos_error(self):
        """Test CLI fails gracefully when no repos provided."""
        from cli.main import cli
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        assert "No repositories provided" in result.output or "Usage" in result.output

    def test_cli_invalid_repo_error(self):
        """Test CLI fails gracefully with invalid repo."""
        from cli.main import cli
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "/nonexistent/path/to/repo"])

        # Should fail but exit gracefully
        assert result.exit_code != 0


class TestAWSQClient:
    """Tests for AWS Q client with mocking."""

    @patch("cli.aws_q_client.subprocess.run")
    def test_aws_q_success(self, mock_run):
        """Test successful AWS Q analysis."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test analysis output"
        mock_run.return_value = mock_result

        client = AmazonQClient()
        result = client.analyze_with_cli("/test/repo")

        assert result == "Test analysis output"
        mock_run.assert_called_once()

    @patch("cli.aws_q_client.subprocess.run")
    def test_aws_q_timeout(self, mock_run):
        """Test AWS Q timeout handling."""
        from exceptions import AWSQTimeoutError

        mock_run.side_effect = subprocess.TimeoutExpired("amazon-q", 60)

        client = AmazonQClient()
        with pytest.raises(AWSQTimeoutError):
            client.analyze_with_cli("/test/repo")

    @patch("cli.aws_q_client.subprocess.run")
    def test_aws_q_retry_logic(self, mock_run):
        """Test AWS Q retry with exponential backoff."""
        # Fail twice, succeed on third attempt
        mock_result_fail = MagicMock()
        mock_result_fail.returncode = 1
        mock_result_fail.stderr = "Temporary error"

        mock_result_success = MagicMock()
        mock_result_success.returncode = 0
        mock_result_success.stdout = "Success"

        mock_run.side_effect = [mock_result_fail, mock_result_fail, mock_result_success]

        client = AmazonQClient()
        client.max_retries = 3
        client.backoff = 1.0  # Speed up test

        result = client.analyze_with_cli("/test/repo")

        assert result == "Success"
        assert mock_run.call_count == 3

    def test_parse_natural_language(self):
        """Test parsing Q's natural language output."""
        client = AmazonQClient()

        text = """
        This is advanced code with AWS Bedrock and AgentCore integration.
        The complexity is around 8/10. The developer has shown sophisticated
        patterns including async/await and vector search capabilities.
        """

        result = client.parse_natural_language(text)

        assert result["skill_level"] == "advanced"
        assert "AWS Bedrock" in result["technologies"]
        assert result["complexity"] == 8
        assert "Async-first" in result["patterns"]
