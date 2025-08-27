#!/usr/bin/env python3
"""
Test script to verify local model integration
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_local_models():
    """Test the local model integration"""
    try:
        # Test embedding processor
        from search.helper_class import EmbeddingProcessor
        embedder = EmbeddingProcessor()
        embeddings = embedder.embed_texts(["Hello, world!"])
        print(f"Embedding shape: {len(embeddings[0])}")
        
        # Test cross-encoder
        from sentence_transformers.cross_encoder import CrossEncoder
        from config.settings import MODELS_DIR
        cross_encoder = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-2-v2",
            cache_folder=MODELS_DIR,
            local_files_only=True,
        )
        scores = cross_encoder.predict([["What is the capital of France?", "The capital of France is Paris."]])
        print(f"Cross-encoder score: {scores[0]}")
        
        # Test lightweight response synthesizer
        from search.helper_class import LightweightResponseSynthesizer
        synthesizer = LightweightResponseSynthesizer()
        if synthesizer.generator:
            response = synthesizer.synthesize(
                "What is the capital of France?", 
                [{"text": "France is a country in Europe. The capital of France is Paris."}]
            )
            print(f"Response: {response}")
        else:
            print("Using template-based response synthesis")
        
        print("All tests passed!")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_local_models()
    if not success:
        sys.exit(1)