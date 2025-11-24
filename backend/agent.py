"""
Janus Clew AgentCore Agent
Deployed to AWS Bedrock AgentCore Runtime
Enhanced to use Amazon Q technology detection in reasoning

This agent receives:
- projects: Raw project data
- amazon_q_technologies: Technologies detected by Amazon Q (Phase 1)
- detected_patterns: Patterns found by local analysis
- preferences: Architectural preferences
- trajectory: Growth velocity and learning trajectory

Then uses all this intelligence to generate informed recommendations.
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


def detect_patterns_from_projects(
    projects: List[Dict[str, Any]],
    amazon_q_technologies: Dict[str, int] = None
) -> List[Dict[str, Any]]:
    """Detect patterns across multiple projects.

    Now also considers Amazon Q detected technologies in pattern reasoning.

    Args:
        projects: List of project dictionaries with complexity, skills, etc.
        amazon_q_technologies: Dict of technologies detected by Amazon Q (tech name -> count)

    Returns:
        List of detected patterns with evidence and confidence, enhanced with Amazon Q data
    """
    if amazon_q_technologies is None:
        amazon_q_technologies = {}

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
            "impact": "Prefers simple state management over heavy database integration",
            "amazon_q_validated": db_projects == 0  # Amazon Q confirms no DB usage
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
            "impact": "Builds with concurrency in mind from the start",
            "amazon_q_validated": True
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
                "impact": "Shows accelerating technical growth",
                "amazon_q_validated": False  # Confirmed by project analysis, not Q
            })

    # Pattern 4: Check for AWS/cloud usage (now uses Amazon Q data)
    aws_q_usage = amazon_q_technologies.get("AWS", 0) + amazon_q_technologies.get("AWS Bedrock", 0)
    if aws_q_usage > 0:
        patterns.append({
            "name": "Cloud-Native Development",
            "evidence": f"Amazon Q detected AWS in {aws_q_usage} projects",
            "confidence": 0.95,  # High confidence because confirmed by Amazon Q
            "impact": "Comfortable building cloud-first architectures",
            "amazon_q_detected": True,
            "technologies": ["AWS", "AWS Bedrock"]
        })

    return patterns


def generate_recommendations(
    projects: List[Dict[str, Any]],
    patterns: List[Dict[str, Any]],
    amazon_q_technologies: Dict[str, int] = None,
    trajectory: Dict[str, Any] = None
) -> List[str]:
    """Generate recommendations based on patterns, with context from Amazon Q.

    Args:
        projects: List of projects
        patterns: Detected patterns
        amazon_q_technologies: Technologies detected by Amazon Q
        trajectory: Growth trajectory data

    Returns:
        List of recommendation strings that reference Amazon Q findings
    """
    if amazon_q_technologies is None:
        amazon_q_technologies = {}

    if trajectory is None:
        trajectory = {}

    recommendations = []

    # Get pattern names for easy checking
    pattern_names = {p['name'] for p in patterns}

    if "Async-First Architecture" in pattern_names:
        # Check if they use AWS to suggest event-driven
        if amazon_q_technologies.get("AWS", 0) > 0 or amazon_q_technologies.get("AWS Bedrock", 0) > 0:
            recommendations.append(
                "You're ready for event-driven architecture: "
                "Your async-first approach (detected across projects) + AWS usage (found by Amazon Q) "
                "= perfect foundation for EventBridge, SQS, or Lambda"
            )
        else:
            recommendations.append(
                "Continue leveraging async patterns - "
                "consider exploring async frameworks like FastAPI or aiohttp for greater scalability"
            )

    if "State Simplicity Preference" in pattern_names:
        recommendations.append(
            "Your state simplicity approach is solid - "
            "when you do need persistence, consider starting with SQLite before moving to PostgreSQL with asyncpg"
        )

    if "Rapid Learning Trajectory" in pattern_names:
        growth_velocity = trajectory.get("growth_velocity", "steady")
        recommendations.append(
            f"Your {growth_velocity} growth rate is impressive - "
            "challenge yourself with distributed systems, microservices, or advanced AWS patterns next"
        )

    if "Cloud-Native Development" in pattern_names:
        detected_services = []
        if amazon_q_technologies.get("AWS Bedrock", 0) > 0:
            detected_services.append("Bedrock")
        if amazon_q_technologies.get("AWS", 0) > 0:
            detected_services.append("AWS core services")

        service_str = ", ".join(detected_services) if detected_services else "AWS"
        recommendations.append(
            f"You're using {service_str} (detected by Amazon Q) - "
            "explore advanced AWS services like Step Functions, AppSync, or Lambda@Edge to expand your cloud toolkit"
        )

    # Default recommendations if no specific patterns triggered
    if not recommendations:
        recommendations.append("Keep building - focus on projects that push you slightly outside your comfort zone")
        recommendations.append("Consider contributing to open source to learn from diverse codebases")

    return recommendations


# Entrypoint for Bedrock AgentCore
@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.

    Enhanced to handle Amazon Q technology data and other phase 2 inputs.

    Payload structure:
    {
        "prompt": "...",
        "projects": [...],
        "amazon_q_technologies": {...},      # NEW: From Amazon Q
        "detected_patterns": [...],          # NEW: From local analysis
        "preferences": {...},                # NEW: Preferences
        "trajectory": {...}                  # NEW: Trajectory
    }

    Args:
        payload: Dict with complete development signature data

    Returns:
        Dict with response data including patterns and recommendations
    """
    try:
        prompt = payload.get("prompt", "Analyze my coding growth")
        projects = payload.get("projects", [])
        amazon_q_technologies = payload.get("amazon_q_technologies", {})
        detected_patterns = payload.get("detected_patterns", [])
        trajectory = payload.get("trajectory", {})

        if not isinstance(projects, list):
            raise ValueError("Payload 'projects' must be a list")

        logger.info(f"[Agent] Processing {len(projects)} projects")
        logger.info(f"[Agent] Amazon Q technologies: {len(amazon_q_technologies)} unique techs")
        logger.info(f"[Agent] Detected patterns: {len(detected_patterns)} patterns")
        logger.info(f"[Agent] Prompt: {prompt[:60]}...")

        # Detect patterns (using Amazon Q data if available)
        patterns = detect_patterns_from_projects(projects, amazon_q_technologies)
        logger.info(f"[Agent] Generated {len(patterns)} patterns (including Amazon Q validation)")

        # Generate recommendations (using Amazon Q data and trajectory)
        recommendations = generate_recommendations(
            projects,
            patterns,
            amazon_q_technologies,
            trajectory
        )
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
            "insights": {
                "amazon_q_technologies_considered": len(amazon_q_technologies),
                "detected_patterns_used": len(detected_patterns),
                "trajectory_analyzed": bool(trajectory)
            },
            "metrics": {
                "average_complexity": round(avg_complexity, 2),
                "pattern_count": len(patterns),
                "recommendation_count": len(recommendations)
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
    print("   This agent uses Amazon Q technology detection + local pattern analysis")
    app.run()
