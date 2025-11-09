"""Pattern detection service for Development Signature.

Detects cross-project patterns without hardcoded rules.
AgentCore does the reasoning; this service orchestrates the analysis.
"""

from typing import Dict, List, Any, Optional
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class PatternDetectorError(JanusException):
    """Error during pattern detection."""
    pass


class PatternDetector:
    """Detects behavioral patterns across projects."""

    def __init__(self, agentcore_client=None):
        """Initialize pattern detector.
        
        Args:
            agentcore_client: Optional AgentCore client (injected for testing)
        """
        self.agentcore_client = agentcore_client

    def detect_patterns(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns across all projects.
        
        Args:
            analyses: List of analysis dictionaries from storage
            
        Returns:
            Dictionary with detected patterns and confidence scores
            
        Raises:
            PatternDetectorError: If pattern detection fails
        """
        if not analyses:
            raise PatternDetectorError("No analyses provided for pattern detection")
        
        logger.debug(f"Detecting patterns across {len(analyses)} analyses")
        
        try:
            # Call AgentCore to do the actual analysis
            patterns = self._extract_patterns_with_agentcore(analyses)
            logger.info(f"Detected {len(patterns.get('patterns', []))} patterns")
            return patterns
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            # Return sensible defaults if AgentCore fails
            return self._fallback_pattern_detection(analyses)

    def _extract_patterns_with_agentcore(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to extract patterns.
        
        Args:
            analyses: List of analyses
            
        Returns:
            Patterns from AgentCore
        """
        from backend.services.agentcore_integration import AgentCoreCaller
        
        caller = AgentCoreCaller(client=self.agentcore_client)
        return caller.detect_patterns(analyses)

    def _fallback_pattern_detection(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback pattern detection if AgentCore unavailable.
        
        Performs basic pattern detection without external calls.
        Used for testing and graceful degradation.
        
        Args:
            analyses: List of analyses
            
        Returns:
            Basic patterns detected
        """
        logger.warning("Using fallback pattern detection")
        
        # Collect all data
        all_projects = []
        all_technologies = set()
        complexities = []
        
        for analysis in analyses:
            for project in analysis.get("projects", []):
                all_projects.append(project)
                complexities.append(project.get("complexity_score", 0))
                all_technologies.update(project.get("technologies", []))
        
        patterns = []
        
        # Pattern 1: Database usage
        db_projects = [
            p for p in all_projects 
            if any(db in p.get("technologies", []) 
                   for db in ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "DynamoDB"])
        ]
        if db_projects:
            patterns.append({
                "name": "Database Usage",
                "evidence": f"Used in {len(db_projects)}/{len(all_projects)} projects",
                "confidence": 0.95,
                "impact": "You're comfortable with persistent state management"
            })
        else:
            patterns.append({
                "name": "Database Avoidance",
                "evidence": f"0/{len(all_projects)} projects use SQL",
                "confidence": 0.98,
                "impact": "You prefer state simplicity and in-memory solutions"
            })
        
        # Pattern 2: Async patterns
        async_projects = [
            p for p in all_projects
            if any(framework in p.get("technologies", [])
                   for framework in ["AsyncIO", "async/await", "Promise", "RxJS"])
        ]
        if len(async_projects) >= 2:
            patterns.append({
                "name": "Async-First Thinking",
                "evidence": f"Async in {len(async_projects)}/{len(all_projects)} projects",
                "confidence": 0.87,
                "impact": "You build for concurrency and scale from day one"
            })
        
        # Pattern 3: Growth rate
        if len(complexities) >= 2 and complexities[0] > 0:
            growth_rate = complexities[-1] / complexities[0]
            if growth_rate > 2.0:
                patterns.append({
                    "name": "Rapid Learning",
                    "evidence": f"Complexity grew {growth_rate:.1f}x from {complexities[0]:.1f} to {complexities[-1]:.1f}",
                    "confidence": 0.92,
                    "impact": "You're learning quickly and taking on more complex projects"
                })
        
        # Pattern 4: Framework diversity
        if len(all_technologies) >= 4:
            patterns.append({
                "name": "Generalist Approach",
                "evidence": f"Used {len(all_technologies)} different technologies",
                "confidence": 0.85,
                "impact": "You're a generalist learner, comfortable with multiple stacks"
            })
        
        return {
            "patterns": patterns,
            "data_points": len(all_projects),
            "fallback": True
        }

    def validate_patterns(self, patterns: Dict[str, Any]) -> bool:
        """Validate pattern detection output.
        
        Args:
            patterns: Pattern detection result
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not isinstance(patterns, dict):
            raise PatternDetectorError("Patterns must be a dictionary")
        
        if "patterns" not in patterns:
            raise PatternDetectorError("Patterns missing 'patterns' key")
        
        patterns_list = patterns.get("patterns", [])
        if not isinstance(patterns_list, list):
            raise PatternDetectorError("Patterns must be a list")
        
        for pattern in patterns_list:
            required_keys = {"name", "evidence", "confidence"}
            if not required_keys.issubset(pattern.keys()):
                raise PatternDetectorError(f"Pattern missing required keys: {required_keys}")
            
            if not 0 <= pattern.get("confidence", 0) <= 1:
                raise PatternDetectorError(f"Confidence must be 0-1, got {pattern['confidence']}")
        
        logger.debug(f"Validated {len(patterns_list)} patterns")
        return True
