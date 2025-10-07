"""
Configuration module for the MCP Server
Handles loading and validation of environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the MCP Server"""
    
    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Cache configuration
    CACHE_MAXSIZE: int = int(os.getenv("CACHE_MAXSIZE", "1000"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "21600"))  # 15 minutes
    
    # Server configuration
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    SERVER_DEBUG: bool = os.getenv("SERVER_DEBUG", "True").lower() == "true"
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration variables"""
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL must be set in environment variables")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY must be set in environment variables")


# Validate configuration at import time
Config.validate()
