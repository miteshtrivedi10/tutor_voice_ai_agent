#!/usr/bin/env python3
"""
Script to download the GGUF model file for Phi-3 Mini
"""

import os
import urllib.request
from config.settings import MODELS_DIR
from config.logging_config import logger

def download_gguf_model():
    """Download the GGUF model file if it doesn't exist"""
    # URL for the Phi-3 Mini GGUF model (Q4_K_M quantization)
    model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    
    # Local path for the model file
    local_model_path = os.path.join(MODELS_DIR, "phi-3-mini-4k-instruct.Q4_K_M.gguf")
    
    # Check if the model file already exists
    if os.path.exists(local_model_path):
        logger.info("GGUF model file already exists")
        return True
    
    # Download the model file
    try:
        logger.info(f"Downloading GGUF model from: {model_url}")
        urllib.request.urlretrieve(model_url, local_model_path)
        logger.info("GGUF model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error downloading GGUF model: {e}")
        return False

if __name__ == "__main__":
    success = download_gguf_model()
    if not success:
        exit(1)