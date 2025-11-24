"""AgentCore integration for Development Signature.

Handles calls to deployed AgentCore agent for intelligent pattern detection and analysis.
Manages prompts, responses, and error handling.
"""

import json
import logging
import subprocess
from typing import Dict, List, Any, Optional
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class AgentCoreIntegrationError(JanusException):
    """Error during AgentCore integration."""
    pass


class AgentCoreCaller:
    """Calls deployed AgentCore agent for intelligent analysis."""

    def __init__(self, client=None):
        """Initialize AgentCore caller.

        Args:
            client: Optional AgentCore client (for testing/mocking)
        """
        self.client = client or self._get_agentcore_client()
        logger.debug(f"AgentCoreCaller initialized with client type: {type(self.client).__name__}")

    def _get_agentcore_client(self):
        """Get AgentCore client - uses deployed agent via agentcore CLI or mock.

        Tries to use the actual deployed agent first, falls back to mock if unavailable.
        """
        try:
            # Check if agentcore CLI is available and agent is running
            result = subprocess.run(
                ["agentcore", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                logger.info("AgentCore CLI is available and agent is ready")
                client = RealAgentCoreClient()
                logger.info("Real AgentCore client initialized successfully")
                return client
            else:
                logger.warning(f"AgentCore status check failed: {result.stderr}, using mock client")
                return MockAgentCoreClient()

        except FileNotFoundError:
            logger.warning("AgentCore CLI not found in PATH, using mock client")
            return MockAgentCoreClient()
        except subprocess.TimeoutExpired:
            logger.warning("AgentCore status check timed out, using mock client")
            return MockAgentCoreClient()
        except Exception as e:
            logger.warning(f"Failed to initialize real AgentCore client: {e}, using mock")
            return MockAgentCoreClient()

    def detect_patterns(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to detect patterns and generate recommendations.

        Args:
            projects: List of project dictionaries

        Returns:
            Pattern detection results with patterns array and recommendations

        Raises:
            AgentCoreIntegrationError: If call fails
        """
        try:
            logger.debug(f"Calling AgentCore to detect patterns for {len(projects)} projects")

            payload = {
                "prompt": "Detect development patterns across these projects and provide career guidance",
                "projects": projects
            }

            # Call AgentCore (real or mock)
            response = self.client.analyze(payload)
            logger.debug("Received AgentCore response")

            # Parse and validate response
            result = self._parse_response(response)
            return result

        except Exception as e:
            logger.error(f"AgentCore pattern detection failed: {e}", exc_info=True)
            raise AgentCoreIntegrationError(f"Pattern detection failed: {e}")

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse response from AgentCore.

        Args:
            response: Response from AgentCore (could be dict or string)

        Returns:
            Parsed response as dictionary

        Raises:
            AgentCoreIntegrationError: If parsing fails
        """
        try:
            # If already a dict, return it
            if isinstance(response, dict):
                return response

            # If string, try to parse as JSON
            if isinstance(response, str):
                return json.loads(response)

            # Otherwise, convert to string first
            response_str = str(response)
            return json.loads(response_str)

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse response: {e}")
            raise AgentCoreIntegrationError(f"Could not parse response: {e}")


class RealAgentCoreClient:
    """Real AgentCore client using deployed agent via agentcore CLI."""

    def __init__(self):
        """Initialize with deployed AgentCore agent."""
        try:
            # Get agent status to verify it's running
            result = subprocess.run(
                ["agentcore", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("AgentCore agent is ready and responsive")
            else:
                logger.warning(f"AgentCore status check returned: {result.stderr}")

        except Exception as e:
            logger.warning(f"Could not verify AgentCore status: {e}")

    def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call deployed AgentCore agent for analysis.

        Args:
            payload: Payload dict with prompt and projects

        Returns:
            Response from agent

        Raises:
            Exception: If invocation fails
        """
        try:
            logger.info("Invoking AgentCore agent via CLI")

            # Invoke agent via agentcore CLI
            payload_json = json.dumps(payload)
            result = subprocess.run(
                ["agentcore", "invoke", payload_json],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"AgentCore invocation failed: {result.stderr}")
                raise Exception(f"AgentCore CLI returned error: {result.stderr}")

            # Parse output - agentcore CLI returns JSON in Response: field
            output = result.stdout
            logger.debug(f"AgentCore raw output: {output[:200]}...")

            # Extract JSON from output (it's usually in "Response:" section)
            if "Response:" in output:
                json_start = output.find("{")
                if json_start != -1:
                    json_str = output[json_start:]
                    # Find the matching closing brace
                    brace_count = 0
                    for i, char in enumerate(json_str):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                json_str = json_str[:i+1]
                                break
                    response = json.loads(json_str)
                    logger.info(f"Successfully parsed AgentCore response with {len(response.get('patterns', []))} patterns")
                    return response

            # If we can't parse, return the raw output as fallback
            logger.warning("Could not parse structured response, returning raw output")
            return {"status": "success", "raw_output": output}

        except Exception as e:
            logger.error(f"AgentCore Runtime CLI call failed: {e}", exc_info=True)
            raise


class MockAgentCoreClient:
    """Mock AgentCore client for testing and graceful degradation."""

    def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock analysis response based on payload.

        Args:
            payload: Payload dict with prompt, projects, amazon_q_technologies, etc.

        Returns:
            Mock response with patterns and recommendations that reference Amazon Q data
        """
        logger.debug("Using mock AgentCore client")

        projects = payload.get("projects", [])
        amazon_q_technologies = payload.get("amazon_q_technologies", {})
        detected_patterns = payload.get("detected_patterns", [])
        prompt = payload.get("prompt", "")

        logger.debug(f"Mock analysis: {len(projects)} projects, {len(amazon_q_technologies)} AWS Q techs")

        # Generate patterns (use provided ones or generate)
        patterns = detected_patterns if detected_patterns else self._generate_patterns(projects)

        # Generate recommendations that reference Amazon Q technologies
        recommendations = self._generate_recommendations(
            patterns,
            amazon_q_technologies,
            projects
        )

        # Generate trajectory analysis
        trajectory = self._generate_trajectory(projects)

        result = {
            "status": "success",
            "projects_analyzed": len(projects),
            "patterns": patterns,
            "recommendations": recommendations,
            "trajectory": trajectory,
            "preferences": {
                "description": "Based on your project patterns and choices, you prefer building stateless, concurrent systems with cloud-first architecture.",
                "traits": ["Stateless Design", "Async-First", "Cloud-Native", "Concurrent Systems"]
            },
            "metrics": {
                "average_complexity": sum(p.get("complexity_score", 0) for p in projects) / max(len(projects), 1) if projects else 0,
                "pattern_count": len(patterns),
                "amazon_q_technologies_used": len(amazon_q_technologies),
            }
        }

        logger.debug(f"Mock response: {len(patterns)} patterns, {len(recommendations)} recommendations")
        return result

    def _generate_trajectory(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate learning trajectory based on projects.

        Args:
            projects: List of projects

        Returns:
            Trajectory analysis
        """
        if not projects:
            return {
                "current_level": "Beginner",
                "growth_velocity": "Steady",
                "next_milestone": "First Project"
            }

        complexities = [p.get("complexity_score", 0) for p in projects]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0

        if avg_complexity < 5:
            level = "Beginner"
        elif avg_complexity < 7:
            level = "Intermediate"
        elif avg_complexity < 8.5:
            level = "Advanced"
        else:
            level = "Expert"

        growth = 0
        if len(complexities) > 1:
            growth = complexities[-1] - complexities[0]

        if growth > 2:
            velocity = "Accelerating"
        elif growth > 0:
            velocity = "Steady"
        else:
            velocity = "Stable"

        # Next milestone based on current level
        milestones = {
            "Beginner": "Intermediate (5.0+ complexity)",
            "Intermediate": "Advanced (7.0+ complexity)",
            "Advanced": "Expert (8.5+ complexity)",
            "Expert": "Technical Leadership"
        }

        return {
            "current_level": level,
            "growth_velocity": velocity,
            "next_milestone": milestones.get(level, "Mastery")
        }

    def _generate_patterns(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic patterns based on project data.

        Args:
            projects: List of projects

        Returns:
            List of detected patterns
        """
        patterns = []

        if not projects:
            return patterns

        # Pattern 1: Check database usage
        db_count = sum(1 for p in projects if any(
            s.lower() in ['sql', 'database', 'postgres', 'mongodb']
            for s in p.get('skills', [])
        ))
        if db_count < len(projects) * 0.3:
            patterns.append({
                "name": "State Simplicity Preference",
                "evidence": [f"{db_count}/{len(projects)} projects use databases"],
                "confidence": 0.90,
                "impact": "Prefers simple state management"
            })

        # Pattern 2: Check async usage
        async_count = sum(1 for p in projects if any(
            s.lower() in ['async', 'asyncio', 'threading', 'concurrency']
            for s in p.get('skills', [])
        ))
        if async_count >= len(projects) * 0.5:
            patterns.append({
                "name": "Async-First Development",
                "evidence": [f"{async_count}/{len(projects)} projects use async"],
                "confidence": 0.85,
                "impact": "Builds with concurrency from day 1"
            })

        # Pattern 3: Check complexity trajectory
        avg_complexity = sum(p.get('complexity_score', 0) for p in projects) / len(projects) if projects else 0
        if avg_complexity > 7.0:
            patterns.append({
                "name": "High Complexity Tolerance",
                "evidence": [f"Average complexity: {avg_complexity:.1f}/10"],
                "confidence": 0.88,
                "impact": "Comfortable with sophisticated architectures"
            })

        return patterns

    def _generate_recommendations(
        self,
        patterns: List[Dict[str, Any]],
        amazon_q_technologies: Dict[str, int],
        projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations that reference Amazon Q technologies.

        Args:
            patterns: Detected patterns
            amazon_q_technologies: Technologies from Amazon Q
            projects: List of projects

        Returns:
            List of recommendations
        """
        recommendations = []
        pattern_names = {p['name'] for p in patterns}

        # Build recommendations that reference Amazon Q technologies

        if "Async-First Development" in pattern_names:
            # Check if they use AWS from Amazon Q
            aws_usage = amazon_q_technologies.get("AWS", 0) + amazon_q_technologies.get("AWS Bedrock", 0)
            if aws_usage > 0:
                recommendations.append({
                    "title": "Ready for Event-Driven Architecture",
                    "description": "Your async-first approach combined with AWS usage makes you ready for event-driven systems.",
                    "status": "ready",
                    "why": f"You use async patterns (confirmed by analysis) + AWS technologies (detected by Amazon Q in {aws_usage} projects)",
                    "timeline": "Now",
                    "technologies": ["AWS EventBridge", "SQS", "SNS"]
                })

        if "State Simplicity Preference" in pattern_names:
            recommendations.append({
                "title": "SQLite → PostgreSQL Path",
                "description": "When you need persistence, start with SQLite for simplicity, then graduate to PostgreSQL.",
                "status": "ready",
                "why": "Your stateless preference shows you prioritize simplicity. SQLite matches this philosophy before moving to PostgreSQL.",
                "timeline": "2-3 weeks",
                "technologies": ["SQLite", "asyncpg", "PostgreSQL"]
            })

        # Check AWS usage from Amazon Q for general recommendations
        if amazon_q_technologies.get("AWS Bedrock", 0) > 0:
            recommendations.append({
                "title": "Explore Advanced AWS Services",
                "description": "You're already using AWS Bedrock. Expand to Step Functions, AppSync, or EventBridge.",
                "status": "explore",
                "why": "Amazon Q detected Bedrock usage. You're ready for more sophisticated AWS patterns.",
                "timeline": "3-4 weeks",
                "technologies": ["Step Functions", "AppSync", "EventBridge"]
            })

        # Default recommendations if nothing else
        if not recommendations:
            recommendations.append({
                "title": "Keep Building",
                "description": "Continue shipping projects that push you slightly outside your comfort zone.",
                "status": "explore",
                "why": "Consistent building is the fastest way to grow.",
                "timeline": "Ongoing",
                "technologies": []
            })

        return recommendations
