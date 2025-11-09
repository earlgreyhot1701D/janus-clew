"""Janus Clew Logging - Structured logging setup with colored output."""

import logging
import sys
from typing import Optional
from datetime import datetime

from config import LOG_FORMAT, LOG_LEVEL, DEBUG


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[41m",   # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        """Format record with colors and timestamp."""
        # Add timestamp if not present
        if not hasattr(record, "asctime"):
            record.asctime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get color for this level
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format with color
        levelname = record.levelname
        record.levelname = f"{color}{levelname}{self.RESET}"

        # Call parent formatter
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = levelname
        
        return result


class ContextFilter(logging.Filter):
    """Add context to log records."""

    def __init__(self, context: Optional[dict] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record):
        """Add context to record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def setup_logging(
    name: str = "janus-clew",
    level: Optional[str] = None,
    context: Optional[dict] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """Setup logger with consistent formatting and optional colors.

    Args:
        name: Logger name (typically __name__)
        level: Log level override (DEBUG, INFO, WARNING, ERROR)
        context: Additional context to include in logs
        use_colors: Enable colored output in console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure once
    if logger.handlers:
        return logger

    # Set level
    log_level = getattr(logging, level or LOG_LEVEL)
    logger.setLevel(log_level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Formatter
    if use_colors:
        formatter = ColoredFormatter(LOG_FORMAT)
    else:
        formatter = logging.Formatter(LOG_FORMAT)

    handler.setFormatter(formatter)

    # Add context filter if provided
    if context:
        handler.addFilter(ContextFilter(context))

    logger.addHandler(handler)

    # Prevent propagation
    logger.propagate = False

    return logger


# Module-level logger
logger = setup_logging(__name__)


def get_logger(name: str, context: Optional[dict] = None, use_colors: bool = True) -> logging.Logger:
    """Get a logger with optional context and colored output.

    Args:
        name: Logger name (typically __name__)
        context: Additional context dictionary
        use_colors: Enable colored output

    Returns:
        Configured logger instance
    """
    log = logging.getLogger(name)
    
    if not log.handlers:
        setup_logging(name, context=context, use_colors=use_colors)

    if context:
        log.addFilter(ContextFilter(context))

    return log
