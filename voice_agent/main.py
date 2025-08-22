#!/usr/bin/env python3
"""
Voice Agent Worker

This script runs as a separate process and handles all voice agent logic.
It connects to LiveKit and waits for jobs to create voice agents.
"""

import asyncio
import os
from dotenv import load_dotenv
from livekit.agents import JobContext, Worker, WorkerOptions
from core.tutor_agent import agent_entrypoint
from config.settings import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, MODELS_DIR
from config.logging_config import logger

# Load environment variables
_ = load_dotenv(dotenv_path=".env", override=True)


async def main():
    """Main entrypoint for the worker"""
    logger.info("Starting Voice Agent Worker...")
    
    # Ensure all models are downloaded before starting the worker
    # Check if models are already loaded to avoid duplicate loading
    models_already_loaded = False
    try:
        # Try to import search components to check if models are already loaded
        from search.helper_class import EmbeddingProcessor
        # If we can import the class without triggering model loading, models might be loaded
        # For now, we'll be conservative and always run download_models to ensure models are available
        logger.info("Proceeding with model download to ensure all models are available")
    except ImportError:
        logger.info("Search components not yet available, will run model download")
    
    # Always run download_models to ensure models are available (with proper delays)
    try:
        from download_models import download_models
        success = download_models()
        if not success:
            logger.error("Failed to download required models. Exiting...")
            return
        logger.info("All required models are available")
    except Exception as e:
        logger.error(f"Error during model download process: {e}")
        return

    # Create worker
    worker = Worker(
        WorkerOptions(
            entrypoint_fnc=agent_entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )

    # Run the worker
    logger.info("Worker started, waiting for jobs...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())