"""
Main module for the MCP Server
Exports all public APIs and tools
"""

from src.config.settings import Config
from src.cache.manager import cache_manager
from src.tools.question_tools import mcp, start_quiz

__all__ = [
    "mcp",
    "start_quiz",
    "cache_manager",
    "Config",
]
