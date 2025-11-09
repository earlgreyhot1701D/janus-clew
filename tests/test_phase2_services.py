"""Tests for Phase 2 Development Signature services.

Tests all core logic with mock data. No external dependencies required.
"""

import pytest
from unittest.mock import Mock, patch

from backend.services.pattern_detector import PatternDetector, PatternDetectorError
from backend.services.trajectory_analyzer import TrajectoryAnalyzer, TrajectoryAnalyzerError
from backend.services.preference_analyzer import PreferenceAnalyzer, PreferenceAnalyzerError
from backend.services.recommendation_engine import RecommendationEngine, RecommendationEngineError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_analyses():
    """Sample analyses for testing."""
    return [
        {
            "timestamp": "2025-09-01",
            "projects": [
                {
                    "name": "Your-Honor",
                    "complexity_score": 2.1,
                    "technologies": ["Python", "LangChain"],
                    "commits": 28
                }
            ],
            "overall": {"avg_complexity": 2.1, "total_projects": 1}
        },
        {
            "timestamp": "2025-10-15",
            "projects": [
                {
                    "name": "Ariadne-Clew",
                    "complexity_score": 4.2,
                    "technologies": ["Python", "AWS Bedrock", "AgentCore"],
                    "commits": 42
                }
            ],
            "overall": {"avg_complexity": 4.2, "total_projects": 1}
        },
        {
            "timestamp": "2025-11-09",
            "projects": [
                {
                    "name": "Janus-Clew",
                    "complexity_score": 8.1,
                    "technologies": ["TypeScript", "Python", "AWS Bedrock"],
                    "commits": 73
                }
            ],
            "overall": {"avg_complexity": 8.1, "total_projects": 1}
        }
    ]


@pytest.fixture
def empty_analyses():
    """Empty analyses."""
    return []


# ============================================================================
# PATTERN DETECTOR TESTS
# ============================================================================

class TestPatternDetector:
    """Tests for PatternDetector."""

    def test_detect_patterns_valid(self, sample_analyses):
        """Test pattern detection with valid data."""
        detector = PatternDetector()
        result = detector.detect_patterns(sample_analyses)

        assert "patterns" in result
        assert len(result["patterns"]) > 0

        # Check pattern structure
        for pattern in result["patterns"]:
            assert "name" in pattern
            assert "evidence" in pattern
            assert "confidence" in pattern
            assert 0 <= pattern["confidence"] <= 1

    def test_detect_patterns_empty(self):
        """Test pattern detection with empty analyses."""
        detector = PatternDetector()

        with pytest.raises(PatternDetectorError):
            detector.detect_patterns([])

    def test_fallback_pattern_detection(self, sample_analyses):
        """Test fallback pattern detection."""
        detector = PatternDetector()
        result = detector._fallback_pattern_detection(sample_analyses)

        assert "patterns" in result
        assert result["fallback"] is True

        # Should detect database avoidance (0 SQL projects)
        db_pattern = [p for p in result["patterns"] if "database" in p["name"].lower()]
        assert len(db_pattern) > 0

    def test_validate_patterns_valid(self, sample_analyses):
        """Test pattern validation with valid data."""
        detector = PatternDetector()
        patterns = detector.detect_patterns(sample_analyses)

        # Should not raise
        assert detector.validate_patterns(patterns) is True

    def test_validate_patterns_invalid_confidence(self):
        """Test pattern validation with invalid confidence."""
        detector = PatternDetector()
        patterns = {
            "patterns": [
                {
                    "name": "Test",
                    "evidence": "test",
                    "confidence": 1.5  # Invalid: > 1.0
                }
            ]
        }

        with pytest.raises(PatternDetectorError):
            detector.validate_patterns(patterns)


# ============================================================================
# TRAJECTORY ANALYZER TESTS
# ============================================================================

