"""Janus Clew Configuration - Centralized settings and constants."""

import os
from pathlib import Path
from typing import Literal

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME = "janus-clew"
APP_VERSION = "0.2.0"
APP_DESCRIPTION = "Evidence-backed coding growth tracking with Amazon Q Developer"
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = Path.home() / f".{APP_NAME}"
ANALYSES_DIR = DATA_DIR / "analyses"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

ENVIRONMENT: Literal["development", "production", "testing"] = os.getenv(
    "JANUS_ENV", "development"
)

DEBUG = ENVIRONMENT != "production"
VERBOSE = os.getenv("JANUS_VERBOSE", "false").lower() == "true"

# ============================================================================
# AWS CONFIGURATION
# ============================================================================

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_BUILDER_ID_EMAIL = os.getenv("AWS_BUILDER_ID_EMAIL", "")

# Amazon Q CLI configuration
AMAZON_Q_CLI_TIMEOUT = int(os.getenv("AMAZON_Q_TIMEOUT", "60"))
AMAZON_Q_RETRY_ATTEMPTS = int(os.getenv("AMAZON_Q_RETRIES", "3"))
AMAZON_Q_RETRY_BACKOFF = float(os.getenv("AMAZON_Q_BACKOFF", "2.0"))

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "3000"))
API_RELOAD = ENVIRONMENT == "development"

FRONTEND_HOST = os.getenv("FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "5173"))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)

# ============================================================================
# ANALYSIS CONFIGURATION
# ============================================================================

# Complexity scoring weights (must sum to 10 or less)
COMPLEXITY_FILE_WEIGHT = 3.0  # 0-3 points for file count
COMPLEXITY_FUNCTION_WEIGHT = 4.0  # 0-4 points for function density
COMPLEXITY_CLASS_WEIGHT = 2.0  # 0-2 points for OOP maturity
COMPLEXITY_NESTING_WEIGHT = 1.0  # 0-1 point for nesting depth

# Growth calculation
MIN_PROJECTS_FOR_GROWTH = 2

# ============================================================================
# CLI CONFIGURATION
# ============================================================================

CLI_CACHE_RESULTS = os.getenv("JANUS_CACHE", "true").lower() == "true"
CLI_USE_MOCK_DATA = os.getenv("JANUS_USE_MOCK", "false").lower() == "true"

# ============================================================================
# API CONFIGURATION
# ============================================================================

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
CORS_ORIGINS_LIST = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# ============================================================================
# DEMO/SAMPLE DATA
# ============================================================================

# Pre-generated sample analysis for demo purposes
SAMPLE_ANALYSIS_FILE = DATA_DIR / "sample_analysis.json"

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    "no_repos": "❌ No repositories provided. Usage: janus-clew analyze <repo1> <repo2> ...",
    "repo_not_found": "❌ Repository not found: {repo_path}",
    "git_error": "❌ Git error analyzing {repo_name}: {error}",
    "analysis_error": "❌ Analysis failed for {repo_name}: {error}",
    "storage_error": "❌ Storage error: {error}",
    "aws_q_error": "❌ Amazon Q error: {error}",
    "config_error": "❌ Configuration error: {error}",
    "no_data": "❌ No analysis data found. Run: janus-clew analyze <repos>",
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES = {
    "analysis_start": "🧵 Janus Clew - Analyzing your repositories...",
    "analysis_complete": "✅ Analysis complete!",
    "data_saved": "💾 Analysis saved to: {path}",
    "cli_ready": "🚀 CLI ready. Run: janus-clew analyze <repos>",
    "server_ready": "🚀 Server running on http://{host}:{port}",
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration."""
    if not AWS_BUILDER_ID_EMAIL and not CLI_USE_MOCK_DATA:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "AWS_BUILDER_ID_EMAIL not set. Set it with: export AWS_BUILDER_ID_EMAIL=your@email.com"
        )


validate_config()
