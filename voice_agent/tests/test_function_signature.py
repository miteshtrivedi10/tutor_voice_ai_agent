#!/usr/bin/env python3
"""
Test script to verify the function signature of fetch_qna
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function to test its signature
from voice_agent.agent.old_agents_to_be_kept.tutor_agent import TutorVoiceAgent

def test_fetch_qna_signature():
    """Test the fetch_qna function signature"""
    import inspect
    
    # Get the fetch_qna method
    fetch_qna = TutorVoiceAgent.fetch_qna
    
    # Get the signature
    sig = inspect.signature(fetch_qna)
    
    # Check parameters
    params = list(sig.parameters.keys())
    print(f"Function parameters: {params}")
    
    # Check if it has the expected parameters
    expected_params = ['self', 'context', 'subject']
    for param in expected_params:
        if param not in params:
            print(f"ERROR: Missing parameter '{param}'")
            return False
    
    # Check return annotation
    return_annotation = sig.return_annotation
    print(f"Return annotation: {return_annotation}")
    
    print("Function signature test passed!")
    return True

if __name__ == "__main__":
    print("Testing fetch_qna function signature...")
    success = test_fetch_qna_signature()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
        sys.exit(1)