"""
User validation utilities for the MCP Server
Contains functions for validating user names against cached valid users
"""

from typing import Dict, Any, Set
from src.cache.manager import cache_manager
from src.config.logging import logger


def validate_user_name(user_id: str) -> Dict[str, Any]:
    """
    Validate that the provided user_id exists in the cached set of valid user_ids.
    This provides O(1) lookup time complexity.
    
    Args:
        user_id (str): The user_id to validate
        
    Returns:
        Dict[str, Any]: A dictionary containing the validation result with status and message
    """
    try:
        logger.info(f"User name validation requested for: {user_id}")
        # Get the set of valid user names from cache (O(1) operation)
        valid_user_names = cache_manager.get_user_names()

        logger.info(f"Valid user names loaded are : {valid_user_names}")
        
        # Check if the cache is empty (which shouldn't happen after initialization)
        if not valid_user_names:
            logger.warning("User name cache is empty")
            return {
                "status": "error",
                "message": "User validation service is temporarily unavailable. Please try again later."
            }
        
        # Check if user_name is provided
        if not user_id or not isinstance(user_id, str):
            logger.warning("Invalid user name provided for validation")
            return {
                "status": "error",
                "message": f"Invalid User Id provided"
            }
        
        # Check if user_name exists in the valid set (O(1) operation)
        if user_id in valid_user_names:
            return {
                "status": "success",
                "message": "User Id is valid"
            }
        else:
            logger.warning(f"User name '{user_id}' not found in valid user set")
            return {
                "status": "error",
                "message": f"User Id '{user_id}' not found"
            }
            
    except Exception as e:
        logger.error(f"Error validating user id: {str(e)}")
        return {
            "status": "error",
            "message": "An error occurred while validating the user id. Please try again."
        }


def get_available_users_message() -> str:
    """
    Get a formatted message with available user names for error responses.
    
    Returns:
        str: A formatted string with available user names
    """
    try:
        valid_user_names = cache_manager.get_user_names()
        if not valid_user_names:
            return "No users available at the moment."
        
        # Convert set to list for indexing
        user_list = list(valid_user_names)
        
        # Show up to 10 user names
        display_list = user_list[:10]
        remaining = len(user_list) - len(display_list)
        
        message = ", ".join(str(name) for name in display_list)
        if remaining > 0:
            message += f" and {remaining} more"
            
        return message
    except Exception as e:
        logger.error(f"Error getting available users message: {str(e)}")
        return "Unable to retrieve user list at the moment."