"""AWS Bedrock AgentCore integration with resilience patterns and observability.

This module implements production-grade integration with AgentCore including:
- Retry logic with exponential backoff
- Circuit breaker pattern for resilience
- Request timeout handling
- Input/output validation
- Structured logging
- Response caching
- Rate limiting
"""

import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import threading

import boto3
from botocore.exceptions import ClientError, BotoCoreError, ConnectTimeoutError, ReadTimeoutError

from logger import get_logger
from config import AWS_REGION, AWS_ACCOUNT_ID

logger = get_logger(__name__)


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

AGENTCORE_TIMEOUT_SECONDS = 30
AGENTCORE_MAX_RETRIES = 3
AGENTCORE_INITIAL_BACKOFF = 1  # 1 second
AGENTCORE_MAX_BACKOFF = 8  # 8 seconds
AGENTCORE_CIRCUIT_BREAKER_THRESHOLD = 3  # Failures before circuit opens
AGENTCORE_CIRCUIT_BREAKER_RECOVERY = 60  # Seconds before trying again
AGENTCORE_CACHE_TTL_SECONDS = 86400  # 24 hours
AGENTCORE_MAX_CONCURRENT_CALLS = 2


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Stop trying, use fallback
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class AnalysisValidationError(Exception):
    """Raised when analysis response fails validation."""
    field: str
    reason: str

    def __str__(self):
        return f"Validation error in {self.field}: {self.reason}"


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """Circuit breaker for AgentCore calls.

    Prevents hammering a failing service by:
    1. Tracking consecutive failures
    2. Opening circuit when threshold reached
    3. Allowing recovery attempts after delay
    """

    def __init__(self, failure_threshold: int, recovery_timeout: int):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self._lock = threading.Lock()

    def record_success(self):
        """Record successful call - reset failure count."""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            logger.debug("Circuit breaker: Success, resetting failure count")

    def record_failure(self):
        """Record failed call - increment failure count."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN: {self.failure_count} consecutive failures")
            else:
                logger.debug(f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold}")

    def is_open(self) -> bool:
        """Check if circuit should be open.

        Returns:
            True if circuit is open, False if closed or half-open for recovery
        """
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return False

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.recovery_timeout:
                        self.state = CircuitState.HALF_OPEN
                        logger.info("Circuit breaker HALF_OPEN: Attempting recovery")
                        return False
                return True

            # HALF_OPEN - allow one attempt
            return False


# ============================================================================
# RESPONSE VALIDATOR
# ============================================================================

class ResponseValidator:
    """Validates AgentCore response schema and content."""

    # Required fields in response
    REQUIRED_FIELDS = {
        "complexity_score": (int, float),
        "technologies": (list,),
        "patterns": (list,),
        "skill_level": (str,),
        "recommendations": (list,),
        "reasoning": (str,),
    }

    # Valid skill levels
    VALID_SKILL_LEVELS = {"beginner", "intermediate", "advanced", "expert"}

    @staticmethod
    def validate(response: Dict[str, Any]) -> bool:
        """Validate response schema and content.

        Args:
            response: Response dict from AgentCore

        Returns:
            True if valid

        Raises:
            AnalysisValidationError: If validation fails
        """
        if not isinstance(response, dict):
            raise AnalysisValidationError("root", "Response is not a dictionary")

        # Check required fields
        for field, expected_types in ResponseValidator.REQUIRED_FIELDS.items():
            if field not in response:
                raise AnalysisValidationError(field, f"Missing required field")

            if not isinstance(response[field], expected_types):
                raise AnalysisValidationError(
                    field,
                    f"Expected {expected_types}, got {type(response[field])}"
                )

        # Validate complexity score
        score = response["complexity_score"]
        if not (0 <= score <= 10):
            raise AnalysisValidationError(
                "complexity_score",
                f"Score must be 0-10, got {score}"
            )

        # Validate skill level
        skill = response["skill_level"].lower()
        if skill not in ResponseValidator.VALID_SKILL_LEVELS:
            raise AnalysisValidationError(
                "skill_level",
                f"Must be one of {ResponseValidator.VALID_SKILL_LEVELS}, got {skill}"
            )

        # Validate technologies is non-empty list of strings
        if not response["technologies"]:
            raise AnalysisValidationError("technologies", "Must contain at least one technology")

        if not all(isinstance(t, str) for t in response["technologies"]):
            raise AnalysisValidationError("technologies", "All items must be strings")

        # Validate patterns is list of strings
        if not all(isinstance(p, str) for p in response["patterns"]):
            raise AnalysisValidationError("patterns", "All items must be strings")

        # Validate recommendations structure
        for i, rec in enumerate(response["recommendations"]):
            if not isinstance(rec, dict):
                raise AnalysisValidationError(
                    f"recommendations[{i}]",
                    "Recommendation must be a dictionary"
                )

            required_rec_fields = {"title", "description", "readiness", "why"}
            if not required_rec_fields.issubset(rec.keys()):
                missing = required_rec_fields - set(rec.keys())
                raise AnalysisValidationError(
                    f"recommendations[{i}]",
                    f"Missing fields: {missing}"
                )

        return True


# ============================================================================
# CACHE MANAGER
# ============================================================================

class CacheManager:
    """Caches AgentCore results by repo hash."""

    def __init__(self, ttl_seconds: int = AGENTCORE_CACHE_TTL_SECONDS):
        """Initialize cache.

        Args:
            ttl_seconds: Time-to-live for cached entries
        """
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple] = {}  # {repo_hash: (result, timestamp)}
        self._lock = threading.Lock()

    def get_key(self, repo_path: str) -> str:
        """Generate cache key from repo path.

        Args:
            repo_path: Path to repository

        Returns:
            SHA256 hash of normalized path
        """
        normalized = Path(repo_path).resolve().as_posix()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired.

        Args:
            repo_path: Path to repository

        Returns:
            Cached result or None if not found/expired
        """
        key = self.get_key(repo_path)

        with self._lock:
            if key not in self._cache:
                return None

            result, timestamp = self._cache[key]
            elapsed = time.time() - timestamp

            if elapsed > self.ttl:
                del self._cache[key]
                logger.debug(f"Cache expired for {Path(repo_path).name}")
                return None

            logger.debug(f"Cache hit for {Path(repo_path).name} (age: {elapsed:.0f}s)")
            return result

    def set(self, repo_path: str, result: Dict[str, Any]):
        """Cache result.

        Args:
            repo_path: Path to repository
            result: Analysis result to cache
        """
        key = self.get_key(repo_path)

        with self._lock:
            self._cache[key] = (result, time.time())
            logger.debug(f"Cached result for {Path(repo_path).name}")


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Limits concurrent AgentCore calls."""

    def __init__(self, max_concurrent: int = AGENTCORE_MAX_CONCURRENT_CALLS):
        """Initialize rate limiter.

        Args:
            max_concurrent: Maximum concurrent calls
        """
        self.max_concurrent = max_concurrent
        self._semaphore = threading.Semaphore(max_concurrent)

    def acquire(self) -> bool:
        """Acquire slot for API call.

        Returns:
            True if slot acquired, False if would exceed limit
        """
        return self._semaphore.acquire(blocking=True, timeout=0.1)

    def release(self):
        """Release slot after call completes."""
        self._semaphore.release()


# ============================================================================
# AGENTCORE CALLER
# ============================================================================

class AgentCoreCaller:
    """Production-grade AgentCore caller with resilience patterns.

    Implements:
    - Retry logic with exponential backoff
    - Circuit breaker for resilience
    - Request timeouts
    - Response validation
    - Caching
    - Rate limiting
    - Structured logging
    """

    def __init__(self):
        """Initialize AgentCore caller with resilience components."""
        self.region = AWS_REGION
        self.account_id = AWS_ACCOUNT_ID

        # Resilience components
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=AGENTCORE_CIRCUIT_BREAKER_THRESHOLD,
            recovery_timeout=AGENTCORE_CIRCUIT_BREAKER_RECOVERY
        )
        self.cache = CacheManager(ttl_seconds=AGENTCORE_CACHE_TTL_SECONDS)
        self.rate_limiter = RateLimiter(max_concurrent=AGENTCORE_MAX_CONCURRENT_CALLS)

        # AWS client
        self.client = None
        self._init_client()

        logger.info(f"✅ AgentCore caller initialized (region: {self.region})")

    def _init_client(self):
        """Initialize AWS Bedrock AgentCore client."""
        try:
            self.client = boto3.client(
                'bedrock-agent-runtime',
                region_name=self.region
            )
            logger.debug("✅ Bedrock client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None

    def _validate_config(self) -> bool:
        """Validate configuration at runtime.

        Returns:
            True if config valid

        Raises:
            ValueError: If critical config missing
        """
        from config import AGENTCORE_AGENT_ID, AGENTCORE_AGENT_ALIAS

        if not AGENTCORE_AGENT_ID:
            logger.error("AGENTCORE_AGENT_ID not configured")
            return False

        if not AGENTCORE_AGENT_ALIAS:
            logger.error("AGENTCORE_AGENT_ALIAS not configured")
            return False

        if not self.client:
            logger.warning("Bedrock client not initialized")
            return False

        return True

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository with full resilience and validation.

        This is the main entry point. It handles:
        1. Cache lookup
        2. Rate limiting
        3. Retry logic
        4. Circuit breaker
        5. Response validation
        6. Fallback to mock

        Args:
            repo_path: Path to git repository

        Returns:
            Analysis dictionary with all required fields
        """
        repo_name = Path(repo_path).name
        start_time = time.time()

        # Step 1: Check cache
        cached = self.cache.get(repo_path)
        if cached:
            logger.info(f"✅ {repo_name}: Analysis from cache (source: cached)")
            return cached

        # Step 2: Check circuit breaker
        if self.circuit_breaker.is_open():
            logger.warning(f"⚠️  {repo_name}: Circuit breaker open, using mock analysis")
            return self._mock_analysis(repo_path)

        # Step 3: Validate config
        if not self._validate_config():
            logger.warning(f"⚠️  {repo_name}: Config invalid, using mock analysis")
            return self._mock_analysis(repo_path)

        # Step 4: Try AgentCore with retries
        result = self._analyze_with_retries(repo_path)

        if result:
            # Success - cache and return
            self.circuit_breaker.record_success()
            self.cache.set(repo_path, result)
            elapsed = time.time() - start_time
            logger.info(f"✅ {repo_name}: AgentCore analysis complete ({elapsed:.1f}s, source: real)")
            return result
        else:
            # Failed - record failure and fallback
            self.circuit_breaker.record_failure()
            logger.warning(f"⚠️  {repo_name}: AgentCore failed after retries, using mock")
            return self._mock_analysis(repo_path)

    def _analyze_with_retries(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Attempt analysis with retry logic and backoff.

        Args:
            repo_path: Path to repository

        Returns:
            Analysis result or None if all retries failed
        """
        repo_name = Path(repo_path).name

        for attempt in range(1, AGENTCORE_MAX_RETRIES + 1):
            try:
                # Rate limit
                if not self.rate_limiter.acquire():
                    logger.debug(f"{repo_name}: Rate limited, waiting...")
                    time.sleep(0.5)
                    if not self.rate_limiter.acquire():
                        logger.warning(f"{repo_name}: Could not acquire rate limit slot")
                        return None

                try:
                    # Build prompt
                    prompt = self._build_prompt(repo_path)

                    # Call AgentCore
                    logger.debug(f"{repo_name}: Calling AgentCore (attempt {attempt}/{AGENTCORE_MAX_RETRIES})")
                    result_text = self._call_agentcore(prompt)

                    # Parse response
                    response = self._extract_json(result_text)
                    if not response:
                        logger.warning(f"{repo_name}: Could not parse response")
                        continue

                    # Validate response
                    try:
                        ResponseValidator.validate(response)
                        response["source"] = "real"
                        logger.debug(f"{repo_name}: Response validated successfully")
                        return response
                    except AnalysisValidationError as e:
                        logger.warning(f"{repo_name}: Validation failed - {e}")
                        continue

                finally:
                    self.rate_limiter.release()

            except (ConnectTimeoutError, ReadTimeoutError) as e:
                logger.warning(f"{repo_name}: Timeout on attempt {attempt} - {type(e).__name__}")
                if attempt < AGENTCORE_MAX_RETRIES:
                    backoff = self._calculate_backoff(attempt)
                    logger.debug(f"{repo_name}: Backing off {backoff}s before retry")
                    time.sleep(backoff)

            except ClientError as e:
                error_code = e.response['Error']['Code']
                logger.error(f"{repo_name}: ClientError ({error_code}) on attempt {attempt}")

                # Don't retry on certain errors
                if error_code in ["ValidationException", "ResourceNotFoundException"]:
                    logger.error(f"{repo_name}: Non-retryable error, stopping")
                    return None

                if attempt < AGENTCORE_MAX_RETRIES:
                    backoff = self._calculate_backoff(attempt)
                    time.sleep(backoff)

            except Exception as e:
                logger.error(f"{repo_name}: Unexpected error on attempt {attempt} - {type(e).__name__}: {e}")
                if attempt < AGENTCORE_MAX_RETRIES:
                    backoff = self._calculate_backoff(attempt)
                    time.sleep(backoff)

        logger.error(f"{repo_name}: All {AGENTCORE_MAX_RETRIES} retries exhausted")
        return None

    def _call_agentcore(self, prompt: str) -> str:
        """Call AgentCore API with timeout.

        Args:
            prompt: Analysis prompt

        Returns:
            Response text

        Raises:
            Various boto3 exceptions on failure
        """
        from config import AGENTCORE_AGENT_ID, AGENTCORE_AGENT_ALIAS

        response = self.client.invoke_agent(
            agentId=AGENTCORE_AGENT_ID,
            agentAliasId=AGENTCORE_AGENT_ALIAS,
            sessionId=f"janus-clew-{int(time.time())}",
            inputText=prompt
        )

        # Parse stream response
        result_text = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk_data = event['chunk'].get('bytes', b'')
                if isinstance(chunk_data, bytes):
                    result_text += chunk_data.decode('utf-8', errors='ignore')
                else:
                    result_text += str(chunk_data)

        return result_text

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter.

        Args:
            attempt: Attempt number (1-based)

        Returns:
            Seconds to wait
        """
        # Exponential: 1s, 2s, 4s
        backoff = min(AGENTCORE_INITIAL_BACKOFF * (2 ** (attempt - 1)), AGENTCORE_MAX_BACKOFF)
        # Add small random jitter to avoid thundering herd
        import random
        jitter = random.uniform(0, backoff * 0.1)
        return backoff + jitter

    def _build_prompt(self, repo_path: str) -> str:
        """Build analysis prompt for AgentCore.

        Args:
            repo_path: Path to repository

        Returns:
            Formatted prompt for AgentCore agent
        """
        repo_name = Path(repo_path).name

        prompt = f"""Analyze this GitHub repository and provide a comprehensive assessment.

Repository: {repo_name}
Path: {repo_path}

Analyze the repository structure and provide a JSON response with:

{{
    "complexity_score": <number 0-10, based on codebase size, architecture depth, patterns>,
    "technologies": [<list of detected technologies from files>],
    "patterns": [<list of development patterns observed, e.g. "You avoid databases", "You favor async patterns">],
    "skill_level": "<beginner|intermediate|advanced|expert>",
    "recommendations": [
        {{
            "title": "<recommendation title>",
            "description": "<why this recommendation based on detected patterns>",
            "readiness": "<ready|soon|later>",
            "why": "<explanation based on code analysis>"
        }}
    ],
    "reasoning": "<brief explanation of scoring>"
}}

CONSTRAINTS:
1. complexity_score MUST be a number between 0 and 10 (inclusive)
2. technologies MUST be a non-empty list of strings
3. patterns MUST be a list of strings
4. skill_level MUST be one of: beginner, intermediate, advanced, expert
5. recommendations MUST be a list of objects with title, description, readiness, why
6. Return ONLY valid JSON, no other text

Scoring guide:
- 0-2: Simple scripts or templates
- 3-4: Small projects with basic structure
- 5-6: Medium complexity with some patterns
- 7-8: Advanced architecture with clear patterns
- 9-10: Enterprise-grade or highly complex systems

For patterns, look at:
- Database usage (or lack thereof)
- Async/sync approaches
- Architecture patterns (monolith, microservices, etc)
- Testing approach
- Code organization

For recommendations, consider the developer's current trajectory and suggest what they should learn next based on what they already know.
"""
        return prompt

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from response text.

        Args:
            text: Response text from AgentCore

        Returns:
            Parsed JSON dict or None if extraction failed
        """
        if not text:
            return None

        try:
            # Try direct parse first
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        try:
            # Try extracting JSON from text
            start = text.find('{')
            end = text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.debug(f"Could not extract JSON from response: {e}")

        return None

    def _mock_analysis(self, repo_path: str) -> Dict[str, Any]:
        """Return realistic mock analysis when AgentCore unavailable.

        Args:
            repo_path: Path to repository

        Returns:
            Mock analysis dictionary
        """
        repo_name = Path(repo_path).name

        # Mock data varies by repo name
        mock_data = {
            "Ariadne-Clew": {
                "complexity_score": 7.2,
                "technologies": ["Python", "AWS Bedrock", "FastAPI", "AgentCore"],
                "patterns": [
                    "You build well-structured async systems",
                    "You favor cloud-native architecture",
                    "You integrate AI agents effectively"
                ],
                "skill_level": "advanced",
                "recommendations": [
                    {
                        "title": "Event-Driven Architecture",
                        "description": "Your async patterns + cloud background make you ready for Kafka/SQS",
                        "readiness": "ready",
                        "why": "You already think in async - event streams are natural next step"
                    }
                ],
                "reasoning": "Advanced async architecture with clear AI integration patterns"
            },
            "TicketGlass": {
                "complexity_score": 8.1,
                "technologies": ["TypeScript", "React", "AWS", "AgentCore"],
                "patterns": [
                    "You build production-grade systems",
                    "You avoid over-engineering",
                    "You think about scalability from start"
                ],
                "skill_level": "advanced",
                "recommendations": [
                    {
                        "title": "Distributed Systems",
                        "description": "Your production experience + scale thinking prepare you for microservices",
                        "readiness": "ready",
                        "why": "You've proven you can build systems that work at scale"
                    }
                ],
                "reasoning": "Production-grade system with clear performance optimization"
            }
        }

        # Return mock or generic
        if repo_name in mock_data:
            result = mock_data[repo_name].copy()
        else:
            result = {
                "complexity_score": 6.5,
                "technologies": ["Python", "Git"],
                "patterns": ["Steady coder", "Learning continuously"],
                "skill_level": "intermediate",
                "recommendations": [
                    {
                        "title": "Continue Building",
                        "description": "Keep shipping projects to grow your skills",
                        "readiness": "now",
                        "why": "The best way to learn is by building real things"
                    }
                ],
                "reasoning": "Growing coder with solid foundations"
            }

        result["source"] = "mock"
        return result
