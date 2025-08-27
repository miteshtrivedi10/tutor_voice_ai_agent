#!/usr/bin/env python3
"""
Script to ensure all required models are downloaded
"""

import os
import sys
import time
from config.settings import MODELS_DIR
from config.logging_config import logger

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def download_turn_detector_model():
    """Download the turn-detector model if not already present"""
    logger.info("Checking for turn-detector model...")

    # Check if the turn-detector model is already downloaded
    turn_detector_path = os.path.join(
        MODELS_DIR, "hub", "models--livekit--turn-detector"
    )
    if os.path.exists(turn_detector_path):
        logger.info("Turn-detector model already exists")
        return True

    try:
        logger.info("Downloading turn-detector model...")
        from huggingface_hub import snapshot_download

        snapshot_download(
            "livekit/turn-detector", revision="v1.2.2-en", cache_dir=MODELS_DIR
        )
        logger.info("Turn-detector model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error downloading turn-detector model: {e}")
        return False


def preload_models():
    """Preload all required models without downloading if they already exist"""
    logger.info("Starting model preload process...")

    # Import the classes that trigger model loading
    try:
        # Load embedding model
        logger.info("Loading embedding model...")
        from search.helper_class import EmbeddingProcessor

        embedder = EmbeddingProcessor()
        logger.info("Embedding model loaded successfully")

        # Add a delay before loading the next model
        logger.info("Waiting 2 seconds before loading next model...")
        time.sleep(2)

        # Load cross-encoder model
        logger.info("Loading cross-encoder model...")
        from sentence_transformers.cross_encoder import CrossEncoder

        cross_encoder = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-2-v2",
            cache_folder=MODELS_DIR,
            local_files_only=True,
        )
        logger.info("Cross-encoder model loaded successfully")

        # Add a delay before loading the next model
        logger.info("Waiting 2 seconds before loading next model...")
        time.sleep(2)

        # Try to load response synthesis models
        logger.info("Loading response synthesis models...")
        from search.helper_class import LightweightResponseSynthesizer

        synthesizer = LightweightResponseSynthesizer()
        if synthesizer.generator:
            logger.info(f"Response synthesis model loaded: {synthesizer.model_name}")
        else:
            logger.info("Using template-based response synthesis")

        logger.info("All models preloaded successfully!")
        return True

    except Exception as e:
        logger.error(f"Error preloading models: {e}")
        return False


def download_models():
    """Download all required models"""
    logger.info("Starting model download process...")

    # First, download the turn-detector model
    if not download_turn_detector_model():
        logger.error("Failed to download turn-detector model")
        return False

    # Download the GGUF model
    try:
        logger.info("Downloading/loading GGUF model...")
        from download_gguf_model import download_gguf_model
        if not download_gguf_model():
            logger.error("Failed to download GGUF model")
            return False
        logger.info("GGUF model downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading GGUF model: {e}")
        return False

    # Add a delay before loading the next models
    # logger.info("Waiting 5 seconds before loading next models...")
    # time.sleep(5)

    # Import the classes that trigger model downloads
    try:
        # Download embedding model
        logger.info("Downloading/loading embedding model...")
        from search.helper_class import EmbeddingProcessor

        embedder = EmbeddingProcessor()
        logger.info("Embedding model loaded successfully")

        # Add a delay before loading the next model
        # logger.info("Waiting 5 seconds before loading next model...")
        # time.sleep(5)

        # Download cross-encoder model
        logger.info("Downloading/loading cross-encoder model...")
        from sentence_transformers.cross_encoder import CrossEncoder

        cross_encoder = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-2-v2", cache_folder=MODELS_DIR
        )
        logger.info("Cross-encoder model loaded successfully")

        # Add a delay before loading the next model
        # logger.info("Waiting 5 seconds before loading next model...")
        # time.sleep(5)

        # Try to load response synthesis models (they will be downloaded if needed)
        logger.info("Downloading/loading response synthesis models...")
        from search.helper_class import LightweightResponseSynthesizer

        synthesizer = LightweightResponseSynthesizer()
        if synthesizer.generator:
            logger.info(f"Response synthesis model loaded: {synthesizer.model_name}")
        else:
            logger.info("Using template-based response synthesis")

        logger.info("All models downloaded/loaded successfully!")
        return True

    except Exception as e:
        logger.error(f"Error downloading models: {e}")
        return False


if __name__ == "__main__":
    success = download_models()
    if success:
        print("Model download process completed successfully!")
    else:
        print("Model download process failed!")
        sys.exit(1)
