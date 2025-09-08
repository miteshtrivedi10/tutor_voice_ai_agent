"""
Logging configuration module using Python's standard logging.
This module sets up logging to work with LiveKit's logging system.
"""

import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_logger(name: str):
    """
    Get a logger instance that works with LiveKit's logging setup.

    Args:
        name: The name of the logger (typically __name__ from the calling module)

    Returns:
        A configured logger instance
    """
    if name is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)

    # Set log level from environment variable or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # If the logger has no handlers, add a console handler
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Create a default logger
logger = get_logger(__name__)

# Re-export logger as the standard logger
__all__ = ["logger", "get_logger"]
