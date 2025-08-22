import os

# -------------------------
# Config
# -------------------------
# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "knowledge")

# Text embedding model (open-source, strong general-purpose, 1024+ dimensions).
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# Vision-language model for diagram/photo explanation
# Using a CPU-friendly model for better performance
VLM_MODEL_NAME = os.getenv("VLM_MODEL", "Salesforce/blip-image-captioning-base")

# Storage directories
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Directory for downloaded models
MODELS_DIR = os.getenv("MODELS_DIR", "./downloaded_models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Directory for image captures
IMAGE_CAPTURES_DIR = os.getenv("IMAGE_CAPTURES_DIR", "./image_captures")
os.makedirs(IMAGE_CAPTURES_DIR, exist_ok=True)

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "your-api-key")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "your-api-secret")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "your-sarvam-api-key")
LLM_API_KEY = os.getenv("GROQ_API_KEY", "your-llm-api-key")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your-tavily-api-key")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "your-deepgram-api-key")
