"""
Logging configuration for the MCP Server
Sets up loguru with configuration from environment variables
"""

import sys
import os
from loguru import logger
from src.config.settings import Config

# Remove default handlers
logger.remove()

# Add handler with configuration from .env
logger.add(
    sys.stdout,
    level=Config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    colorize=True
)

# Also log to file
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    os.path.join(log_dir, "mcp_server_{time:YYYY-MM-DD}.log"),
    level=Config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="500 MB",
    retention="10 days"
)

# Export configured logger
__all__ = ["logger"]