"""
Configuration settings for the Voice Tutor application
Centralized configuration following SOLID principles
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.logging_config import logger


class AppSettings(BaseSettings):
    """Main application settings"""

    # Core application settings
    APP_NAME: str = Field(default="Voice Tutor", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Database/Supabase settings
    SUPABASE_URL: Optional[str] = Field(
        default=None, description="Supabase project URL"
    )
    SUPABASE_KEY: Optional[str] = Field(default=None, description="Supabase anon key")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(
        default=None, description="Supabase service key"
    )
    DATABASE_URL: Optional[str] = Field(
        default=None, description="Database connection URL"
    )

    # LLM Configuration
    LLM_MODEL: str = Field(
        default="meta-llama/llama-3.1-8b-instruct:free",
        description="Primary LLM model for tool calling and conversation",
    )
    LLM_MODEL_NAME: str = Field(
        default="meta-llama/llama-3.1-8b-instruct:free",
        description="Primary LLM model for tool calling and conversation",
    )
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None, description="OpenRouter API key"
    )
    LLM_API_KEY: Optional[str] = Field(
        default=None, description="API key for LLM provider"
    )
    SARVAM_API_KEY: Optional[str] = Field(
        default=None, description="Sarvam AI API key for voice processing"
    )
    TAVILY_API_KEY: Optional[str] = Field(
        default=None, description="Tavily search API key for research tools"
    )
    LLM_BASE_URL: Optional[str] = Field(
        default=None,
        description="Base URL for LLM API (e.g., for local or custom endpoints)",
    )
    LLM_TEMPERATURE: float = Field(default=0.7, description="LLM sampling temperature")
    LLM_MAX_TOKENS: int = Field(
        default=1000, description="Maximum tokens for LLM responses"
    )
    LLM_TIMEOUT: int = Field(default=30, description="LLM request timeout in seconds")

    # LiveKit settings for voice processing
    LIVEKIT_URL: Optional[str] = Field(default=None, description="LiveKit server URL")
    LIVEKIT_API_KEY: Optional[str] = Field(default=None, description="LiveKit API key")
    LIVEKIT_API_SECRET: Optional[str] = Field(
        default=None, description="LiveKit API secret"
    )
    ROOM_NAME: str = Field(default="voice-tutor-room", description="Default room name")
    LK_AGENT_OTEL_AUTH_CODE: Optional[str] = Field(
        default=None, description="LiveKit Agent OpenTelemetry authentication code"
    )
    LK_AGENT_OTEL_ENABLED: bool = Field(
        default=False, description="Enable OpenTelemetry for LiveKit Agent"
    )
    LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(
        default=None, description="LiveKit Agent OpenTelemetry OTLP endpoint"
    )
    LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT: Optional[str] = Field(
        default=None, description="LiveKit Agent OpenTelemetry logs endpoint"
    )
    LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT: Optional[str] = Field(
        default=None, description="LiveKit Agent OpenTelemetry metrics endpoint"
    )
    LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED: bool = Field(
        default=False, description="Enable auto instrumentation for Python logging"
    )
    LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED: bool = Field(
        default=False, description="Enable auto instrumentation for Python metrics"
    )

    # STT/TTS settings (Deepgram)
    DEEPGRAM_API_KEY: Optional[str] = Field(
        default=None, description="Deepgram API key"
    )
    STT_MODEL: str = Field(default="nova-2", description="STT model")
    TTS_MODEL: str = Field(default="nova-2", description="TTS model")
    TTS_VOICE: str = Field(default="en-US-JennyNeural", description="TTS voice")

    # Session and cache settings
    SESSION_CACHE_TTL_MINUTES: int = Field(default=30, description="Session cache TTL")
    CONVERSATION_HISTORY_LIMIT: int = Field(
        default=20, description="Max conversation history items"
    )

    # Quiz and learning settings
    DEFAULT_QUIZ_LENGTH: int = Field(
        default=5, description="Default number of questions per quiz"
    )
    SUPPORTED_SUBJECTS: List[str] = Field(
        default_factory=lambda: ["Science", "English", "Geography"]
    )
    DEFAULT_CHILD_AGE: int = Field(
        default=9, description="Default age for child-friendly responses"
    )
    MAX_QUIZ_QUESTIONS: int = Field(
        default=20, description="Maximum questions per quiz"
    )
    EMERGENCY_QUESTIONS_ENABLED: bool = Field(
        default=True, description="Enable emergency fallback questions"
    )

    # Tool calling settings
    ENABLE_TOOLS: bool = Field(default=True, description="Enable tool calling")
    TOOL_CALL_TIMEOUT: int = Field(default=10, description="Tool execution timeout")

    # Error handling and fallback settings
    MAX_RETRIES: int = Field(default=3, description="Maximum retry attempts")
    RETRY_DELAY_SECONDS: float = Field(default=2.0, description="Initial retry delay")

    # Monitoring and analytics (OpenTelemetry)
    ENABLE_TELEMETRY: bool = Field(
        default=False, description="Enable telemetry collection"
    )
    ENABLE_USAGE_METRICS: bool = Field(default=True, description="Track usage metrics")
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(
        default=None, description="OpenTelemetry OTLP exporter endpoint"
    )
    OTEL_SERVICE_NAME: str = Field(
        default="tutor-voice-agent", description="OpenTelemetry service name"
    )

    # Security settings
    ENABLE_RLS: bool = Field(default=True, description="Enable Row Level Security")
    MAX_SESSION_DURATION_HOURS: int = Field(
        default=2, description="Maximum session duration"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env


# Global settings instance
settings = AppSettings()

# Legacy individual settings for backward compatibility
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL

# Database settings
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
DATABASE_URL = settings.DATABASE_URL

# LLM settings
LLM_MODEL = settings.LLM_MODEL
LLM_MODEL_NAME = settings.LLM_MODEL_NAME
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
LLM_API_KEY = settings.LLM_API_KEY
SARVAM_API_KEY = settings.SARVAM_API_KEY
TAVILY_API_KEY = settings.TAVILY_API_KEY
LLM_BASE_URL = settings.LLM_BASE_URL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
LLM_MAX_TOKENS = settings.LLM_MAX_TOKENS
LLM_TIMEOUT = settings.LLM_TIMEOUT

# LiveKit settings
LIVEKIT_URL = settings.LIVEKIT_URL
LIVEKIT_API_KEY = settings.LIVEKIT_API_KEY
LIVEKIT_API_SECRET = settings.LIVEKIT_API_SECRET
ROOM_NAME = settings.ROOM_NAME
LK_AGENT_OTEL_AUTH_CODE = settings.LK_AGENT_OTEL_AUTH_CODE
LK_AGENT_OTEL_ENABLED = settings.LK_AGENT_OTEL_ENABLED
LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT = settings.LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT
LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT = settings.LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT = settings.LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED = settings.LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED = settings.LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED

# STT/TTS settings
DEEPGRAM_API_KEY = settings.DEEPGRAM_API_KEY
STT_MODEL = settings.STT_MODEL
TTS_MODEL = settings.TTS_MODEL
TTS_VOICE = settings.TTS_VOICE

# Session settings
SESSION_CACHE_TTL_MINUTES = settings.SESSION_CACHE_TTL_MINUTES
CONVERSATION_HISTORY_LIMIT = settings.CONVERSATION_HISTORY_LIMIT

# Learning settings
DEFAULT_QUIZ_LENGTH = settings.DEFAULT_QUIZ_LENGTH
SUPPORTED_SUBJECTS = settings.SUPPORTED_SUBJECTS
DEFAULT_CHILD_AGE = settings.DEFAULT_CHILD_AGE
MAX_QUIZ_QUESTIONS = settings.MAX_QUIZ_QUESTIONS
EMERGENCY_QUESTIONS_ENABLED = settings.EMERGENCY_QUESTIONS_ENABLED

# Tool settings
ENABLE_TOOLS = settings.ENABLE_TOOLS
TOOL_CALL_TIMEOUT = settings.TOOL_CALL_TIMEOUT

# Error handling
MAX_RETRIES = settings.MAX_RETRIES
RETRY_DELAY_SECONDS = settings.RETRY_DELAY_SECONDS

# Monitoring
ENABLE_TELEMETRY = settings.ENABLE_TELEMETRY
ENABLE_USAGE_METRICS = settings.ENABLE_USAGE_METRICS
OTEL_EXPORTER_OTLP_ENDPOINT = settings.OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_SERVICE_NAME = settings.OTEL_SERVICE_NAME

# Security
ENABLE_RLS = settings.ENABLE_RLS
MAX_SESSION_DURATION_HOURS = settings.MAX_SESSION_DURATION_HOURS


def validate_settings() -> bool:
    """
    Validate required settings are present

    Returns:
        True if all required settings are valid
    """
    required_settings = [
        ("LLM_MODEL_NAME", LLM_MODEL_NAME),
        ("LLM_API_KEY", LLM_API_KEY),
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
        ("DEEPGRAM_API_KEY", DEEPGRAM_API_KEY),
        ("LIVEKIT_URL", LIVEKIT_URL),
        ("LIVEKIT_API_KEY", LIVEKIT_API_KEY),
        ("LIVEKIT_API_SECRET", LIVEKIT_API_SECRET),
    ]

    missing_settings = []
    for setting_name, setting_value in required_settings:
        if not setting_value or setting_value == "None":
            missing_settings.append(setting_name)

    if missing_settings:
        logger.error(f"Missing required settings: {', '.join(missing_settings)}")
        logger.error(
            "Please check your .env file and ensure all required environment variables are set"
        )
        return False

    logger.info("All required settings validated successfully")
    return True