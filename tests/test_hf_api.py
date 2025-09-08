#!/usr/bin/env python3
"""
Test script to verify Hugging Face API integration
"""

import os
import sys
from config.settings import HF_API_TOKEN

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hf_api_integration():
    """Test the Hugging Face API integration"""
    if not HF_API_TOKEN or HF_API_TOKEN == "your-huggingface-api-token":
        print("WARNING: HF_API_TOKEN not set. Skipping API tests.")
        return True
    
    try:
        # Test embedding processor
        from search.helper_class import EmbeddingProcessor
        embedder = EmbeddingProcessor()
        embeddings = embedder.embed_texts(["Hello, world!"])
        print(f"Embedding shape: {len(embeddings[0])}")
        
        # Test lightweight response synthesizer
        from search.helper_class import LightweightResponseSynthesizer
        synthesizer = LightweightResponseSynthesizer()
        response = synthesizer.synthesize(
            "What is the capital of France?", 
            [{"text": "France is a country in Europe. The capital of France is Paris."}]
        )
        print(f"Response: {response}")
        
        print("All tests passed!")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_hf_api_integration()
    if not success:
        sys.exit(1)