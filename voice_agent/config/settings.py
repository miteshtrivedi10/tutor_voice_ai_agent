import os
from pathlib import Path

from dotenv import load_dotenv

# -------------------------
# Config
# -------------------------


# -------------------------
# Config
# -------------------------


BASE_DIR = Path(__file__).resolve().parent.parent  # Points to rag_pipeline/
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path, override=True)

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "your-api-key")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "your-api-secret")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "your-sarvam-api-key")
LLM_API_KEY = os.getenv("GROQ_API_KEY", "your-llm-api-key")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your-tavily-api-key")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "your-deepgram-api-key")
LK_AGENT_OTEL_ENABLED = os.getenv("LK_AGENT_OTEL_ENABLED", False)
LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT", "some-endpoint"
)
LK_AGENT_OTEL_AUTH_CODE = os.getenv("LK_AGENT_OTEL_AUTH_CODE", "some-headers")
LK_AGENT_OTEL_RESOURCE_ATTRIBUTES = os.getenv(
    "LK_AGENT_OTEL_RESOURCE_ATTRIBUTES", "some-resource-attributes"
)
LK_AGENT_EXPORTER_OLTP_PROTOCOL = os.getenv("LK_AGENT_EXPORTER_OLTP_PROTOCOL", "grpc")
LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED = os.getenv(
    "LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "false"
)
LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT = os.getenv(
    "LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "some-endpoint"
)

LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED = os.getenv(
    "LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED", "false"
)
LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT = os.getenv(
    "LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT", "some-endpoint"
)


# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")
