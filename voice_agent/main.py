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
from config.settings import (
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    MODELS_DIR,
)
from config.logging_config import logger

# Load environment variables
_ = load_dotenv(dotenv_path=".env", override=True)


async def main():
    """Main entrypoint for the worker"""
    logger.info("Starting Voice Agent Worker...")

    # Create worker
    worker = Worker(
        WorkerOptions(
            entrypoint_fnc=agent_entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            initialize_process_timeout=30.0,  # Keep reasonable timeout
        )
    )

    # Run the worker
    logger.info("Worker started, waiting for jobs...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
