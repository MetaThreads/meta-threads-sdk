"""Logging configuration for the Threads SDK."""

from __future__ import annotations

import logging
import sys

# Create the SDK logger
logger = logging.getLogger("threads")

# Default to no output (NullHandler) - users must configure if they want logs
logger.addHandler(logging.NullHandler())


def setup_logging(
    level: int | str = logging.INFO,
    format: str | None = None,
    handler: logging.Handler | None = None,
) -> logging.Logger:
    """Configure logging for the Threads SDK.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Custom format string. If None, uses default format.
        handler: Custom handler. If None, logs to stderr.

    Returns:
        The configured logger.

    Example:
        ```python
        from threads._utils.logger import setup_logging
        import logging

        # Basic setup - logs INFO and above to stderr
        setup_logging()

        # Debug mode - see all API requests
        setup_logging(level=logging.DEBUG)

        # Custom format
        setup_logging(format="%(asctime)s - %(message)s")
        ```
    """
    # Remove existing handlers
    logger.handlers.clear()

    # Set level
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)

    # Create handler
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)

    # Set format
    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Module name to append to 'threads'. If None, returns root SDK logger.

    Returns:
        Logger instance.

    Example:
        ```python
        from threads._utils.logger import get_logger

        logger = get_logger("auth")  # Returns logger named "threads.auth"
        logger.debug("Exchanging auth code")
        ```
    """
    if name is None:
        return logger
    return logging.getLogger(f"threads.{name}")
