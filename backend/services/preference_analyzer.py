"""Preference analyzer for Development Signature.

Detects architectural preferences (state management, async comfort, etc).
Uses deterministic analysis + AgentCore reasoning.
"""

from typing import Dict, List, Any
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class PreferenceAnalyzerError(JanusException):
    """Error during preference analysis."""
    pass


class PreferenceAnalyzer:
    """Detects architectural preferences from code patterns."""

    # Technology indicators
    STATE_HEAVY_TECHS = {"PostgreSQL", "MySQL", "MongoDB", "DynamoDB", "Redis"}
    STATE_LIGHT_TECHS = {"Lambda", "Serverless", "In-Memory"}
    ASYNC_TECHS = {"AsyncIO", "async/await", "Promise", "RxJS", "Tokio", "Goroutines"}
    COMPLEX_FRAMEWORKS = {"Kubernetes", "Microservices", "Event-Driven", "GraphQL"}
    SIMPLE_FRAMEWORKS = {"Flask", "Django", "FastAPI"}

    def analyze_preferences(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze architectural preferences from all projects.
        
        Args:
            analyses: List of analysis dictionaries
            
        Returns:
            Dictionary with preference scores and evidence
            
        Raises:
            PreferenceAnalyzerError: If analysis fails
        """
        if not analyses:
            raise PreferenceAnalyzerError("No analyses provided")
        
        logger.debug(f"Analyzing preferences across {len(analyses)} analyses")
        
        try:
            # Collect all technologies
            all_techs = set()
            for analysis in analyses:
                for project in analysis.get("projects", []):
                    all_techs.update(project.get("technologies", []))
            
            # Calculate preference scores
            preferences = []
            
            # Preference 1: State Simplicity
            state_score = self._calculate_state_preference(all_techs)
            preferences.append({
                "name": "State Simplicity",
                "score": state_score,
                "description": self._describe_state_preference(state_score, all_techs)
            })
            
            # Preference 2: Async/Concurrency Comfort
            async_score = self._calculate_async_preference(analyses)
            preferences.append({
                "name": "Async/Concurrency Comfort",
                "score": async_score,
                "description": self._describe_async_preference(async_score, all_techs)
            })
            
            # Preference 3: Complexity Tolerance
            complexity_score = self._calculate_complexity_tolerance(analyses)
            preferences.append({
                "name": "Complexity Tolerance",
                "score": complexity_score,
                "description": self._describe_complexity_preference(complexity_score)
            })
            
            # Preference 4: Code Organization
            organization_score = self._calculate_organization_preference(analyses)
            preferences.append({
                "name": "Code Organization",
                "score": organization_score,
                "description": self._describe_organization_preference(organization_score)
            })
            
            # Preference 5: Framework Diversity
            diversity_score = self._calculate_framework_diversity(all_techs)
            preferences.append({
                "name": "Framework Diversity",
                "score": diversity_score,
                "description": self._describe_diversity_preference(diversity_score, all_techs)
            })
            
            logger.info(f"Analyzed {len(preferences)} preferences")
            return {"preferences": preferences}
            
        except Exception as e:
            logger.error(f"Preference analysis failed: {e}")
            raise PreferenceAnalyzerError(f"Failed to analyze preferences: {e}")

    def _calculate_state_preference(self, technologies: set) -> float:
        """Calculate state simplicity preference (0-1).
        
        Args:
            technologies: Set of all technologies used
            
        Returns:
            Score 0-1 (1 = prefers simple state)
        """
        state_heavy = len(technologies & self.STATE_HEAVY_TECHS)
        state_light = len(technologies & self.STATE_LIGHT_TECHS)
        
        if state_heavy == 0 and state_light > 0:
            return 0.95  # Strongly prefers simple state
        elif state_heavy == 0:
            return 0.90  # Avoids databases
        elif state_light > state_heavy:
            return 0.70  # Prefers simple but uses some complex state
        else:
            return 0.40  # Comfortable with state-heavy architectures

    def _calculate_async_preference(self, analyses: List[Dict[str, Any]]) -> float:
        """Calculate async/concurrency comfort (0-1).
        
        Args:
            analyses: List of analyses
            
        Returns:
            Score 0-1 (1 = very comfortable with async)
        """
        total_projects = 0
        async_projects = 0
        
        for analysis in analyses:
            for project in analysis.get("projects", []):
                total_projects += 1
                techs = project.get("technologies", [])
                if any(tech in techs for tech in self.ASYNC_TECHS):
                    async_projects += 1
        
        if total_projects == 0:
            return 0.5
        
        ratio = async_projects / total_projects
        return min(1.0, ratio * 1.1)  # Slightly boost async projects

    def _calculate_complexity_tolerance(self, analyses: List[Dict[str, Any]]) -> float:
        """Calculate complexity tolerance (0-1).
        
        Args:
            analyses: List of analyses
            
        Returns:
            Score 0-1 based on average complexity
        """
        complexities = []
        for analysis in analyses:
            for project in analysis.get("projects", []):
                complexities.append(project.get("complexity_score", 0))
        
        if not complexities:
            return 0.5
        
        avg = sum(complexities) / len(complexities)
        return min(1.0, avg / 10.0)  # 8.1/10 → 0.81

    def _calculate_organization_preference(self, analyses: List[Dict[str, Any]]) -> float:
        """Calculate code organization score (0-1).
        
        Args:
            analyses: List of analyses
            
        Returns:
            Score 0-1 (based on project structure hints)
        """
        # Simple heuristic: multiple projects with good complexity scores
        # suggests organized code
        good_projects = 0
        total_projects = 0
        
        for analysis in analyses:
            for project in analysis.get("projects", []):
                total_projects += 1
                if project.get("complexity_score", 0) >= 6.0:
                    good_projects += 1
        
        if total_projects == 0:
            return 0.5
        
        return min(1.0, good_projects / total_projects * 1.2)

    def _calculate_framework_diversity(self, technologies: set) -> float:
        """Calculate framework diversity (0-1).
        
        Args:
            technologies: Set of all technologies
            
        Returns:
            Score 0-1 (1 = uses many different frameworks)
        """
        # More technologies = higher diversity
        diversity_score = min(1.0, len(technologies) / 8.0)
        return round(diversity_score, 2)

    def _describe_state_preference(self, score: float, technologies: set) -> str:
        """Describe state management preference."""
        if score > 0.85:
            return "You consistently avoid databases and prefer stateless, in-memory solutions"
        elif score > 0.70:
            return "You prefer simple state management but are willing to use databases when needed"
        else:
            return "You're comfortable with stateful, database-driven architectures"

    def _describe_async_preference(self, score: float, technologies: set) -> str:
        """Describe async/concurrency preference."""
        if score > 0.85:
            return "You're very comfortable with async patterns and use them across projects"
        elif score > 0.60:
            return "You use async patterns when beneficial and understand concurrency"
        else:
            return "You prefer synchronous, straightforward code structures"

    def _describe_complexity_preference(self, score: float) -> str:
        """Describe complexity tolerance."""
        if score > 0.80:
            return "You're very comfortable with sophisticated architectures and high complexity"
        elif score > 0.60:
            return "You handle moderate complexity and can design well-structured systems"
        else:
            return "You prefer simple, straightforward designs"

    def _describe_organization_preference(self, score: float) -> str:
        """Describe code organization preference."""
        if score > 0.80:
            return "Your code is well-organized and modular across projects"
        elif score > 0.60:
            return "You maintain reasonable organization in your code"
        else:
            return "Your focus is on functionality over organization"

    def _describe_diversity_preference(self, score: float, technologies: set) -> str:
        """Describe framework diversity preference."""
        tech_count = len(technologies)
        if tech_count >= 8:
            return f"You're a generalist, using {tech_count} different technologies"
        elif tech_count >= 5:
            return f"You use diverse technologies ({tech_count}), suggesting breadth of learning"
        else:
            return f"You focus on specific technologies ({tech_count}), going deep rather than wide"
