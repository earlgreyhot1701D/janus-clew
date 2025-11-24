"""Janus Clew Configuration - Centralized settings and constants."""

from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from typing import Literal

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME = "janus-clew"
APP_VERSION = "0.3.0"
APP_DESCRIPTION = "Evidence-backed coding growth tracking with AWS AgentCore"
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

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "833162255362")

# ============================================================================
# AWS AGENTCORE CONFIGURATION
# ============================================================================

# AgentCore agent credentials (set in .env)
AGENTCORE_AGENT_ID = os.getenv("AGENTCORE_AGENT_ID", "")
AGENTCORE_AGENT_ALIAS = os.getenv("AGENTCORE_AGENT_ALIAS", "LFZNSMOJVE")

# ============================================================================
# AGENTCORE RESILIENCE SETTINGS
# ============================================================================

# Retry configuration
AGENTCORE_MAX_RETRIES = int(os.getenv("AGENTCORE_MAX_RETRIES", "3"))
AGENTCORE_INITIAL_BACKOFF = int(os.getenv("AGENTCORE_INITIAL_BACKOFF", "1"))
AGENTCORE_MAX_BACKOFF = int(os.getenv("AGENTCORE_MAX_BACKOFF", "8"))

# Circuit breaker configuration
AGENTCORE_CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("AGENTCORE_CIRCUIT_BREAKER_THRESHOLD", "3"))
AGENTCORE_CIRCUIT_BREAKER_RECOVERY = int(os.getenv("AGENTCORE_CIRCUIT_BREAKER_RECOVERY", "60"))

# Request timeout (seconds)
AGENTCORE_TIMEOUT_SECONDS = int(os.getenv("AGENTCORE_TIMEOUT_SECONDS", "30"))

# Cache configuration
AGENTCORE_CACHE_TTL_SECONDS = int(os.getenv("AGENTCORE_CACHE_TTL_SECONDS", "86400"))

# Rate limiting
AGENTCORE_MAX_CONCURRENT_CALLS = int(os.getenv("AGENTCORE_MAX_CONCURRENT_CALLS", "2"))

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "3001"))
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
CACHE_ENABLED = CLI_CACHE_RESULTS  # Alias for backward compatibility with analyzer.py

# ============================================================================
# API CONFIGURATION
# ============================================================================

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3001")
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
    """Validate critical configuration at runtime.

    Raises:
        ValueError: If critical config is invalid
    """
    import logging
    logger = logging.getLogger(__name__)

    errors = []

    # Validate AWS region
    if not AWS_REGION:
        errors.append("AWS_REGION not set")

    # Validate resilience settings
    if AGENTCORE_MAX_RETRIES < 1:
        errors.append("AGENTCORE_MAX_RETRIES must be >= 1")

    if AGENTCORE_INITIAL_BACKOFF < 1:
        errors.append("AGENTCORE_INITIAL_BACKOFF must be >= 1")

    if AGENTCORE_TIMEOUT_SECONDS < 5:
        errors.append("AGENTCORE_TIMEOUT_SECONDS must be >= 5")

    if AGENTCORE_MAX_CONCURRENT_CALLS < 1:
        errors.append("AGENTCORE_MAX_CONCURRENT_CALLS must be >= 1")

    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug("✅ Configuration validation passed")


# Run validation at import time
try:
    validate_config()
except ValueError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Config validation failed: {e}")
    # Don't raise - allow graceful degradation with warnings
