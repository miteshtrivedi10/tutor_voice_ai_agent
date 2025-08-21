"""
Logging configuration module using loguru.
This module sets up the loguru logger as the standard logger for the application.
"""
import sys
import os
from loguru import logger

# Remove default handlers
logger.remove()

# Add custom handler with desired format
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
    colorize=True,
)

# Add file handler for worker logs
logger.add(
    "/tmp/worker.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="10 MB",
    retention="1 week",
)

# Optionally, add file handler for error logs
logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="1 month",
)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Re-export logger as the standard logger
__all__ = ["logger"]