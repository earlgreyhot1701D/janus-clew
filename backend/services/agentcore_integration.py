"""AgentCore integration for Development Signature.

Handles calls to deployed AgentCore agent for intelligent pattern detection and analysis.
Manages prompts, responses, and error handling.
"""

import json
import yaml
from pathlib import Path
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
            client: Optional AgentCore client (for testing)
        """
        self.client = client or self._get_agentcore_client()

    def _get_agentcore_client(self):
        """Get AgentCore client - uses deployed agent via Bedrock AgentCore Runtime."""
        try:
            import boto3

            # Load agent ARN from config
            config_path = Path(__file__).parent.parent.parent / '.bedrock_agentcore.yaml'
            if not config_path.exists():
                logger.warning(f"AgentCore config not found at {config_path}, using mock")
                return MockAgentCoreClient()

            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            agent_arn = config.get('agents', {}).get('backend_agent', {}).get('bedrock_agentcore', {}).get('agent_arn')

            if not agent_arn:
                logger.warning("Agent ARN not found in config (not deployed yet), using mock")
                return MockAgentCoreClient()

            # Create bedrock-agentcore-runtime client
            client = boto3.client('bedrock-agentcore-runtime', region_name='us-east-1')
            logger.info(f"Initialized AgentCore Runtime client with agent: {agent_arn}")
            return RealAgentCoreClient(client, agent_arn)

        except Exception as e:
            logger.warning(f"AgentCore client init failed: {e}, using mock")
            return MockAgentCoreClient()

    def detect_patterns(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to detect patterns.

        Args:
            analyses: List of analysis dictionaries

        Returns:
            Pattern detection results with patterns array

        Raises:
            AgentCoreIntegrationError: If call fails
        """
        try:
            # Build payload for agent
            projects = []
            for analysis in analyses:
                project_data = {
                    'name': analysis.get('project_name', 'unknown'),
                    'complexity_score': analysis.get('complexity_score', 0.0),
                    'skills': analysis.get('detected_skills', []),
                    'timestamp': analysis.get('timestamp', 0),
                }
                projects.append(project_data)

            payload = {
                "prompt": "Detect development patterns across these projects",
                "projects": projects
            }

            # Call AgentCore
            response = self.client.analyze(payload)
            logger.debug("Received AgentCore pattern detection response")

            # Parse response
            result = self._parse_response(response)
            return result

        except Exception as e:
            logger.error(f"AgentCore pattern detection failed: {e}")
            raise AgentCoreIntegrationError(f"Pattern detection failed: {e}")

    def analyze_preferences(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to analyze preferences.

        Args:
            analyses: List of analyses

        Returns:
            Preference analysis results (currently returns patterns as preferences)
        """
        try:
            # For now, use pattern detection as preferences
            # The agent returns patterns which can be interpreted as preferences
            result = self.detect_patterns(analyses)

            # Transform patterns into preference format
            preferences = []
            for pattern in result.get('patterns', []):
                preference = {
                    'name': pattern['name'],
                    'score': pattern.get('confidence', 0.5),
                    'reasoning': pattern.get('impact', ''),
                    'evidence': pattern.get('evidence', '')
                }
                preferences.append(preference)

            return {'preferences': preferences}

        except Exception as e:
            logger.error(f"AgentCore preference analysis failed: {e}")
            raise AgentCoreIntegrationError(f"Preference analysis failed: {e}")

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
    """Real AgentCore client using deployed agent via Bedrock AgentCore Runtime."""

    def __init__(self, bedrock_client, agent_arn: str):
        """Initialize with Bedrock AgentCore Runtime client and agent ARN.

        Args:
            bedrock_client: boto3 bedrock-agentcore-runtime client
            agent_arn: ARN of deployed AgentCore agent
        """
        self.client = bedrock_client
        self.agent_arn = agent_arn

    def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call deployed AgentCore agent for analysis.

        Args:
            payload: Payload dict with prompt and projects

        Returns:
            Response from agent
        """
        try:
            logger.info(f"Invoking AgentCore agent: {self.agent_arn}")

            # Invoke agent via AgentCore Runtime API
            response = self.client.invoke_agent(
                agentArn=self.agent_arn,
                sessionId=f"session-{hash(str(payload)) % 100000}",  # Simple session ID
                input=json.dumps(payload)
            )

            # Parse response
            if 'output' in response:
                output = response['output']
                if isinstance(output, str):
                    return json.loads(output)
                return output
            elif 'body' in response:
                # Handle streaming response
                body = response['body'].read()
                return json.loads(body)
            else:
                logger.error(f"Unexpected response format: {response}")
                raise AgentCoreIntegrationError("Unexpected response format from agent")

        except Exception as e:
            logger.error(f"AgentCore Runtime API call failed: {e}", exc_info=True)
            # Gracefully fallback to mock
            logger.warning("Falling back to mock client")
            return MockAgentCoreClient().analyze(payload)


class MockAgentCoreClient:
    """Mock AgentCore client for testing and graceful degradation."""

    def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock analysis response based on payload.

        Args:
            payload: Payload dict with prompt and projects

        Returns:
            Mock response with patterns and recommendations
        """
        logger.debug("Using mock AgentCore client")

        projects = payload.get('projects', [])
        prompt = payload.get('prompt', '')

        # Generate basic patterns based on project data
        patterns = []

        if projects:
            # Check database usage
            db_count = sum(1 for p in projects if any(
                s.lower() in ['sql', 'database', 'postgres', 'mongodb']
                for s in p.get('skills', [])
            ))
            if db_count < len(projects) * 0.3:
                patterns.append({
                    "name": "State Simplicity Preference",
                    "evidence": f"{db_count}/{len(projects)} projects use databases",
                    "confidence": 0.90,
                    "impact": "Prefers simple state management"
                })

            # Check async usage
            async_count = sum(1 for p in projects if any(
                s.lower() in ['async', 'asyncio', 'threading']
                for s in p.get('skills', [])
            ))
            if async_count >= len(projects) * 0.5:
                patterns.append({
                    "name": "Async-First Development",
                    "evidence": f"{async_count}/{len(projects)} projects use async",
                    "confidence": 0.85,
                    "impact": "Builds with concurrency from day 1"
                })

            # Check complexity trajectory
            avg_complexity = sum(p.get('complexity_score', 0) for p in projects) / len(projects)
            if avg_complexity > 7.0:
                patterns.append({
                    "name": "High Complexity Tolerance",
                    "evidence": f"Average complexity: {avg_complexity:.1f}/10",
                    "confidence": 0.88,
                    "impact": "Comfortable with sophisticated architectures"
                })

        # Generate recommendations
        recommendations = [
            "Continue leveraging async patterns for scalability",
            "Explore advanced AWS services to expand your cloud toolkit",
            "Consider contributing to open source projects"
        ]

        return {
            "status": "success",
            "projects_analyzed": len(projects),
            "patterns": patterns,
            "recommendations": recommendations,
            "metrics": {
                "average_complexity": sum(p.get('complexity_score', 0) for p in projects) / max(len(projects), 1) if projects else 0,
                "pattern_count": len(patterns)
            }
        }
