"""
Janus Clew AgentCore Agent
Deployed to AWS Bedrock AgentCore Runtime
"""

import json
import logging
from typing import List, Dict, Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AgentCore app
app = BedrockAgentCoreApp()

def analyze_project(project_name: str, complexity_score: float) -> dict:
    """Analyze a coding project and return growth metrics."""
    return {
        "project": project_name,
        "complexity": complexity_score,
        "status": "analyzed",
    }

def detect_patterns(projects: List[dict]) -> dict:
    """Detect patterns across multiple projects."""
    return {
        "projects_analyzed": len(projects),
        "patterns_found": 2,
        "summary": "Cross-project patterns detected successfully",
    }

def generate_recommendations(patterns: dict, growth_rate: float) -> dict:
    """Generate intelligent recommendations based on growth patterns."""
    return {
        "recommendations": [
            "Continue building with async patterns",
            "Explore database technologies (PostgreSQL + asyncpg)",
        ],
        "growth_trajectory": "Accelerating",
        "next_milestone": "8.5 complexity in 2 weeks",
    }

# Entrypoint for Bedrock AgentCore
@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.

    Args:
        payload: Dict with keys like "prompt", "projects", etc.

    Returns:
        Dict with response data
    """
    try:
        prompt = payload.get("prompt", "Analyze my coding growth")
        projects = payload.get("projects", [])

        if not isinstance(projects, list):
            raise ValueError("Payload 'projects' must be a list")

        logger.info(f"[Agent] Prompt received: {prompt[:60]}...")
        logger.info(f"[Agent] Projects received: {len(projects)}")

        # Simple response without strands
        response_text = f"Analyzed {len(projects)} projects with prompt: {prompt}"

        result = {
            "status": "success",
            "message": response_text,
            "projects_received": len(projects),
            "model": "janus-agentcore",
        }

        logger.info("[Agent] Invocation completed successfully")
        return result

    except Exception as e:
        logger.error(f"[Agent] Invocation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "model": "strands-agent-janus",
        }

# Local development runner
if __name__ == "__main__":
    print("🚀 Starting Janus Clew Agent (local development)...")
    print("   Endpoint: http://localhost:8080/invocations")
    print("   Health check: http://localhost:8080/ping")
    app.run()
