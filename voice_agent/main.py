#!/usr/bin/env python3
"""
Voice Agent Worker

This script runs as a separate process and handles all voice agent logic.
It connects to LiveKit and waits for jobs to create voice agents.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from livekit.agents import Worker, WorkerOptions
from config.logging_config import logger
from config.settings import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
from tutor_agent import agent_entrypoint

# Load environment variables
_ = load_dotenv(dotenv_path=".env", override=True)

# Configure LiveKit logging to use our logging setup

# Set LiveKit log level from environment variable
livekit_log_level = os.getenv("LIVEKIT_LOG_LEVEL", "INFO")
logging.getLogger("livekit").setLevel(livekit_log_level)
logging.getLogger("livekit.agents").setLevel(livekit_log_level)
logging.getLogger("livekit.plugins").setLevel(livekit_log_level)


async def main():
    """Main entrypoint for the worker"""
    logger.info("Starting Voice Agent Worker...")

    # Create worker with limited processes to avoid duplicated logs
    worker = Worker(
        WorkerOptions(
            entrypoint_fnc=agent_entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            initialize_process_timeout=10.0,  # Keep reasonable timeout
            agent_name="Voice Agent",
        )
    )

    # Run the worker
    logger.info("Worker started, waiting for jobs...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
