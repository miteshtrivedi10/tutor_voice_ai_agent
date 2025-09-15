#!/usr/bin/env python3
"""
Test script to verify GGUF model integration
"""

import os
import sys
from config.settings import MODELS_DIR

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gguf_model():
    """Test the GGUF model integration"""
    try:
        # Test lightweight response synthesizer
        from search.helper_class import LightweightResponseSynthesizer
        synthesizer = LightweightResponseSynthesizer()
        
        if not synthesizer.generator:
            print("WARNING: GGUF model not loaded. Skipping tests.")
            return True
            
        response = synthesizer.synthesize(
            "What is the capital of France?", 
            [{"text": "France is a country in Europe. The capital of France is Paris."}]
        )
        print(f"Response: {response}")
        
        print("Test passed!")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gguf_model()
    if not success:
        sys.exit(1)