#!/usr/bin/env python3
"""
Voice Agent Worker

This script runs as a separate process and handles all voice agent logic.
It connects to LiveKit and waits for jobs to create voice agents.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit.agents import JobContext, Worker, WorkerOptions
from tutor_agent import agent_entrypoint

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/tmp/worker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "your-api-key")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "your-api-secret")

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
        )
    )
    
    # Run the worker
    logger.info("Worker started, waiting for jobs...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
