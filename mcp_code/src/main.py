#!/usr/bin/env python3
"""
Main entry point for the MCP Server
"""

from src.cache.manager import cache_manager
from src.config.logging import logger
from src.supabase.client import supabase_client
from src.tools.question_tools import mcp


def initialize_user_cache():
    """Initialize the cache with all user names from the database"""
    try:
        user_names = supabase_client.load_all_unique_user_names()
        cache_manager.set_user_names(user_names)
        logger.info(f"Initialized user cache with {len(user_names)} user names")
    except Exception as e:
        logger.error(f"Failed to initialize user cache: {str(e)}")

# Configure the MCP server for streamable HTTP
def run_server():
    """Run the MCP server with streamable HTTP transport"""
    # Initialize user cache at startup
    initialize_user_cache()
    
    logger.info(f"Server loaded with 2 tools")
    mcp.custom_route(
        "/mcp_server",
        methods=["GET", "POST"],
    )
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    run_server()