"""
Configuration manager for the voice tutor application
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Any

from src.config.settings import (
    BASE_DIR,
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    SARVAM_API_KEY,
    LLM_API_KEY,
    TAVILY_API_KEY,
    DEEPGRAM_API_KEY,
    LK_AGENT_OTEL_ENABLED,
    LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT,
    LK_AGENT_OTEL_AUTH_CODE,
    LK_AGENT_OTEL_RESOURCE_ATTRIBUTES,
    LK_AGENT_EXPORTER_OLTP_PROTOCOL,
    LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED,
    LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT,
    LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED,
    LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
    SUPABASE_URL,
    SUPABASE_KEY,
)


class ConfigManager:
    """Manages application configuration"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        self.base_dir = BASE_DIR
        self.livekit_url = LIVEKIT_URL
        self.livekit_api_key = LIVEKIT_API_KEY
        self.livekit_api_secret = LIVEKIT_API_SECRET
        self.sarvam_api_key = SARVAM_API_KEY
        self.llm_api_key = LLM_API_KEY
        self.tavily_api_key = TAVILY_API_KEY
        self.deepgram_api_key = DEEPGRAM_API_KEY
        
        # OpenTelemetry configuration
        self.otel_enabled = LK_AGENT_OTEL_ENABLED
        self.otel_exporter_otlp_endpoint = LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT
        self.otel_auth_code = LK_AGENT_OTEL_AUTH_CODE
        self.otel_resource_attributes = LK_AGENT_OTEL_RESOURCE_ATTRIBUTES
        self.otel_exporter_protocol = LK_AGENT_EXPORTER_OLTP_PROTOCOL
        self.otel_logging_auto_instrumentation_enabled = LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
        self.otel_exporter_otlp_logs_endpoint = LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
        self.otel_metrics_auto_instrumentation_enabled = LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED
        self.otel_exporter_otlp_metrics_endpoint = LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
        
        # Supabase configuration
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        
        self._initialized = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        setattr(self, key, value)


def get_config_manager() -> ConfigManager:
    """Get the singleton config manager instance"""
    return ConfigManager()