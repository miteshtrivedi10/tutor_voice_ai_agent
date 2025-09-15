"""
Config package init file
"""

from .settings import SUPABASE_URL, SUPABASE_KEY
from .logging_config import logger, get_logger

__all__ = ["SUPABASE_URL", "SUPABASE_KEY", "logger", "get_logger"]