"""
Logging module for the voice tutor application
"""
import logging
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class VoiceTutorLogger:
    """Custom logger for the voice tutor application"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance with the specified name
        
        Args:
            name: Logger name
            level: Log level (defaults to LOG_LEVEL env var or INFO)
            
        Returns:
            Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
            
        logger = logging.getLogger(name)
        
        # Set log level
        log_level = level or os.getenv("LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # If the logger has no handlers, add a console handler
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        cls._loggers[name] = logger
        return logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name
        level: Log level (defaults to LOG_LEVEL env var or INFO)
        
    Returns:
        Logger instance
    """
    return VoiceTutorLogger.get_logger(name, level)