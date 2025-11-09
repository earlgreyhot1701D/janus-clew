"""Janus Clew Backend - FastAPI server."""

__version__ = "0.2.0"

# Import all services so they're available
from backend.services import (
    AnalysisService,
    TimelineService,
    SkillsService,
    GrowthService,
    ComplexityService,
    DevelopmentSignatureService,
)

__all__ = [
    "AnalysisService",
    "TimelineService",
    "SkillsService",
    "GrowthService",
    "ComplexityService",
    "DevelopmentSignatureService",
]
