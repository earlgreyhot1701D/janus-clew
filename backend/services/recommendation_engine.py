"""Recommendation engine for Development Signature.

Generates forward-looking recommendations based on patterns and preferences.
Uses AgentCore for intelligent reasoning about readiness.
"""

from typing import Dict, List, Any
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class RecommendationEngineError(JanusException):
    """Error during recommendation generation."""
    pass


class RecommendationEngine:
    """Generates intelligent forward-looking recommendations."""

    def generate_recommendations(
        self,
        patterns: Dict[str, Any],
        preferences: Dict[str, Any],
        trajectory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate forward-looking recommendations.
        
        Args:
            patterns: Output from PatternDetector
            preferences: Output from PreferenceAnalyzer
            trajectory: Output from TrajectoryAnalyzer
            
        Returns:
            Dictionary with recommendations
            
        Raises:
            RecommendationEngineError: If generation fails
        """
        if not all([patterns, preferences, trajectory]):
            raise RecommendationEngineError("All inputs required for recommendations")
        
        logger.debug("Generating recommendations")
        
        try:
            recommendations = []
            
            # Rule 1: Async + No Databases = Ready for PostgreSQL
            if self._has_pattern(patterns, "async") and self._has_pattern(patterns, "database"):
                if self._get_pattern_impact(patterns, "database avoidance") or \
                   self._get_pattern_impact(patterns, "async-first"):
                    recommendations.append(self._create_recommendation(
                        skill="PostgreSQL + asyncpg",
                        status="ready",
                        confidence=0.92,
                        reasoning="You know async patterns and prefer state simplicity. PostgreSQL + asyncpg is the natural next step.",
                        evidence=[
                            "Async patterns: Detected in your projects",
                            "Database avoidance: Consistent across projects",
                            "Complexity comfort: You handle 8+/10"
                        ],
                        timeline="4-6 weeks",
                        next_action="Build one event-driven service with PostgreSQL"
                    ))
            
            # Rule 2: Fast Growth + Complexity = Ready for Event-Driven
            if trajectory.get("growth_rate", 1) > 2.0 and \
               trajectory.get("trend") in ["accelerating", "steady"]:
                recommendations.append(self._create_recommendation(
                    skill="Event-Driven Architecture (Kafka/RabbitMQ)",
                    status="ready_soon",
                    confidence=0.78,
                    reasoning="You're learning fast and comfortable with complexity. Event-driven is your natural next step.",
                    evidence=[
                        f"Growth rate: {trajectory.get('growth_rate', 1):.1f}x",
                        f"Trend: {trajectory.get('trend', 'steady')}",
                        "Multi-framework experience"
                    ],
                    timeline="6-8 weeks after PostgreSQL",
                    next_action="Study message queues, build Kafka service"
                ))
            
            # Rule 3: Solo Projects Only = Not Yet for Leadership
            recommendations.append(self._create_recommendation(
                skill="Team Leadership / Mentoring",
                status="not_yet",
                confidence=0.95,
                reasoning="Focus on solo shipping first. Build your track record. Leadership comes after mastery.",
                evidence=[
                    "All projects are solo-authored",
                    "Still building foundational skills",
                    "More proven projects needed first"
                ],
                timeline="After 3-4 shipped products",
                next_action="Keep shipping solo. Document your learning journey."
            ))
            
            # Rule 4: High Framework Diversity = Ready for Specialization
            if len(self._extract_technologies(patterns)) >= 5:
                recommendations.append(self._create_recommendation(
                    skill="AI/LLM Systems Specialization",
                    status="ready",
                    confidence=0.85,
                    reasoning="You've mastered multiple technologies. Consider specializing in AI systems.",
                    evidence=[
                        "Proven ability to learn new frameworks",
                        "Already using AWS Bedrock and AgentCore",
                        "Rapid growth trajectory"
                    ],
                    timeline="Ongoing",
                    next_action="Build AI agents, focus on AgentCore patterns"
                ))
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return {"recommendations": recommendations}
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise RecommendationEngineError(f"Failed to generate recommendations: {e}")

    def _create_recommendation(
        self,
        skill: str,
        status: str,
        confidence: float,
        reasoning: str,
        evidence: List[str],
        timeline: str,
        next_action: str
    ) -> Dict[str, Any]:
        """Create a recommendation dictionary.
        
        Args:
            skill: Technology/skill name
            status: "ready", "ready_soon", or "not_yet"
            confidence: Confidence 0-1
            reasoning: Why this recommendation
            evidence: List of evidence points
            timeline: Realistic timeline
            next_action: Specific next step
            
        Returns:
            Recommendation dictionary
        """
        return {
            "skill": skill,
            "status": status,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "evidence": evidence,
            "timeline": timeline,
            "next_action": next_action
        }

    def _has_pattern(self, patterns: Dict[str, Any], keyword: str) -> bool:
        """Check if pattern contains keyword.
        
        Args:
            patterns: Patterns dictionary
            keyword: Pattern keyword to search
            
        Returns:
            True if pattern found
        """
        for pattern in patterns.get("patterns", []):
            if keyword.lower() in pattern.get("name", "").lower():
                return True
        return False

    def _get_pattern_impact(self, patterns: Dict[str, Any], keyword: str) -> bool:
        """Get pattern with specific keyword.
        
        Args:
            patterns: Patterns dictionary
            keyword: Keyword to search for
            
        Returns:
            True if pattern found
        """
        for pattern in patterns.get("patterns", []):
            if keyword.lower() in pattern.get("name", "").lower():
                return bool(pattern.get("impact"))
        return False

    def _extract_technologies(self, patterns: Dict[str, Any]) -> set:
        """Extract technology mentions from patterns.
        
        Args:
            patterns: Patterns dictionary
            
        Returns:
            Set of technology names mentioned
        """
        techs = set()
        common_techs = {
            "PostgreSQL", "Python", "TypeScript", "JavaScript",
            "AWS", "Bedrock", "AgentCore", "LangChain",
            "React", "FastAPI", "Docker", "Kubernetes"
        }
        
        # Extract from pattern evidence
        for pattern in patterns.get("patterns", []):
            evidence = pattern.get("evidence", "")
            for tech in common_techs:
                if tech.lower() in evidence.lower():
                    techs.add(tech)
        
        return techs

    def validate_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """Validate recommendation output.
        
        Args:
            recommendations: Recommendations dictionary
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not isinstance(recommendations, dict):
            raise RecommendationEngineError("Recommendations must be a dictionary")
        
        if "recommendations" not in recommendations:
            raise RecommendationEngineError("Missing 'recommendations' key")
        
        recs_list = recommendations.get("recommendations", [])
        if not isinstance(recs_list, list):
            raise RecommendationEngineError("Recommendations must be a list")
        
        for rec in recs_list:
            required = {"skill", "status", "confidence", "reasoning"}
            if not required.issubset(rec.keys()):
                raise RecommendationEngineError(f"Recommendation missing keys: {required}")
            
            if rec["status"] not in ["ready", "ready_soon", "not_yet"]:
                raise RecommendationEngineError(f"Invalid status: {rec['status']}")
            
            if not 0 <= rec["confidence"] <= 1:
                raise RecommendationEngineError(f"Confidence must be 0-1: {rec['confidence']}")
        
        return True
