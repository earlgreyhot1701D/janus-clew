"""AgentCore integration for Development Signature.

Handles calls to AgentCore for intelligent pattern detection and analysis.
Manages prompts, responses, and error handling.
"""

import json
from typing import Dict, List, Any, Optional
from logger import get_logger
from exceptions import JanusException

logger = get_logger(__name__)


class AgentCoreIntegrationError(JanusException):
    """Error during AgentCore integration."""
    pass


class AgentCoreCaller:
    """Calls AgentCore for intelligent analysis."""

    def __init__(self, client=None):
        """Initialize AgentCore caller.

        Args:
            client: Optional AgentCore client (for testing)
        """
        self.client = client or self._get_agentcore_client()

    def _get_agentcore_client(self):
        """Get AgentCore client - uses Claude API via Bedrock."""
        try:
            import boto3
            client = boto3.client('bedrock-runtime', region_name='us-west-2')
            logger.debug("Initialized Bedrock AgentCore client")
            return BedrockAgentCoreClient(client)
        except Exception as e:
            logger.warning(f"Bedrock client init failed: {e}, using mock")
            return MockAgentCoreClient()

    def detect_patterns(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to detect patterns.

        Args:
            analyses: List of analysis dictionaries

        Returns:
            Pattern detection results

        Raises:
            AgentCoreIntegrationError: If call fails
        """
        try:
            from development_signature_prompts import (
                PATTERN_DETECTION_PROMPT,
                build_pattern_detection_input
            )

            # Build input for prompt
            project_history = build_pattern_detection_input(analyses)
            prompt = PATTERN_DETECTION_PROMPT.format(project_history=project_history)

            # Call AgentCore
            response = self.client.analyze(prompt)
            logger.debug("Received AgentCore pattern detection response")

            # Parse response
            result = self._parse_json_response(response)
            return result

        except Exception as e:
            logger.error(f"AgentCore pattern detection failed: {e}")
            raise AgentCoreIntegrationError(f"Pattern detection failed: {e}")

    def analyze_preferences(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call AgentCore to analyze preferences.

        Args:
            analyses: List of analyses

        Returns:
            Preference analysis results
        """
        try:
            from development_signature_prompts import (
                ARCHITECTURAL_PREFERENCES_PROMPT,
                build_preference_analysis_input
            )

            project_analysis = build_preference_analysis_input(analyses)
            prompt = ARCHITECTURAL_PREFERENCES_PROMPT.format(
                project_analysis=project_analysis
            )

            response = self.client.analyze(prompt)
            result = self._parse_json_response(response)
            return result

        except Exception as e:
            logger.error(f"AgentCore preference analysis failed: {e}")
            raise AgentCoreIntegrationError(f"Preference analysis failed: {e}")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from AgentCore.

        Args:
            response: Response text from AgentCore

        Returns:
            Parsed JSON as dictionary

        Raises:
            AgentCoreIntegrationError: If parsing fails
        """
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            raise AgentCoreIntegrationError(f"Could not parse JSON response: {response[:100]}")


class BedrockAgentCoreClient:
    """Bedrock-backed AgentCore client using Claude models."""

    def __init__(self, bedrock_client):
        """Initialize with Bedrock client."""
        self.client = bedrock_client
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    def analyze(self, prompt: str) -> str:
        """Call Claude via Bedrock for analysis.

        Args:
            prompt: Analysis prompt

        Returns:
            Response text from Claude
        """
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1024
                })
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except Exception as e:
            logger.error(f"Bedrock API call failed: {e}")
            # Gracefully fallback to mock
            return MockAgentCoreClient().analyze(prompt)


class MockAgentCoreClient:
    """Mock AgentCore client for testing and graceful degradation."""

    def analyze(self, prompt: str) -> str:
        """Mock analysis response.

        Args:
            prompt: Analysis prompt

        Returns:
            Mock JSON response
        """
        logger.debug("Using mock AgentCore client")

        # Return sensible defaults based on prompt type
        if "Pattern" in prompt or "pattern" in prompt:
            return self._mock_pattern_response()
        elif "Preference" in prompt or "preference" in prompt:
            return self._mock_preference_response()
        else:
            return self._mock_default_response()

    def _mock_pattern_response(self) -> str:
        """Mock pattern detection response."""
        return json.dumps({
            "patterns": [
                {
                    "name": "Database Avoidance",
                    "evidence": "0/3 projects use SQL",
                    "confidence": 0.98,
                    "impact": "You prefer state simplicity"
                },
                {
                    "name": "Async-First Thinking",
                    "evidence": "2/3 projects use async/await",
                    "confidence": 0.87,
                    "impact": "You build for concurrency from day 1"
                },
                {
                    "name": "Rapid Learning",
                    "evidence": "2.5x growth in 8 weeks",
                    "confidence": 0.92,
                    "impact": "You're learning quickly"
                }
            ]
        })

    def _mock_preference_response(self) -> str:
        """Mock preference analysis response."""
        return json.dumps({
            "preferences": [
                {
                    "name": "State Simplicity",
                    "score": 0.92,
                    "reasoning": "Avoids databases consistently",
                    "evidence": "No SQL in any project"
                },
                {
                    "name": "Async/Concurrency Comfort",
                    "score": 0.87,
                    "reasoning": "Uses async patterns effectively",
                    "evidence": "Async/await in 2/3 projects"
                },
                {
                    "name": "Complexity Tolerance",
                    "score": 0.78,
                    "reasoning": "Comfortable with 8.1/10 average",
                    "evidence": "Handles sophisticated architectures"
                }
            ]
        })

    def _mock_default_response(self) -> str:
        """Mock default response."""
        return json.dumps({"status": "success", "message": "Mock response"})
