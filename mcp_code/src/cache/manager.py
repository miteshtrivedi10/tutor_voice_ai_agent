"""
Cache module for the MCP Server
Handles in-memory caching with TTL support
"""

from datetime import timedelta
from theine import Cache
from src.config.settings import Config
from src.config.logging import logger


class CacheManager:
    """Manages in-memory caching with TTL support"""

    def __init__(self):
        """Initialize the cache with configured size"""
        self.cache = Cache(Config.CACHE_MAXSIZE)
        self.default_ttl = timedelta(seconds=Config.CACHE_TTL)
        logger.info(f"Cache initialized with maxsize={Config.CACHE_MAXSIZE}")

    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)

    def set(self, key: str, value, ttl: timedelta = None):
        """Set value in cache with optional TTL"""
        if ttl is None:
            ttl = self.default_ttl
        self.cache.set(key, value, ttl=ttl)
        logger.debug(f"Set cache key: {key} with TTL: {ttl}")

    def delete(self, key: str):
        """Delete value from cache"""
        self.cache.delete(key)
        logger.debug(f"Deleted cache key: {key}")

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")


# Global cache instance
cache_manager = CacheManager()
