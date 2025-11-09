"""Pydantic models for data validation and API responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# INPUT MODELS
# ============================================================================


class AnalyzeRequest(BaseModel):
    """Request to analyze repositories."""

    repos: List[str] = Field(..., min_items=1, description="List of repository paths")
    force: bool = Field(False, description="Force re-analysis")


# ============================================================================
# DATA MODELS
# ============================================================================


class QAnalysis(BaseModel):
    """Amazon Q analysis results."""

    skill_level: str = Field(..., description="Beginner, intermediate, or advanced")
    technologies: List[str] = Field(default_factory=list, description="Detected tech stack")
    complexity: int = Field(..., ge=0, le=10, description="Complexity score 0-10")
    patterns: List[str] = Field(default_factory=list, description="Detected patterns")
    raw_output: Optional[str] = Field(None, description="Raw Q output")


class ProjectAnalysis(BaseModel):
    """Analysis of a single project."""

    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project path")
    commits: int = Field(..., ge=0, description="Commit count")
    complexity_score: float = Field(..., ge=0, le=10, description="Complexity score")
    technologies: List[str] = Field(default_factory=list, description="Detected technologies")
    first_commit: Optional[str] = Field(None, description="First commit timestamp")
    q_analysis: Optional[QAnalysis] = Field(None, description="Amazon Q analysis")


class OverallMetrics(BaseModel):
    """Overall metrics across projects."""

    avg_complexity: float = Field(..., ge=0, le=10, description="Average complexity")
    total_projects: int = Field(..., ge=0, description="Number of projects")
    growth_rate: float = Field(..., description="Growth rate percentage")


class AnalysisError(BaseModel):
    """Error during analysis."""

    repo: str = Field(..., description="Repository path")
    error: str = Field(..., description="Error message")


class FullAnalysis(BaseModel):
    """Complete analysis result."""

    projects: List[ProjectAnalysis]
    overall: OverallMetrics
    errors: List[AnalysisError] = Field(default_factory=list)
    patterns: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    version: Optional[str] = None


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    analyses_stored: int = Field(..., description="Number of stored analyses")


class AnalysesResponse(BaseModel):
    """Response for getting all analyses."""

    status: str = Field(..., description="Response status")
    count: int = Field(..., description="Number of analyses")
    analyses: List[FullAnalysis] = Field(..., description="List of analyses")


class AnalysisResponse(BaseModel):
    """Response for single analysis."""

    status: str = Field(..., description="Response status")
    analysis: FullAnalysis = Field(..., description="Analysis data")


class TimelinePoint(BaseModel):
    """Point on growth timeline."""

    date: str = Field(..., description="Date of analysis")
    project_name: str = Field(..., description="Project name")
    complexity: float = Field(..., description="Complexity score")
    skills: List[str] = Field(..., description="Skills learned")


class TimelineResponse(BaseModel):
    """Response for timeline data."""

    status: str = Field(..., description="Response status")
    timeline: List[TimelinePoint] = Field(..., description="Timeline data")


class SkillData(BaseModel):
    """Skill information."""

    name: str = Field(..., description="Skill name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    projects: List[str] = Field(..., description="Projects with this skill")


class SkillsResponse(BaseModel):
    """Response for skills data."""

    status: str = Field(..., description="Response status")
    skills: List[SkillData] = Field(..., description="Detected skills")


class GrowthMetrics(BaseModel):
    """Growth metrics."""

    avg_complexity: float = Field(..., description="Average complexity")
    total_projects: int = Field(..., description="Total projects")
    growth_rate: float = Field(..., description="Growth rate percentage")


class GrowthResponse(BaseModel):
    """Response for growth metrics."""

    status: str = Field(..., description="Response status")
    metrics: GrowthMetrics = Field(..., description="Growth metrics")


class ComplexityBreakdown(BaseModel):
    """Complexity score breakdown."""

    total_score: float = Field(..., description="Total complexity score")
    file_score: float = Field(..., description="Files component")
    function_score: float = Field(..., description="Functions component")
    class_score: float = Field(..., description="Classes component")
    nesting_score: float = Field(..., description="Nesting component")
    explanation: str = Field(..., description="Explanation of calculation")


class ComplexityResponse(BaseModel):
    """Response for complexity breakdown."""

    status: str = Field(..., description="Response status")
    project: str = Field(..., description="Project name")
    breakdown: ComplexityBreakdown = Field(..., description="Breakdown data")


class ErrorResponse(BaseModel):
    """Error response."""

    status: str = Field(..., description="Error status")
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
