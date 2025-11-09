"""Janus Clew FastAPI Server - Production-ready REST API.

Security Note (Local Use Only):
This server is designed for LOCAL development only. It has:
- No authentication
- No rate limiting
- No encryption

For production, add:
- JWT authentication
- HTTPS/TLS
- Rate limiting
- Input validation
- Audit logging
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import API_HOST, API_PORT, CORS_ORIGINS_LIST
from backend.models import (
    HealthResponse,
    AnalysesResponse,
    AnalysisResponse,
    TimelineResponse,
    SkillsResponse,
    GrowthResponse,
    ComplexityResponse,
    ErrorResponse,
)
from backend.services import (
    AnalysisService,
    TimelineService,
    SkillsService,
    GrowthService,
    ComplexityService,
    DevelopmentSignatureService,
)
from exceptions import JanusException, NotFoundError
from logger import get_logger

logger = get_logger(__name__)

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="Janus Clew",
    description="Evidence-backed growth tracking with Amazon Q",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug(f"CORS enabled for origins: {CORS_ORIGINS_LIST}")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(JanusException)
async def janus_exception_handler(request, exc: JanusException):
    """Handle Janus exceptions."""
    logger.warning(f"Janus exception: {exc.code} - {exc.message}")
    return ErrorResponse(
        status="error",
        error=exc.message,
        code=exc.code,
    ).dict()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return ErrorResponse(
        status="error",
        error=exc.detail,
        code=f"http_{exc.status_code}",
    ).dict()


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions - catch-all for unhandled errors."""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={"path": str(request.url), "method": request.method},
    )
    return ErrorResponse(
        status="error",
        error="Internal server error",
        code="internal_error",
    ).dict()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance."""
    return AnalysisService()


def get_timeline_service() -> TimelineService:
    """Get timeline service instance."""
    return TimelineService()


def get_skills_service() -> SkillsService:
    """Get skills service instance."""
    return SkillsService()


def get_growth_service() -> GrowthService:
    """Get growth service instance."""
    return GrowthService()


def get_complexity_service() -> ComplexityService:
    """Get complexity service instance."""
    return ComplexityService()


def get_development_signature_service() -> DevelopmentSignatureService:
    """Get development signature service instance."""
    return DevelopmentSignatureService()


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Health status with service version and data count
    """
    analysis_service = get_analysis_service()
    logger.debug("Health check")
    return {
        "status": "ok",
        "version": "0.2.0",
        "analyses_stored": analysis_service.get_analysis_count(),
    }


@app.get("/api/status")
async def status_endpoint():
    """Service status endpoint (alias for /health)."""
    return await health_check()


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/api/analyses")
async def get_all_analyses():
    """Get all stored analyses.

    Returns:
        List of all analyses sorted by timestamp (newest first)
    """
    logger.debug("GET /api/analyses")
    service = get_analysis_service()

    try:
        analyses = service.get_all_analyses()
        return AnalysesResponse(
            status="success",
            count=len(analyses),
            analyses=analyses,
        )
    except Exception as e:
        logger.error(f"Error getting analyses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch analyses")


@app.get("/api/analyses/latest")
async def get_latest_analysis():
    """Get the most recent analysis.

    Returns:
        Latest analysis data

    Raises:
        HTTPException: 404 if no analyses found
    """
    logger.debug("GET /api/analyses/latest")
    service = get_analysis_service()

    try:
        analysis = service.get_latest_analysis()
        return AnalysisResponse(status="success", analysis=analysis)
    except NotFoundError as e:
        logger.warning(f"No analyses found: {e}")
        raise HTTPException(status_code=404, detail="No analyses found")
    except Exception as e:
        logger.error(f"Error getting latest analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch analysis")


# ============================================================================
# TIMELINE ENDPOINTS
# ============================================================================

@app.get("/api/timeline")
async def get_timeline():
    """Get timeline data for visualization.

    Returns:
        Timeline data sorted by date
    """
    logger.debug("GET /api/timeline")
    service = get_timeline_service()

    try:
        timeline = service.get_timeline()
        return TimelineResponse(status="success", timeline=timeline)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="No timeline data available")
    except Exception as e:
        logger.error(f"Error getting timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch timeline")


# ============================================================================
# SKILLS ENDPOINTS
# ============================================================================

@app.get("/api/skills")
async def get_skills():
    """Get detected skills from latest analysis.

    Returns:
        List of detected skills with confidence and projects
    """
    logger.debug("GET /api/skills")
    service = get_skills_service()

    try:
        skills = service.get_skills()
        return SkillsResponse(status="success", skills=skills)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="No skills data available")
    except Exception as e:
        logger.error(f"Error getting skills: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch skills")


# ============================================================================
# GROWTH ENDPOINTS
# ============================================================================

@app.get("/api/growth")
async def get_growth_metrics():
    """Get overall growth metrics.

    Returns:
        Growth metrics including average complexity and growth rate
    """
    logger.debug("GET /api/growth")
    service = get_growth_service()

    try:
        metrics = service.get_growth_metrics()
        return GrowthResponse(status="success", metrics=metrics)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="No growth data available")
    except Exception as e:
        logger.error(f"Error getting growth metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch growth metrics")


# ============================================================================
# COMPLEXITY ENDPOINTS
# ============================================================================

@app.get("/api/complexity/{project_name}")
async def get_complexity_breakdown(project_name: str):
    """Get complexity breakdown for a specific project.

    Args:
        project_name: Name of the project

    Returns:
        Complexity breakdown showing calculation components

    Raises:
        HTTPException: 404 if project not found
    """
    logger.debug(f"GET /api/complexity/{project_name}")
    service = get_complexity_service()

    try:
        breakdown = service.get_complexity_breakdown(project_name)
        return ComplexityResponse(status="success", project=project_name, breakdown=breakdown)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Project {project_name} not found")
    except Exception as e:
        logger.error(f"Error getting complexity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch complexity")


# ============================================================================
# DEVELOPMENT SIGNATURE ENDPOINTS (PHASE 2)
# ============================================================================

@app.get("/api/development-signature")
async def get_development_signature():
    """Get Development Signature - complete analysis with patterns, preferences, trajectory, and recommendations.

    Returns:
        Development signature with patterns, preferences, trajectory, and recommendations

    Raises:
        HTTPException: 404 if no analyses found
    """
    logger.debug("GET /api/development-signature")
    service = get_development_signature_service()

    try:
        signature = service.generate_development_signature()
        return {
            "status": "success",
            "signature": signature
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="No analyses found for signature")
    except Exception as e:
        logger.error(f"Error generating development signature: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate development signature")


# ============================================================================
# STATIC FILES
# ============================================================================

# Serve static React files if they exist
static_path = Path(__file__).parent.parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
    logger.info(f"Serving static files from {static_path}")
else:
    logger.warning(f"Static files not found at {static_path}")


@app.get("/")
async def root():
    """Root route - serve frontend or welcome message."""
    index_file = static_path / "index.html"

    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return {
            "message": "Janus Clew API",
            "status": "running",
            "docs": "/docs",
            "health": "/api/health",
        }


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Called when server starts."""
    logger.info("🚀 Janus Clew API starting...")
    logger.info(f"API running on http://{API_HOST}:{API_PORT}")
    logger.info(f"Docs available at http://{API_HOST}:{API_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when server shuts down."""
    logger.info("👋 Janus Clew API shutting down...")


def run_server(host: str = API_HOST, port: int = API_PORT, reload: bool = False):
    """Run the FastAPI server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Auto-reload on code changes (development only)
    """
    import uvicorn

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "backend.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    run_server(reload=True)
