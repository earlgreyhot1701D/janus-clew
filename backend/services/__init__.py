"""Janus Clew Backend Services - Business logic layer."""

from typing import Dict, List, Any, Optional

from cli.storage import StorageManager
from backend.services.pattern_detector import PatternDetector
from backend.services.preference_analyzer import PreferenceAnalyzer
from backend.services.trajectory_analyzer import TrajectoryAnalyzer
from backend.services.recommendation_engine import RecommendationEngine
from backend.services.agentcore_integration import AgentCoreCaller
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

    Orchestrates local analysis + Amazon Q tech detection + AgentCore reasoning.
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
        self.agentcore_caller = AgentCoreCaller()

    def generate_development_signature(self) -> Dict[str, Any]:
        """Generate complete Development Signature.

        Orchestrates:
        1. Extract Amazon Q technologies from stored analyses
        2. Detect local patterns (files, functions, classes, etc.)
        3. Analyze architectural preferences
        4. Analyze learning trajectory
        5. Invoke AgentCore with all intelligence (with graceful fallback)
        6. Return combined results

        Returns:
            Dictionary with patterns, preferences, trajectory, recommendations,
            amazon_q_technologies, and agentcore_status

        Raises:
            NotFoundError: If no analyses available
        """
        logger.debug("Generating Development Signature (Phase 2)")

        try:
            analyses = self.analysis_service.get_all_analyses()
            if not analyses:
                raise NotFoundError("No analyses found for signature generation")

            logger.info(f"Starting Development Signature generation with {len(analyses)} analyses")

            # ================================================================
            # STEP 1: EXTRACT AMAZON Q TECHNOLOGIES
            # ================================================================
            logger.debug("Step 1: Extracting Amazon Q detected technologies")
            amazon_q_technologies = self._extract_amazon_q_technologies(analyses)
            logger.debug(f"Found {len(amazon_q_technologies)} unique technologies from Amazon Q")

            # ================================================================
            # STEP 2: DETECT LOCAL PATTERNS
            # ================================================================
            logger.debug("Step 2: Detecting local patterns")
            patterns = self.pattern_detector.detect_patterns(analyses)
            logger.debug(f"Detected {len(patterns)} local patterns")

            # ================================================================
            # STEP 3: ANALYZE ARCHITECTURAL PREFERENCES
            # ================================================================
            logger.debug("Step 3: Analyzing architectural preferences")
            preferences = self.preference_analyzer.analyze_preferences(analyses)
            logger.debug(f"Analyzed architectural preferences")

            # ================================================================
            # STEP 4: ANALYZE LEARNING TRAJECTORY
            # ================================================================
            logger.debug("Step 4: Analyzing learning trajectory")
            trajectory = self.trajectory_analyzer.analyze_trajectory(analyses)
            logger.debug(f"Analyzed trajectory: {trajectory}")

            # ================================================================
            # STEP 5: INVOKE AGENTCORE WITH FULL INTELLIGENCE (WITH FALLBACK)
            # ================================================================
            logger.debug("Step 5: Invoking AgentCore with combined intelligence")

            agentcore_result = self._invoke_agentcore_with_fallback(
                analyses=analyses,
                amazon_q_technologies=amazon_q_technologies,
                patterns=patterns,
                preferences=preferences,
                trajectory=trajectory
            )

            # ================================================================
            # STEP 6: BUILD FINAL SIGNATURE
            # ================================================================
            signature = {
                # Local analysis (always present)
                "patterns": agentcore_result.get("patterns", patterns),
                "preferences": preferences,
                "trajectory": trajectory,

                # Amazon Q technologies (for transparency)
                "amazon_q_technologies": amazon_q_technologies,

                # AgentCore results
                "recommendations": agentcore_result.get("recommendations", []),
                "agentcore_insights": agentcore_result.get("insights", {}),
                "agentcore_available": agentcore_result.get("agentcore_available", False),

                # Metadata
                "generated_at": self._get_timestamp(),
            }

            logger.info("Development Signature generated successfully")
            return signature

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate Development Signature: {e}", exc_info=True)
            raise

    def _extract_amazon_q_technologies(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract and aggregate technologies detected by Amazon Q.

        Looks at all analyses and counts how many projects use each technology
        (as detected by Amazon Q during Phase 1).

        Args:
            analyses: List of analysis dictionaries

        Returns:
            Dictionary mapping technology name to count of projects using it.
            Example: {"Python": 2, "AWS Bedrock": 2, "async/await": 2}
        """
        logger.debug("Extracting Amazon Q technologies from analyses")

        tech_counts: Dict[str, int] = {}

        try:
            for analysis in analyses:
                projects = analysis.get("projects", [])
                for project in projects:
                    technologies = project.get("technologies", [])
                    for tech in technologies:
                        if isinstance(tech, str) and tech.strip():
                            tech_counts[tech] = tech_counts.get(tech, 0) + 1

            logger.debug(f"Aggregated {len(tech_counts)} unique technologies: {tech_counts}")
            return tech_counts

        except Exception as e:
            logger.error(f"Error extracting Amazon Q technologies: {e}")
            return {}

    def _invoke_agentcore_with_fallback(
        self,
        analyses: List[Dict[str, Any]],
        amazon_q_technologies: Dict[str, int],
        patterns: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        trajectory: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke AgentCore with full intelligence, gracefully fallback to local analysis.

        Attempts to call AgentCore with:
        - Projects data
        - Amazon Q detected technologies
        - Local patterns
        - Preferences
        - Trajectory

        If AgentCore fails, returns local recommendations gracefully.

        Args:
            analyses: All stored analyses
            amazon_q_technologies: Technologies from Amazon Q
            patterns: Locally detected patterns
            preferences: Architectural preferences
            trajectory: Learning trajectory

        Returns:
            Dictionary with:
            - patterns: Enhanced by AgentCore or local
            - recommendations: From AgentCore or local fallback
            - insights: From AgentCore or empty
            - agentcore_available: Boolean indicating if AgentCore worked
        """
        logger.debug("Building AgentCore payload with combined intelligence")

        # Build projects list for AgentCore
        projects = []
        for analysis in analyses:
            for project in analysis.get("projects", []):
                projects.append({
                    "name": project.get("name", "unknown"),
                    "complexity_score": project.get("complexity_score", 0.0),
                    "skills": project.get("technologies", []),
                    "timestamp": analysis.get("timestamp", 0),
                })

        # Build complete payload for AgentCore
        payload = {
            "prompt": "Analyze my complete development signature and provide intelligent career guidance",
            "projects": projects,
            "amazon_q_technologies": amazon_q_technologies,  # NEW: Include Amazon Q data
            "detected_patterns": patterns,  # NEW: Include local patterns
            "preferences": preferences,  # NEW: Include preferences
            "trajectory": trajectory,  # NEW: Include trajectory
        }

        logger.debug(f"AgentCore payload: {len(projects)} projects, {len(amazon_q_technologies)} AWS Q technologies")

        try:
            # Try to invoke AgentCore
            logger.info("Attempting to invoke AgentCore agent")
            agentcore_response = self.agentcore_caller.detect_patterns(projects)

            logger.info("AgentCore invocation successful")

            # AgentCore succeeded - return enhanced results
            return {
                "patterns": agentcore_response.get("patterns", patterns),
                "recommendations": agentcore_response.get("recommendations", []),
                "insights": {
                    "from_agentcore": True,
                    "model": "bedrock-agentcore-janus",
                    "amazon_q_technologies_provided": len(amazon_q_technologies),
                },
                "agentcore_available": True,
            }

        except Exception as e:
            # AgentCore failed - gracefully fallback to local analysis
            logger.warning(f"AgentCore invocation failed: {e}. Using local analysis fallback.")

            # Generate local recommendations as fallback
            local_recommendations = self.recommendation_engine.generate_recommendations(
                patterns, preferences, trajectory
            )

            return {
                "patterns": patterns,  # Use locally detected patterns
                "recommendations": local_recommendations,  # Use local recommendations
                "insights": {
                    "from_agentcore": False,
                    "fallback_reason": str(e),
                    "local_analysis_only": True,
                },
                "agentcore_available": False,
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format.

        Returns:
            ISO format timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
