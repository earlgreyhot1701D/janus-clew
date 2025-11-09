"""AgentCore prompts for Development Signature analysis.

Stores all prompts for AgentCore pattern detection and recommendation generation.
This module is isolated from implementation to allow easy prompt iteration.
"""

# ============================================================================
# PATTERN DETECTION PROMPT
# ============================================================================

PATTERN_DETECTION_PROMPT = """Analyze the following developer's project history and identify key behavioral patterns.

Project History:
{project_history}

Please identify patterns across ALL projects. Look for:
1. Technology preferences (databases used/avoided, frameworks, languages)
2. Architectural patterns (async/sync, state management, event-driven)
3. Code organization patterns (modular, monolithic, etc.)
4. Learning velocity (complexity growth over time)
5. Framework diversity (technologies used)

For each pattern identified, provide:
- Pattern name
- Evidence (which projects show this)
- Confidence level (0.0-1.0)
- Impact (what this pattern means about the developer)

Return as JSON with structure:
{{
  "patterns": [
    {{
      "name": "pattern_name",
      "evidence": "specific examples from projects",
      "confidence": 0.85,
      "impact": "what this reveals about the developer"
    }}
  ]
}}

Be specific and evidence-based. Only include patterns you can directly verify from the code."""

# ============================================================================
# ARCHITECTURAL PREFERENCES PROMPT
# ============================================================================

ARCHITECTURAL_PREFERENCES_PROMPT = """Analyze this developer's projects and extract their architectural preferences.

Project Analysis:
{project_analysis}

Determine scores (0-1.0) for these preferences:

1. **State Simplicity** (0-1): Do they prefer stateless architectures or state-heavy?
   - High: Avoids databases, prefers in-memory solutions
   - Low: Heavy state management, persistent storage

2. **Async/Concurrency Comfort** (0-1): How comfortable with async patterns?
   - High: Uses async/await, concurrent patterns, parallel processing
   - Low: Synchronous, blocking code

3. **Complexity Tolerance** (0-1): Can they handle sophisticated architecture?
   - High: Multi-layer systems, intricate logic, high coupling tolerance
   - Low: Prefers simple, straightforward designs

4. **Framework Diversity** (0-1): Do they learn many frameworks or specialize?
   - High: Uses many different technologies
   - Low: Focuses on specific tech stack

5. **Code Organization** (0-1): How organized/modular is their code?
   - High: Clear separation, modular design
   - Low: Monolithic, tightly coupled

For each preference, provide:
- Score (0-1.0)
- Reasoning (why this score)
- Evidence (from specific projects)

Return as JSON:
{{
  "preferences": [
    {{
      "name": "preference_name",
      "score": 0.85,
      "reasoning": "explanation of score",
      "evidence": "specific evidence from projects"
    }}
  ]
}}"""

# ============================================================================
# TRAJECTORY ANALYSIS PROMPT
# ============================================================================

TRAJECTORY_ANALYSIS_PROMPT = """Analyze this developer's learning trajectory over time.

Timeline:
{timeline_data}

Complexity Evolution:
{complexity_evolution}

Calculate and provide:

1. **Growth Rate** (as multiplier): Latest complexity / Earliest complexity
2. **Learning Velocity** (complexity gain per week): How fast they're learning
3. **Trend** (accelerating/steady/decelerating)
4. **Projection** (4-week prediction)
5. **Interpretation** (what this trajectory reveals)

Return as JSON:
{{
  "growth_rate": 2.5,
  "weeks_elapsed": 8,
  "learning_velocity": 0.27,
  "projected_4_weeks": 8.9,
  "trend": "accelerating",
  "interpretation": "This developer is learning rapidly, increasing complexity at a 0.27 points per week rate."
}}"""

# ============================================================================
# RECOMMENDATION GENERATION PROMPT
# ============================================================================

RECOMMENDATION_GENERATION_PROMPT = """Based on this developer's patterns, preferences, and trajectory, generate forward-looking recommendations.

Developer Profile:
- Architectural Preferences: {preferences}
- Detected Patterns: {patterns}
- Learning Trajectory: {trajectory}
- Projects: {projects}

Generate 3-5 intelligent recommendations about what they should learn next.

For EACH recommendation:
- Skill/Technology to learn
- Status: "ready" (can learn now), "ready_soon" (in 4-8 weeks), or "not_yet" (should wait)
- Confidence (0-1.0)
- Reasoning (WHY this recommendation, based on their patterns)
- Evidence (which patterns support this)
- Timeline (realistic timeline to master)
- Next Action (specific project to build)

Important: Be SELECTIVE. Not every developer is ready for everything.
Include at least one "not_yet" recommendation if appropriate - judges respect wisdom.

Return as JSON:
{{
  "recommendations": [
    {{
      "skill": "PostgreSQL + asyncpg",
      "status": "ready",
      "confidence": 0.92,
      "reasoning": "You already understand async patterns and prefer state simplicity...",
      "evidence": ["Async in 2/3 projects", "0/3 projects use SQL", "Comfortable with 8.1/10 complexity"],
      "timeline": "4-6 weeks",
      "next_action": "Build one event-driven service with PostgreSQL"
    }}
  ]
}}"""

# ============================================================================
# HELPER FUNCTION TO BUILD ANALYSIS INPUT
# ============================================================================


def build_pattern_detection_input(analyses: list) -> str:
    """Build formatted project history for pattern detection prompt.
    
    Args:
        analyses: List of analysis dictionaries from storage
        
    Returns:
        Formatted string for prompt injection
    """
    projects_text = []
    for analysis in analyses:
        for project in analysis.get("projects", []):
            proj_info = f"""
Project: {project.get('name', 'Unknown')}
- Complexity: {project.get('complexity_score', 0)}/10
- Technologies: {', '.join(project.get('technologies', []))}
- Commits: {project.get('commits', 0)}
"""
            projects_text.append(proj_info)
    
    return "\n".join(projects_text)


def build_preference_analysis_input(analyses: list) -> str:
    """Build formatted project analysis for preference detection.
    
    Args:
        analyses: List of analysis dictionaries
        
    Returns:
        Formatted string for prompt
    """
    # Extract project details with code patterns
    details = []
    for analysis in analyses:
        for project in analysis.get("projects", []):
            tech_stack = ", ".join(project.get("technologies", []))
            details.append(f"""
{project.get('name')}:
  Complexity: {project.get('complexity_score', 0)}/10
  Tech: {tech_stack}
  Commits: {project.get('commits', 0)}
""")
    
    return "\n".join(details)


def build_trajectory_input(analyses: list) -> dict:
    """Build trajectory data for analysis.
    
    Args:
        analyses: List of analysis dictionaries
        
    Returns:
        Dictionary with timeline and complexity evolution
    """
    timeline = []
    complexities = []
    
    for analysis in analyses:
        timestamp = analysis.get("timestamp", "unknown")
        for project in analysis.get("projects", []):
            complexity = project.get("complexity_score", 0)
            complexities.append(complexity)
            timeline.append({
                "date": timestamp,
                "project": project.get("name"),
                "complexity": complexity
            })
    
    return {
        "timeline": timeline,
        "complexities": complexities,
        "complexity_evolution": " → ".join(f"{c:.1f}" for c in complexities)
    }
