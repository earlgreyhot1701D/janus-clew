"""Tests for the storage module."""

import json
import tempfile
from pathlib import Path

import pytest

from cli.storage import StorageManager
from exceptions import StorageReadError, StorageWriteError


class TestStorageManager:
    """Tests for StorageManager class."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create StorageManager with temp directory (pytest fixture).
        
        Using tmp_path is cleaner than tempfile.TemporaryDirectory()
        because pytest handles cleanup automatically.
        """
        return StorageManager(base_dir=tmp_path)

    @pytest.fixture
    def sample_analysis(self):
        """Sample analysis data."""
        return {
            "projects": [
                {
                    "name": "test-project",
                    "path": "/path/to/test",
                    "commits": 10,
                    "complexity_score": 7.0,
                    "technologies": ["Python"],
                }
            ],
            "overall": {
                "avg_complexity": 7.0,
                "total_projects": 1,
                "growth_rate": 0.0,
            },
        }

    def test_save_analysis(self, storage, sample_analysis):
        """Test saving analysis."""
        filepath = storage.save_analysis(sample_analysis)

        assert filepath.exists()
        assert filepath.suffix == ".json"
        assert "timestamp" in sample_analysis
        assert "version" in sample_analysis

    def test_load_latest_analysis(self, storage, sample_analysis):
        """Test loading latest analysis."""
        storage.save_analysis(sample_analysis.copy())

        loaded = storage.load_latest_analysis()

        assert loaded is not None
        assert len(loaded["projects"]) == 1

    def test_load_all_analyses(self, storage, sample_analysis):
        """Test loading all analyses."""
        storage.save_analysis(sample_analysis.copy())
        storage.save_analysis(sample_analysis.copy())

        analyses = storage.load_all_analyses()

        assert len(analyses) >= 2

    def test_load_all_analyses_empty(self, storage):
        """Test loading analyses when none exist."""
        analyses = storage.load_all_analyses()

        assert isinstance(analyses, list)
        assert len(analyses) == 0

    def test_get_analysis_count(self, storage, sample_analysis):
        """Test counting analyses."""
        storage.save_analysis(sample_analysis.copy())
        storage.save_analysis(sample_analysis.copy())

        count = storage.get_analysis_count()

        assert count == 2

    def test_get_analysis_count_empty(self, storage):
        """Test count when no analyses."""
        count = storage.get_analysis_count()

        assert count == 0

    def test_save_analysis_invalid_path(self):
        """Test saving to invalid path."""
        invalid_storage = StorageManager(base_dir=Path("/invalid/path/that/does/not/exist"))

        with pytest.raises(StorageWriteError):
            invalid_storage.save_analysis({})

    def test_delete_analysis(self, storage, sample_analysis):
        """Test deleting an analysis."""
        filepath = storage.save_analysis(sample_analysis.copy())
        filename = filepath.name

        storage.delete_analysis(filename)

        assert not filepath.exists()

    def test_clear_analyses(self, storage, sample_analysis):
        """Test clearing all analyses."""
        storage.save_analysis(sample_analysis.copy())
        storage.save_analysis(sample_analysis.copy())

        storage.clear_analyses()

        count = storage.get_analysis_count()
        assert count == 0

    def test_analysis_data_validation(self, storage):
        """Test that invalid JSON is skipped."""
        # Write invalid JSON manually
        invalid_file = storage.analyses_dir / "invalid.json"
        invalid_file.write_text("{invalid json")

        # Should load other valid analyses
        analyses = storage.load_all_analyses()

        # Should not raise error
        assert isinstance(analyses, list)
