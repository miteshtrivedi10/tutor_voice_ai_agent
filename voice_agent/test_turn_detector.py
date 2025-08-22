#!/usr/bin/env python3
"""
Test script to verify turn-detector model initialization
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
_ = load_dotenv(dotenv_path=".env", override=True)

from config.settings import MODELS_DIR
from config.logging_config import logger

# Set HF_HOME to ensure models are loaded from the correct directory
os.environ["HF_HOME"] = MODELS_DIR

logger.info(f"MODELS_DIR: {MODELS_DIR}")
logger.info(f"HF_HOME: {os.environ.get('HF_HOME')}")

try:
    logger.info("Attempting to import EnglishModel...")
    from livekit.plugins.turn_detector.english import EnglishModel
    logger.info("EnglishModel imported successfully")
    
    logger.info("Attempting to initialize EnglishModel...")
    model = EnglishModel()
    logger.info("EnglishModel initialized successfully!")
    
    print("Turn detector model test passed!")
    
except Exception as e:
    logger.error(f"Error testing turn detector model: {e}")
    print(f"Turn detector model test failed: {e}")
    sys.exit(1)