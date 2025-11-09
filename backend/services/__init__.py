"""Janus Clew Backend Services - Business logic layer."""

from typing import Dict, List, Any, Optional

from cli.storage import StorageManager
from backend.services.pattern_detector import PatternDetector
from backend.services.preference_analyzer import PreferenceAnalyzer
from backend.services.trajectory_analyzer import TrajectoryAnalyzer
from backend.services.recommendation_engine import RecommendationEngine
from exceptions import NotFoundError
from logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """Service for analysis operations."""

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize analysis service.

        Args:
            storage: StorageManager instance (or create new one)
        """
        self.storage = storage or StorageManager()

    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Get all stored analyses.

        Returns:
            List of analysis dictionaries sorted by timestamp (newest first)
        """
        logger.debug("Fetching all analyses")
        analyses = self.storage.load_all_analyses()
        logger.debug(f"Found {len(analyses)} analyses")
        return analyses

    def get_latest_analysis(self) -> Dict[str, Any]:
        """Get the most recent analysis.

        Returns:
            Latest analysis dictionary

        Raises:
            NotFoundError: If no analyses exist
        """
        logger.debug("Fetching latest analysis")
        analysis = self.storage.load_latest_analysis()

        if not analysis:
            raise NotFoundError("No analyses found")

        return analysis

    def get_analysis_count(self) -> int:
        """Get total number of stored analyses.

        Returns:
            Count of analyses
        """
        count = self.storage.get_analysis_count()
        logger.debug(f"Analysis count: {count}")
        return count


class TimelineService:
    """Service for timeline data operations."""

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize timeline service."""
        self.storage = storage or StorageManager()
        self.analysis_service = AnalysisService(storage)

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get timeline data for all analyses.

        Returns:
            List of timeline points sorted by date
        """
        logger.debug("Building timeline")

        analyses = self.analysis_service.get_all_analyses()
        timeline = []

        for analysis in analyses:
            for project in analysis.get("projects", []):
                point = {
                    "date": analysis.get("timestamp", "unknown"),
                    "project_name": project.get("name", "unknown"),
                    "complexity": project.get("complexity_score", 0),
                    "skills": project.get("technologies", []),
                }
                timeline.append(point)

        logger.debug(f"Timeline has {len(timeline)} points")
        return timeline


class SkillsService:
    """Service for skills data operations."""

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize skills service."""
        self.storage = storage or StorageManager()
        self.analysis_service = AnalysisService(storage)

    def get_skills(self) -> List[Dict[str, Any]]:
        """Get detected skills from latest analysis.

        Returns:
            List of skill dictionaries with project information
        """
        logger.debug("Extracting skills")

        analysis = self.analysis_service.get_latest_analysis()
        skills = {}

        for project in analysis.get("projects", []):
            for tech in project.get("technologies", []):
                if tech not in skills:
                    skills[tech] = {
                        "name": tech,
                        "confidence": 0.8,
                        "projects": [],
                    }
                skills[tech]["projects"].append(project.get("name", ""))

        skill_list = list(skills.values())
        logger.debug(f"Found {len(skill_list)} unique skills")
        return skill_list


class GrowthService:
    """Service for growth metrics operations."""

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize growth service."""
        self.storage = storage or StorageManager()
        self.analysis_service = AnalysisService(storage)

    def get_growth_metrics(self) -> Dict[str, Any]:
        """Get overall growth metrics.

        Returns:
            Dictionary with growth metrics
        """
        logger.debug("Calculating growth metrics")

        analysis = self.analysis_service.get_latest_analysis()
        overall = analysis.get("overall", {})

        metrics = {
            "avg_complexity": overall.get("avg_complexity", 0),
            "total_projects": overall.get("total_projects", 0),
            "growth_rate": overall.get("growth_rate", 0),
        }

        logger.debug(f"Growth metrics: {metrics}")
        return metrics


class ComplexityService:
    """Service for complexity breakdown operations."""

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize complexity service."""
        self.storage = storage or StorageManager()
        self.analysis_service = AnalysisService(storage)

    def get_complexity_breakdown(self, project_name: str) -> Dict[str, Any]:
        """Get complexity breakdown for specific project.

        Args:
            project_name: Name of project to get breakdown for

        Returns:
            Dictionary with complexity breakdown

        Raises:
            NotFoundError: If project not found
        """
        logger.debug(f"Getting complexity breakdown for {project_name}")

        try:
            analysis = self.analysis_service.get_latest_analysis()
        except NotFoundError:
            raise NotFoundError(f"No analyses available to find project {project_name}")

        for project in analysis.get("projects", []):
            if project.get("name", "").lower() == project_name.lower():
                breakdown = {
                    "project": project.get("name"),
                    "total_score": project.get("complexity_score", 0),
                    "file_score": 0.0,  # Would need to re-analyze for detailed breakdown
                    "function_score": 0.0,
                    "class_score": 0.0,
                    "nesting_score": 0.0,
                    "explanation": (
                        "Complexity calculated using multi-factor analysis: "
                        "files, functions, classes, and nesting depth"
                    ),
                }
                logger.debug(f"Found complexity for {project_name}")
                return breakdown

        raise NotFoundError(f"Project {project_name} not found")


class DevelopmentSignatureService:
    """Service for Development Signature generation (Phase 2).

    Generates complete development profile with patterns, preferences,
    trajectory, and forward-looking recommendations.
    """

    def __init__(self, storage: Optional[StorageManager] = None):
        """Initialize Development Signature service.

        Args:
            storage: StorageManager instance (or create new one)
        """
        self.storage = storage or StorageManager()
        self.analysis_service = AnalysisService(storage)
        self.pattern_detector = PatternDetector()
        self.preference_analyzer = PreferenceAnalyzer()
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.recommendation_engine = RecommendationEngine()

    def generate_development_signature(self) -> Dict[str, Any]:
        """Generate complete Development Signature.

        Orchestrates pattern detection, preference analysis, trajectory
        analysis, and recommendation generation into one comprehensive signature.

        Returns:
            Dictionary with patterns, preferences, trajectory, recommendations

        Raises:
            NotFoundError: If no analyses available
        """
        logger.debug("Generating Development Signature")

        try:
            analyses = self.analysis_service.get_all_analyses()
            if not analyses:
                raise NotFoundError("No analyses found for signature generation")

            # Step 1: Detect patterns across all projects
            logger.debug("Step 1: Detecting patterns")
            patterns = self.pattern_detector.detect_patterns(analyses)

            # Step 2: Analyze architectural preferences
            logger.debug("Step 2: Analyzing preferences")
            preferences = self.preference_analyzer.analyze_preferences(analyses)

            # Step 3: Analyze learning trajectory
            logger.debug("Step 3: Analyzing trajectory")
            trajectory = self.trajectory_analyzer.analyze_trajectory(analyses)

            # Step 4: Generate forward-looking recommendations
            logger.debug("Step 4: Generating recommendations")
            recommendations = self.recommendation_engine.generate_recommendations(
                patterns, preferences, trajectory
            )

            signature = {
                "patterns": patterns,
                "preferences": preferences,
                "trajectory": trajectory,
                "recommendations": recommendations,
                "generated_at": self._get_timestamp(),
            }

            logger.info("Development Signature generated successfully")
            return signature

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate Development Signature: {e}", exc_info=True)
            raise

    def _get_timestamp(self) -> str:
        """Get current timestamp.

        Returns:
            ISO format timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

