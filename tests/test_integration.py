"""Integration tests - CLI → Storage → API end-to-end."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from cli.analyzer import AnalysisEngine
from cli.storage import StorageManager
from backend.services import AnalysisService


class TestEndToEndIntegration:
    """Integration tests for full data flow."""

    @pytest.fixture
    def integration_storage(self, tmp_path):
        """Setup storage for integration test."""
        return StorageManager(base_dir=tmp_path)

    @patch("cli.analyzer.Repo")
    def test_cli_to_storage_to_service(self, mock_repo_class, integration_storage):
        """Test full flow: CLI analyzes → Storage saves → Service retrieves.
        
        This tests the complete data pipeline:
        1. CLI analyzer produces analysis data
        2. Storage manager persists it
        3. API service retrieves it
        
        Simulating: CLI runs → data saved → API serves it
        """
        # Setup mock Git repo
        mock_git_repo = MagicMock()
        mock_git_repo.iter_commits.return_value = [MagicMock() for _ in range(10)]
        mock_repo_class.return_value = mock_git_repo

        # Step 1: CLI analyzes repository
        analysis_result = AnalysisEngine.run(["/mock/repo1", "/mock/repo2"])

        assert len(analysis_result["projects"]) == 2
        assert "overall" in analysis_result

        # Step 2: Storage saves analysis
        filepath = integration_storage.save_analysis(analysis_result)
        assert filepath.exists()

        # Step 3: API service retrieves analysis
        service = AnalysisService(integration_storage)
        loaded_analysis = service.get_latest_analysis()

        assert loaded_analysis is not None
        assert len(loaded_analysis["projects"]) == 2
        assert loaded_analysis["overall"]["avg_complexity"] == analysis_result["overall"]["avg_complexity"]

    @patch("cli.analyzer.Repo")
    def test_multiple_analyses_timeline(self, mock_repo_class, integration_storage):
        """Test timeline building across multiple analyses.
        
        Simulating: Run analysis twice, timeline shows growth
        """
        mock_git_repo = MagicMock()
        mock_repo_class.return_value = mock_git_repo

        # First analysis run
        mock_git_repo.iter_commits.return_value = [MagicMock() for _ in range(5)]
        analysis1 = AnalysisEngine.run(["/mock/repo"])
        integration_storage.save_analysis(analysis1)

        # Second analysis run (simulating growth)
        mock_git_repo.iter_commits.return_value = [MagicMock() for _ in range(10)]
        analysis2 = AnalysisEngine.run(["/mock/repo"])
        integration_storage.save_analysis(analysis2)

        # Service retrieves all analyses (timeline)
        service = AnalysisService(integration_storage)
        all_analyses = service.get_all_analyses()

        assert len(all_analyses) == 2
        # Most recent should be first (sorted by timestamp)
        assert all_analyses[0]["timestamp"] >= all_analyses[1]["timestamp"]

    @patch("cli.analyzer.Repo")
    def test_error_handling_in_pipeline(self, mock_repo_class, integration_storage):
        """Test error handling at each stage of pipeline.
        
        CLI error → Storage handles gracefully → Service reports state
        """
        # First repo succeeds
        mock_git_repo = MagicMock()
        mock_git_repo.iter_commits.return_value = [MagicMock() for _ in range(5)]
        mock_repo_class.return_value = mock_git_repo

        # Second repo fails (git error)
        def repo_side_effect(path):
            if "repo1" in path:
                return mock_git_repo
            else:
                raise RuntimeError("Git error")

        mock_repo_class.side_effect = repo_side_effect

        # CLI should aggregate errors but still work
        analysis = AnalysisEngine.run(["/mock/repo1", "/mock/repo2"])

        assert len(analysis["projects"]) >= 1  # At least one succeeded
        assert len(analysis["errors"]) >= 1    # At least one failed

        # Storage should still save the partial result
        filepath = integration_storage.save_analysis(analysis)
        assert filepath.exists()

        # Service should retrieve the partial data
        service = AnalysisService(integration_storage)
        loaded = service.get_latest_analysis()
        assert loaded["overall"]["total_projects"] >= 1

    def test_storage_data_validation_pipeline(self, integration_storage):
        """Test that storage validates data integrity.
        
        Ensures API only serves valid data
        """
        # Valid analysis
        valid_analysis = {
            "projects": [
                {
                    "name": "test",
                    "path": "/test",
                    "commits": 5,
                    "complexity_score": 5.0,
                    "technologies": ["Python"],
                }
            ],
            "overall": {
                "avg_complexity": 5.0,
                "total_projects": 1,
                "growth_rate": 0.0,
            },
        }

        filepath = integration_storage.save_analysis(valid_analysis)

        # Load and validate
        loaded = integration_storage.load_latest_analysis()

        assert loaded is not None
        assert loaded["projects"][0]["name"] == "test"
        assert loaded["overall"]["total_projects"] == 1

        # Write invalid JSON manually
        invalid_file = integration_storage.analyses_dir / "invalid.json"
        invalid_file.write_text("{bad json")

        # Should still load valid analyses and skip invalid
        all_analyses = integration_storage.load_all_analyses()
        assert len(all_analyses) == 1  # Only the valid one
