"""Amazon Q Developer integration with retry logic and error handling."""

import subprocess
import json
import logging
import time
from typing import Dict, Any, Optional

from cli.rate_limiter import RateLimiter
from cli.timeout_handler import warn_if_slow, retry_with_backoff
from cli.logger import setup_logger
from config import (
    AMAZON_Q_CLI_TIMEOUT,
    AMAZON_Q_RETRY_ATTEMPTS,
    AMAZON_Q_RETRY_BACKOFF,
    CLI_USE_MOCK_DATA,
)
from exceptions import AWSQTimeoutError, AWSQRetryError, AWSQNotAvailableError

logger = setup_logger(__name__)


class AmazonQClient:
    """Client for Amazon Q Developer analysis with retry logic and rate limiting."""

    def __init__(self):
        """Initialize Amazon Q client."""
        self.available = self._check_q_available()
        self.timeout = AMAZON_Q_CLI_TIMEOUT
        self.max_retries = AMAZON_Q_RETRY_ATTEMPTS
        self.backoff = AMAZON_Q_RETRY_BACKOFF

        # ✅ GUARDRAIL: Rate limiter to prevent hammering AWS Q
        self.rate_limiter = RateLimiter(max_calls_per_minute=3)

        if not self.available and not CLI_USE_MOCK_DATA:
            logger.warning("Amazon Q CLI not found. Falling back to mock analysis.")

    def _check_q_available(self) -> bool:
        """Check if Amazon Q CLI is available.

        Returns:
            True if amazon-q command is available
        """
        try:
            result = subprocess.run(
                ["amazon-q", "--version"],
                capture_output=True,
                timeout=5,
            )
            available = result.returncode == 0
            logger.debug(f"Amazon Q CLI available: {available}")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug(f"Amazon Q check failed: {e}")
            return False

    def analyze_with_cli(self, repo_path: str) -> Optional[str]:
        """Analyze repository using Amazon Q CLI with retry logic.

        ✅ GUARDRAILS INTEGRATED:
        - Rate limiting (max 3 calls/min)
        - Timeout warnings (60s timeout)
        - Retry with exponential backoff
        - Token tracking

        Args:
            repo_path: Path to repository to analyze

        Returns:
            Natural language analysis from Q, or None if unavailable

        Raises:
            AWSQRetryError: If all retries exhausted
            AWSQTimeoutError: If timeout occurs
        """
        if CLI_USE_MOCK_DATA:
            logger.debug("Using mock analysis (JANUS_USE_MOCK=true)")
            return self._get_mock_analysis(repo_path)

        if not self.available:
            logger.debug("Amazon Q not available, using mock analysis")
            return self._get_mock_analysis(repo_path)

        # ✅ GUARDRAIL: Rate limit before calling Q
        self.rate_limiter.wait_if_needed()

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.max_retries}: Analyzing {repo_path}")
                result = subprocess.run(
                    ["amazon-q", "analyze", repo_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )

                if result.returncode == 0:
                    response_text = result.stdout

                    # ✅ GUARDRAIL: Track tokens used
                    token_count = self._estimate_tokens(response_text)
                    self.rate_limiter.record_tokens(token_count)

                    logger.info(f"✅ Q analyzed {repo_path} ({token_count} tokens)")
                    return response_text

                last_error = result.stderr or "Unknown error"
                logger.warning(f"Q analysis failed: {last_error}")

                # Exponential backoff before retry
                if attempt < self.max_retries:
                    wait_time = self.backoff ** (attempt - 1)
                    logger.debug(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)

            except subprocess.TimeoutExpired:
                last_error = f"Timeout after {self.timeout}s"
                logger.warning(f"⏱️  Q analysis timeout: {last_error}")

                if attempt >= self.max_retries:
                    raise AWSQTimeoutError(self.timeout)

                # Exponential backoff
                wait_time = self.backoff ** (attempt - 1)
                logger.debug(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except Exception as e:
                last_error = str(e)
                logger.error(f"Q analysis error: {e}", exc_info=True)

                if attempt >= self.max_retries:
                    raise AWSQRetryError(self.max_retries, last_error)

                wait_time = self.backoff ** (attempt - 1)
                time.sleep(wait_time)

        # All retries exhausted
        raise AWSQRetryError(self.max_retries, last_error or "Unknown error")

    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse Q's natural language output into structured data.

        Args:
            text: Natural language analysis from Q

        Returns:
            Structured analysis data
        """
        if not text:
            return self._get_mock_structured_data()

        text_lower = text.lower()

        # Detect skill level
        skill_level = "intermediate"
        if "beginner" in text_lower or "learning" in text_lower:
            skill_level = "beginner"
        elif "advanced" in text_lower or "sophisticated" in text_lower:
            skill_level = "advanced"

        # Detect technologies
        technologies = []
        tech_keywords = {
            "bedrock": "AWS Bedrock",
            "agentcore": "AgentCore",
            "langchain": "LangChain",
            "fastapi": "FastAPI",
            "django": "Django",
            "async": "Async/Await",
            "vector": "Vector Search",
            "rag": "RAG",
            "llm": "LLM",
        }

        for keyword, tech in tech_keywords.items():
            if keyword in text_lower:
                technologies.append(tech)

        # Extract complexity
        complexity = 5  # Default
        try:
            import re
            matches = re.findall(r"(\d+)\s*(?:/10|complexity)", text_lower)
            if matches:
                complexity = min(10, max(0, int(matches[0])))
        except Exception as e:
            logger.debug(f"Could not extract complexity: {e}")

        # Detect patterns
        patterns = []
        pattern_keywords = {
            "async": "Async-first architecture",
            "database": "Database-aware design",
            "stateless": "Stateless design",
            "oo": "Object-oriented design",
            "functional": "Functional programming",
        }

        for keyword, pattern in pattern_keywords.items():
            if keyword in text_lower:
                patterns.append(pattern)

        return {
            "skill_level": skill_level,
            "technologies": technologies,
            "complexity": complexity,
            "patterns": patterns,
            "raw_output": text,
        }

    @staticmethod
    def _get_mock_analysis(repo_path: str) -> str:
        """Return mock Q analysis for development/testing.

        Args:
            repo_path: Path to repository

        Returns:
            Mock analysis string
        """
        from pathlib import Path

        repo_name = Path(repo_path).name

        mock_data = {
            "Your-Honor": """This repository demonstrates intermediate Python skills
with AWS Bedrock integration. The developer has used Amazon Bedrock for RAG pipeline
construction with vector search capabilities. Code quality assessment: 6.2/10.""",
            "Ariadne-Clew": """This repository shows advanced agentic AI patterns with AWS
Bedrock and AgentCore integration. The developer has progressed from basic RAG to
sophisticated agent architectures. Code quality assessment: 7.1/10.""",
            "TicketGlass": """This repository demonstrates expert-level implementation of
complex agentic systems. The developer has mastered AWS Bedrock, AgentCore, and
advanced async Python patterns for production deployments. Code quality assessment: 8.1/10.""",
        }

        return mock_data.get(repo_name, mock_data["Ariadne-Clew"])

    @staticmethod
    def _get_mock_structured_data() -> Dict[str, Any]:
        """Return mock structured data for fallback.

        Returns:
            Mock structured analysis data
        """
        return {
            "skill_level": "intermediate",
            "technologies": ["AWS Bedrock", "Python"],
            "complexity": 6,
            "patterns": ["Async-first", "Clean code"],
            "raw_output": "Mock data",
        }

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate tokens in response (~4 chars per token for Claude).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4