class TestTrajectoryAnalyzer:
    """Tests for TrajectoryAnalyzer."""

    def test_analyze_trajectory_valid(self, sample_analyses):
        """Test trajectory analysis with valid data."""
        analyzer = TrajectoryAnalyzer()
        result = analyzer.analyze_trajectory(sample_analyses)

        assert "growth_rate" in result
        assert "learning_velocity" in result
        assert "projected_4_weeks" in result
        assert "trend" in result

        # Check values are reasonable
        assert result["growth_rate"] > 1.0  # Should show growth
        assert 2.0 <= result["growth_rate"] <= 4.0  # 2.1 -> 8.1 = 3.86x
        assert result["learning_velocity"] > 0
        assert result["projected_4_weeks"] <= 10.0

    def test_analyze_trajectory_insufficient_data(self):
        """Test trajectory analysis with insufficient data."""
        analyzer = TrajectoryAnalyzer()

        with pytest.raises(TrajectoryAnalyzerError):
            analyzer.analyze_trajectory([{"projects": []}])

    def test_extract_complexities(self, sample_analyses):
        """Test complexity extraction."""
        analyzer = TrajectoryAnalyzer()
        complexities = analyzer._extract_complexities(sample_analyses)

        assert len(complexities) == 3
        assert complexities[0] == 2.1
        assert complexities[-1] == 8.1

    def test_detect_trend_accelerating(self):
        """Test trend detection for accelerating growth."""
        analyzer = TrajectoryAnalyzer()
        # Simulated accelerating: 2, 4, 8 (doubling each time)
        trend = analyzer._detect_trend([2, 4, 8])
        assert trend in ["accelerating", "steady"]

    def test_detect_trend_steady(self):
        """Test trend detection for steady growth."""
        analyzer = TrajectoryAnalyzer()
        trend = analyzer._detect_trend([2, 3, 4])
        assert trend in ["steady", "accelerating"]  # Consistent growth

    def test_detect_trend_decelerating(self):
        """Test trend detection for decelerating growth."""
        analyzer = TrajectoryAnalyzer()
        trend = analyzer._detect_trend([2, 8, 9])
        assert trend in ["decelerating", "steady"]

    def test_project_forward(self):
        """Test forward projection."""
        analyzer = TrajectoryAnalyzer()

        # Current: 8.1, velocity: 0.27/week, 4 weeks
        projected = analyzer._project_forward(8.1, 0.27, weeks=4)

        # Should be 8.1 + (0.27 * 4) = 9.18, capped at 10
        assert 8.1 <= projected <= 10.0
        assert projected > 8.1


# ============================================================================
# PREFERENCE ANALYZER TESTS
# ============================================================================

class TestPreferenceAnalyzer:
    """Tests for PreferenceAnalyzer."""

    def test_analyze_preferences_valid(self, sample_analyses):
        """Test preference analysis with valid data."""
        analyzer = PreferenceAnalyzer()
        result = analyzer.analyze_preferences(sample_analyses)

        assert "preferences" in result
        assert len(result["preferences"]) >= 4  # At least 4 preferences

        # Check preference structure
        for pref in result["preferences"]:
            assert "name" in pref
            assert "score" in pref
            assert "description" in pref
            assert 0 <= pref["score"] <= 1

    def test_analyze_preferences_empty(self):
        """Test preference analysis with empty analyses."""
        analyzer = PreferenceAnalyzer()

        with pytest.raises(PreferenceAnalyzerError):
            analyzer.analyze_preferences([])

    def test_calculate_state_preference_no_databases(self):
        """Test state preference when no databases used."""
        analyzer = PreferenceAnalyzer()
        # No PostgreSQL, MySQL, etc.
        score = analyzer._calculate_state_preference({"Python", "TypeScript"})

        assert score >= 0.90

    def test_calculate_state_preference_heavy_databases(self):
        """Test state preference with database use."""
        analyzer = PreferenceAnalyzer()
        score = analyzer._calculate_state_preference(
            {"PostgreSQL", "MySQL", "Redis"}
        )

        assert score < 0.50

    def test_calculate_async_preference_high(self, sample_analyses):
        """Test async preference with async projects."""
        analyzer = PreferenceAnalyzer()
        # Should detect async from sample (though limited)
        score = analyzer._calculate_async_preference(sample_analyses)

        assert 0 <= score <= 1

    def test_framework_diversity(self):
        """Test framework diversity calculation."""
        analyzer = PreferenceAnalyzer()

        # Many technologies
        score = analyzer._calculate_framework_diversity(
            {"Python", "TypeScript", "PostgreSQL", "AWS", "React", "Docker", "Kubernetes"}
        )
        assert score > 0.7

        # Few technologies
        score = analyzer._calculate_framework_diversity({"Python"})
        assert score < 0.3


