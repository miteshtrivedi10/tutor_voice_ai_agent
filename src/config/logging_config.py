"""
Logging configuration module for the voice tutor application
"""
from src.logging.logger import get_logger


# Create a default logger
logger = get_logger(__name__)

# Re-export logger as the standard logger
__all__ = ["logger", "get_logger"]
