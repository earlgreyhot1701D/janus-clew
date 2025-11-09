"""Trajectory analyzer for Development Signature.

Calculates learning velocity, growth rates, and projections.
All calculations based on complexity scores over time.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class TrajectoryAnalyzerError(JanusException):
    """Error during trajectory analysis."""
    pass


class TrajectoryAnalyzer:
    """Analyzes learning trajectory and growth metrics."""

    def analyze_trajectory(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning trajectory across analyses.
        
        Args:
            analyses: List of analysis dictionaries sorted by date
            
        Returns:
            Dictionary with trajectory metrics
            
        Raises:
            TrajectoryAnalyzerError: If insufficient data
        """
        if not analyses or len(analyses) < 2:
            raise TrajectoryAnalyzerError("Need at least 2 analyses to calculate trajectory")
        
        logger.debug(f"Analyzing trajectory across {len(analyses)} analyses")
        
        try:
            # Extract complexity scores in chronological order
            complexities = self._extract_complexities(analyses)
            
            if len(complexities) < 2:
                raise TrajectoryAnalyzerError("Need at least 2 complexity scores")
            
            # Calculate metrics
            growth_rate = complexities[-1] / complexities[0] if complexities[0] > 0 else 0
            weeks_elapsed = self._calculate_weeks_elapsed(analyses)
            learning_velocity = self._calculate_velocity(complexities, weeks_elapsed)
            projection = self._project_forward(complexities[-1], learning_velocity, weeks=4)
            trend = self._detect_trend(complexities)
            
            return {
                "growth_rate": round(growth_rate, 2),
                "weeks_elapsed": weeks_elapsed,
                "learning_velocity": round(learning_velocity, 3),
                "projected_4_weeks": round(projection, 2),
                "trend": trend,
                "complexity_evolution": [round(c, 1) for c in complexities],
                "interpretation": self._interpret_trajectory(growth_rate, learning_velocity, trend)
            }
        except Exception as e:
            logger.error(f"Trajectory analysis failed: {e}")
            raise TrajectoryAnalyzerError(f"Failed to analyze trajectory: {e}")

    def _extract_complexities(self, analyses: List[Dict[str, Any]]) -> List[float]:
        """Extract average complexity from each analysis.
        
        Args:
            analyses: List of analyses
            
        Returns:
            List of average complexities in order
        """
        complexities = []
        
        for analysis in analyses:
            if "overall" in analysis and "avg_complexity" in analysis["overall"]:
                complexities.append(analysis["overall"]["avg_complexity"])
            elif "projects" in analysis:
                scores = [p.get("complexity_score", 0) for p in analysis["projects"]]
                if scores:
                    avg = sum(scores) / len(scores)
                    complexities.append(avg)
        
        return complexities

    def _calculate_weeks_elapsed(self, analyses: List[Dict[str, Any]]) -> int:
        """Calculate weeks between first and last analysis.
        
        Args:
            analyses: List of analyses (assumes sorted by date)
            
        Returns:
            Number of weeks elapsed (minimum 1)
        """
        if len(analyses) < 2:
            return 1
        
        try:
            first_date = self._parse_timestamp(analyses[0].get("timestamp", ""))
            last_date = self._parse_timestamp(analyses[-1].get("timestamp", ""))
            
            if first_date and last_date:
                days = (last_date - first_date).days
                weeks = max(1, days // 7)
                return weeks
        except Exception as e:
            logger.debug(f"Could not parse dates: {e}")
        
        return 1  # Minimum 1 week

    def _parse_timestamp(self, timestamp: str) -> Optional[datetime]:
        """Parse various timestamp formats.
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not timestamp:
            return None
        
        formats = [
            "%Y-%m-%d_%H-%M-%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        
        return None

    def _calculate_velocity(self, complexities: List[float], weeks: int) -> float:
        """Calculate learning velocity (complexity gain per week).
        
        Args:
            complexities: List of complexity scores
            weeks: Weeks elapsed
            
        Returns:
            Complexity points gained per week
        """
        if weeks <= 0:
            return 0
        
        total_gain = complexities[-1] - complexities[0]
        return total_gain / weeks

    def _project_forward(self, current: float, velocity: float, weeks: int = 4) -> float:
        """Project complexity forward.
        
        Args:
            current: Current complexity
            velocity: Complexity gain per week
            weeks: Weeks to project (default 4)
            
        Returns:
            Projected complexity (capped at 10.0)
        """
        projected = current + (velocity * weeks)
        return min(10.0, max(0.0, projected))

    def _detect_trend(self, complexities: List[float]) -> str:
        """Detect trend in complexity growth.
        
        Args:
            complexities: List of complexity scores
            
        Returns:
            "accelerating", "steady", or "decelerating"
        """
        if len(complexities) < 3:
            return "insufficient_data"
        
        # Calculate growth rates for each period
        growth_rates = []
        for i in range(1, len(complexities)):
            prev = complexities[i - 1]
            curr = complexities[i]
            if prev > 0:
                growth = (curr - prev) / prev
                growth_rates.append(growth)
        
        if not growth_rates:
            return "steady"
        
        avg_growth = sum(growth_rates) / len(growth_rates)
        latest_growth = growth_rates[-1]
        
        # Threshold: 25% difference between latest and average
        if latest_growth > avg_growth * 1.25:
            return "accelerating"
        elif latest_growth < avg_growth * 0.75:
            return "decelerating"
        else:
            return "steady"

    def _interpret_trajectory(self, growth_rate: float, velocity: float, trend: str) -> str:
        """Create human-readable interpretation of trajectory.
        
        Args:
            growth_rate: Overall growth multiplier
            velocity: Learning velocity per week
            trend: Detected trend
            
        Returns:
            Interpretation string
        """
        if growth_rate < 1.5:
            return "Steady learning at a measured pace"
        elif growth_rate < 2.0:
            return "Strong growth with consistent learning"
        elif trend == "accelerating":
            return "Rapid learning with accelerating complexity gains"
        else:
            return "Significant growth - you're taking on increasingly complex projects"