# ============================================================================
# RECOMMENDATION ENGINE TESTS
# ============================================================================

class TestRecommendationEngine:
    """Tests for RecommendationEngine."""

    def test_generate_recommendations_valid(self):
        """Test recommendation generation with valid inputs."""
        engine = RecommendationEngine()

        patterns = {
            "patterns": [
                {
                    "name": "Database Avoidance",
                    "evidence": "No SQL",
                    "confidence": 0.98,
                    "impact": "Simple state"
                },
                {
                    "name": "Async-First",
                    "evidence": "Async/await",
                    "confidence": 0.87,
                    "impact": "Concurrency"
                }
            ]
        }
        preferences = {
            "preferences": [
                {"name": "State Simplicity", "score": 0.92},
                {"name": "Async Comfort", "score": 0.87}
            ]
        }
        trajectory = {
            "growth_rate": 2.5,
            "trend": "accelerating",
            "learning_velocity": 0.27
        }

        result = engine.generate_recommendations(patterns, preferences, trajectory)

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_generate_recommendations_missing_input(self):
        """Test recommendation generation with missing input."""
        engine = RecommendationEngine()

        with pytest.raises(RecommendationEngineError):
            engine.generate_recommendations({}, None, None)

    def test_validate_recommendations_valid(self):
        """Test recommendation validation with valid data."""
        engine = RecommendationEngine()

        recs = {
            "recommendations": [
                {
                    "skill": "PostgreSQL",
                    "status": "ready",
                    "confidence": 0.9,
                    "reasoning": "You're ready",
                    "evidence": ["test"],
                    "timeline": "4 weeks",
                    "next_action": "Build it"
                }
            ]
        }

        assert engine.validate_recommendations(recs) is True

    def test_validate_recommendations_invalid_status(self):
        """Test recommendation validation with invalid status."""
        engine = RecommendationEngine()

        recs = {
            "recommendations": [
                {
                    "skill": "PostgreSQL",
                    "status": "maybe",  # Invalid
                    "confidence": 0.9,
                    "reasoning": "test"
                }
            ]
        }

        with pytest.raises(RecommendationEngineError):
            engine.validate_recommendations(recs)

    def test_validate_recommendations_invalid_confidence(self):
        """Test recommendation validation with invalid confidence."""
        engine = RecommendationEngine()

        recs = {
            "recommendations": [
                {
                    "skill": "PostgreSQL",
                    "status": "ready",
                    "confidence": 1.5,  # Invalid: > 1.0
                    "reasoning": "test"
                }
            ]
        }

        with pytest.raises(RecommendationEngineError):
            engine.validate_recommendations(recs)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for full signature generation."""

    def test_full_pipeline(self, sample_analyses):
        """Test full Development Signature pipeline."""
        # 1. Detect patterns
        pattern_detector = PatternDetector()
        patterns = pattern_detector.detect_patterns(sample_analyses)

        # 2. Analyze preferences
        preference_analyzer = PreferenceAnalyzer()
        preferences = preference_analyzer.analyze_preferences(sample_analyses)

        # 3. Analyze trajectory
        trajectory_analyzer = TrajectoryAnalyzer()
        trajectory = trajectory_analyzer.analyze_trajectory(sample_analyses)

        # 4. Generate recommendations
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations(
            patterns, preferences, trajectory
        )

        # All should succeed
        assert patterns is not None
        assert preferences is not None
        assert trajectory is not None
        assert recommendations is not None

        # Validate all outputs
        pattern_detector.validate_patterns(patterns)
        engine.validate_recommendations(recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
