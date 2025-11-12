"""
Janus Clew AgentCore Agent
Deployed to AWS Bedrock AgentCore Runtime
Pure bedrock-agentcore implementation without strands dependency
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


def detect_patterns_from_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect patterns across multiple projects.

    Args:
        projects: List of project dictionaries with complexity, skills, etc.

    Returns:
        List of detected patterns with evidence and confidence
    """
    patterns = []

    if not projects:
        return patterns

    # Pattern 1: Check for database usage
    db_projects = sum(1 for p in projects if any(
        skill.lower() in ['sql', 'postgresql', 'mysql', 'mongodb', 'database']
        for skill in p.get('skills', [])
    ))
    if db_projects < len(projects) * 0.3:  # Less than 30% use databases
        patterns.append({
            "name": "State Simplicity Preference",
            "evidence": f"{db_projects}/{len(projects)} projects use databases",
            "confidence": 0.95,
            "impact": "Prefers simple state management over heavy database integration"
        })

    # Pattern 2: Check for async/concurrency
    async_projects = sum(1 for p in projects if any(
        skill.lower() in ['async', 'asyncio', 'concurrency', 'threading']
        for skill in p.get('skills', [])
    ))
    if async_projects >= len(projects) * 0.5:  # 50% or more use async
        patterns.append({
            "name": "Async-First Architecture",
            "evidence": f"{async_projects}/{len(projects)} projects use async patterns",
            "confidence": 0.88,
            "impact": "Builds with concurrency in mind from the start"
        })

    # Pattern 3: Complexity trajectory
    if len(projects) >= 2:
        sorted_projects = sorted(projects, key=lambda p: p.get('timestamp', 0))
        first_complexity = sorted_projects[0].get('complexity_score', 5.0)
        last_complexity = sorted_projects[-1].get('complexity_score', 5.0)
        growth_rate = (last_complexity - first_complexity) / max(len(projects), 1)

        if growth_rate > 1.0:
            patterns.append({
                "name": "Rapid Learning Trajectory",
                "evidence": f"Complexity grew from {first_complexity:.1f} to {last_complexity:.1f}",
                "confidence": 0.92,
                "impact": "Shows accelerating technical growth"
            })

    # Pattern 4: Check for AWS/cloud usage
    cloud_projects = sum(1 for p in projects if any(
        skill.lower() in ['aws', 'boto3', 'lambda', 'cloud', 'bedrock']
        for skill in p.get('skills', [])
    ))
    if cloud_projects >= len(projects) * 0.4:
        patterns.append({
            "name": "Cloud-Native Development",
            "evidence": f"{cloud_projects}/{len(projects)} projects use cloud services",
            "confidence": 0.85,
            "impact": "Comfortable building cloud-first architectures"
        })

    return patterns


def generate_recommendations(projects: List[Dict[str, Any]], patterns: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations based on patterns.

    Args:
        projects: List of projects
        patterns: Detected patterns

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Get pattern names for easy checking
    pattern_names = {p['name'] for p in patterns}

    if "Async-First Architecture" in pattern_names:
        recommendations.append("Continue leveraging async patterns - consider exploring async frameworks like FastAPI or aiohttp")

    if "State Simplicity Preference" in pattern_names:
        recommendations.append("Your state simplicity approach is solid - when you do need persistence, consider starting with SQLite before moving to PostgreSQL")

    if "Rapid Learning Trajectory" in pattern_names:
        recommendations.append("Your growth rate is impressive - challenge yourself with distributed systems or microservices next")

    if "Cloud-Native Development" in pattern_names:
        recommendations.append("Explore advanced AWS services like Step Functions, EventBridge, or AppSync to expand your cloud toolkit")

    # Default recommendations if no specific patterns
    if not recommendations:
        recommendations.append("Keep building - focus on projects that push you slightly outside your comfort zone")
        recommendations.append("Consider contributing to open source to learn from diverse codebases")

    return recommendations


# Entrypoint for Bedrock AgentCore
@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.

    Args:
        payload: Dict with keys like "prompt", "projects", etc.

    Returns:
        Dict with response data including patterns and recommendations
    """
    try:
        prompt = payload.get("prompt", "Analyze my coding growth")
        projects = payload.get("projects", [])

        if not isinstance(projects, list):
            raise ValueError("Payload 'projects' must be a list")

        logger.info(f"[Agent] Processing {len(projects)} projects")
        logger.info(f"[Agent] Prompt: {prompt[:60]}...")

        # Detect patterns
        patterns = detect_patterns_from_projects(projects)
        logger.info(f"[Agent] Detected {len(patterns)} patterns")

        # Generate recommendations
        recommendations = generate_recommendations(projects, patterns)
        logger.info(f"[Agent] Generated {len(recommendations)} recommendations")

        # Calculate average complexity
        avg_complexity = 0.0
        if projects:
            complexities = [p.get('complexity_score', 0.0) for p in projects]
            avg_complexity = sum(complexities) / len(complexities)

        result = {
            "status": "success",
            "projects_analyzed": len(projects),
            "patterns": patterns,
            "recommendations": recommendations,
            "metrics": {
                "average_complexity": round(avg_complexity, 2),
                "pattern_count": len(patterns)
            },
            "model": "bedrock-agentcore-janus"
        }

        logger.info("[Agent] Invocation completed successfully")
        return result

    except Exception as e:
        logger.error(f"[Agent] Invocation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "projects_analyzed": 0,
            "patterns": [],
            "recommendations": [],
            "model": "bedrock-agentcore-janus"
        }


# Local development runner
if __name__ == "__main__":
    print("🚀 Starting Janus Clew Agent (local development)...")
    print("   Endpoint: http://localhost:8080/invocations")
    print("   Health check: http://localhost:8080/ping")
    app.run()
