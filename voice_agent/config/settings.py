import os

# -------------------------
# Config
# -------------------------
QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "kb")

# Text embedding model (open-source, strong general-purpose, 1024+ dimensions).
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# Vision-language model for diagram/photo explanation
# Using a CPU-friendly model for better performance
VLM_MODEL_NAME = os.getenv("VLM_MODEL", "Salesforce/blip-image-captioning-base")

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Directory for downloaded models
MODELS_DIR = os.getenv("MODELS_DIR", "./downloaded_models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Directory for image captures
IMAGE_CAPTURES_DIR = os.getenv("IMAGE_CAPTURES_DIR", "./image_captures")
os.makedirs(IMAGE_CAPTURES_DIR, exist_ok=True)