"""
Main module for the MCP Server
Exports all public APIs and tools
"""

from src.config.settings import Config
from src.cache.manager import cache_manager
from src.tools.question_tools import mcp, load_questions, update_question_index
from src.config.logging import logger

# Configure the MCP server for streamable HTTP
def run_server():
    """Run the MCP server with streamable HTTP transport"""
    logger.info(f"Server loaded with 2 tools")
    mcp.custom_route(
        "/mcp_server",
        methods=["GET", "POST"],
    )
    mcp.run(transport="streamable-http")

__all__ = [
    "mcp",
    "load_questions", 
    "update_question_index",
    "cache_manager",
    "Config",
    "run_server"
]