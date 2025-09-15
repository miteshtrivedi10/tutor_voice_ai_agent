#!/usr/bin/env python3
"""
Test script to verify Supabase integration and answer evaluation
"""

import asyncio
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.supabase_client import get_supabase_qna_client
from core.answer_evaluator import get_answer_evaluator

# Get instances
supabase_qna_client = get_supabase_qna_client()
answer_evaluator = get_answer_evaluator()


async def test_supabase_client():
    """Test the Supabase client functionality"""
    print("Testing Supabase client...")
    
    # Check if client is initialized
    if not supabase_qna_client.client:
        print("   Supabase client not initialized (expected with dummy credentials)")
        print("Supabase client test completed.\n")
        return
    
    # Test with an invalid subject
    print("1. Testing with invalid subject...")
    invalid_questions = await supabase_qna_client.fetch_random_questions("test_user", "Mathematics")
    print(f"   Invalid subject result: {invalid_questions}")
    
    # Test with a valid subject
    print("2. Testing with valid subject...")
    valid_questions = await supabase_qna_client.fetch_random_questions("test_user", "Science")
    print(f"   Valid subject result: {valid_questions}")
    
    print("Supabase client test completed.\n")


def test_answer_evaluator():
    """Test the answer evaluator functionality"""
    print("Testing answer evaluator...")
    
    # Test with identical answers
    print("1. Testing with identical answers...")
    score1 = answer_evaluator.evaluate_answer("The sky is blue", "The sky is blue")
    print(f"   Identical answers score: {score1}")
    
    # Test with similar answers
    print("2. Testing with similar answers...")
    score2 = answer_evaluator.evaluate_answer("The sky is blue", "The sky is blue and beautiful")
    print(f"   Similar answers score: {score2}")
    
    # Test with different answers
    print("3. Testing with different answers...")
    score3 = answer_evaluator.evaluate_answer("The sky is blue", "I like ice cream")
    print(f"   Different answers score: {score3}")
    
    # Test with empty student answer
    print("4. Testing with empty student answer...")
    score4 = answer_evaluator.evaluate_answer("The sky is blue", "")
    print(f"   Empty student answer score: {score4}")
    
    print("Answer evaluator test completed.\n")


async def main():
    """Main test function"""
    print("Running Supabase integration and answer evaluation tests...\n")
    
    # Test Supabase client
    await test_supabase_client()
    
    # Test answer evaluator
    test_answer_evaluator()
    
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())