#!/usr/bin/env python3
"""
Test script to verify turn-detector model is properly downloaded and structured
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import MODELS_DIR

def check_model_files():
    """Check if all required model files exist"""
    model_path = Path(MODELS_DIR) / "hub" / "models--livekit--turn-detector"
    
    if not model_path.exists():
        print(f"Error: Turn-detector model directory not found at {model_path}")
        return False
    
    # Check if refs directory exists
    refs_path = model_path / "refs"
    if not refs_path.exists():
        print(f"Error: refs directory not found at {refs_path}")
        return False
    
    # Check if v1.2.2-en ref exists
    ref_file = refs_path / "v1.2.2-en"
    if not ref_file.exists():
        print(f"Error: v1.2.2-en ref file not found at {ref_file}")
        return False
    
    # Read the ref to get the snapshot hash
    try:
        with open(ref_file, 'r') as f:
            snapshot_hash = f.read().strip()
    except Exception as e:
        print(f"Error reading ref file: {e}")
        return False
    
    # Check if snapshot directory exists
    snapshot_path = model_path / "snapshots" / snapshot_hash
    if not snapshot_path.exists():
        print(f"Error: snapshot directory not found at {snapshot_path}")
        return False
    
    # Check if required files exist in snapshot
    required_files = [
        "config.json",
        "tokenizer.json",
        "onnx/model_q8.onnx"
    ]
    
    for file in required_files:
        file_path = snapshot_path / file
        if not file_path.exists():
            print(f"Error: Required file not found at {file_path}")
            return False
    
    print("All required turn-detector model files found!")
    return True

if __name__ == "__main__":
    print(f"Checking turn-detector model files in {MODELS_DIR}")
    if check_model_files():
        print("SUCCESS: Turn-detector model is properly downloaded and structured.")
        sys.exit(0)
    else:
        print("FAILURE: Turn-detector model is not properly downloaded or structured.")
        sys.exit(1)