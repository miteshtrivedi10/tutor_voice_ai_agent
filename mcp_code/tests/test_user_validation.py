"""
Test file for user validation utilities
"""

import unittest
from src.cache.manager import cache_manager
from src.utils.user_validation import validate_user_name


class TestUserValidation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear cache before each test
        cache_manager.clear()
    
    def test_validate_user_name_success(self):
        """Test successful user name validation"""
        # Set up mock user names in cache
        cache_manager.set_user_names({"alice", "bob", "charlie"})
    
        # Test valid user name
        result = validate_user_name("alice")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "User Id is valid")
        
    def test_validate_user_name_not_found(self):
        """Test user name not found in valid list"""
        # Set up mock user names in cache
        cache_manager.set_user_names({"alice", "bob", "charlie"})
    
        # Test invalid user name
        result = validate_user_name("david")
        self.assertEqual(result["status"], "error")
        self.assertIn("User Id 'david' not found", result["message"])
        
    def test_validate_user_name_invalid_input(self):
        """Test validation with invalid input"""
        # Set up mock user names in cache
        cache_manager.set_user_names({"alice", "bob", "charlie"})
    
        # Test with None
        result = validate_user_name(None)
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid User Id provided", result["message"])
        
        # Test with empty string
        result = validate_user_name("")
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid User Id provided", result["message"])
        
    def test_validate_user_name_empty_cache(self):
        """Test validation with empty cache"""
        # Ensure cache is empty
        cache_manager.clear()
        
        # Test with valid user name (should fail because cache is empty)
        result = validate_user_name("alice")
        self.assertEqual(result["status"], "error")
        self.assertIn("User validation service is temporarily unavailable", result["message"])


if __name__ == '__main__':
    unittest.main()