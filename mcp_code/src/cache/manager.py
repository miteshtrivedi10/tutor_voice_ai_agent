"""
Cache module for the MCP Server
Handles in-memory caching with TTL support
"""

from datetime import timedelta
from typing import List, Set
from theine import Cache
from src.config.settings import Config
from src.config.logging import logger


class CacheManager:
    """Manages in-memory caching with TTL support"""

    def __init__(self):
        """Initialize the cache with configured size"""
        self.cache = Cache(Config.CACHE_MAXSIZE)
        self.default_ttl = timedelta(hours=1)
        logger.info(f"Cache initialized with maxsize={Config.CACHE_MAXSIZE}")

    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)[0]

    def set(self, key: str, value, ttl: timedelta = None):
        """Set value in cache with optional TTL"""
        if ttl is None:
            ttl = self.default_ttl
        self.cache.set(key, value, ttl=ttl)
        logger.debug(f"Set cache key: {key} with TTL: {ttl}")

    def set_permanent(self, key: str, value):
        """Set value in cache with no expiration"""
        self.cache.set(key, value, ttl=None)
        logger.debug(f"Set permanent cache key: {key}")

    def delete(self, key: str):
        """Delete value from cache"""
        self.cache.delete(key)
        logger.debug(f"Deleted cache key: {key}")

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")

    def set_user_names(self, user_names: List[str]):
        """Set the set of valid user names in cache permanently"""
        user_names_set = set(user_names)
        self.set_permanent("valid_user_names", user_names_set)
        logger.info(f"Stored {len(user_names_set)} user names in cache as a set")

    def get_user_names(self) -> Set[str]:
        """Get the set of valid user names from cache"""
        user_names = self.get("valid_user_names")
        # Handle different possible return types from cache
        if user_names is None:
            return set()
        elif isinstance(user_names, tuple) and len(user_names) >= 2:
            # If it's a tuple, the actual value is likely the first element
            if isinstance(user_names[0], set):
                return user_names[0]
            elif isinstance(user_names[0], list):
                return set(user_names[0])
        elif isinstance(user_names, set):
            return user_names
        elif isinstance(user_names, list):
            return set(user_names)
        # If we can't determine the type, return empty set
        return set()


# Global cache instance
cache_manager = CacheManager()
