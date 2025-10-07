"""
Test file for question tools
"""

import unittest
from src.cache.manager import cache_manager


class TestQuestionTools(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear cache before each test
        cache_manager.clear()
        # Set up mock user names in cache
        cache_manager.set_user_names({"alice", "bob", "charlie"})
    
    def test_imports_work(self):
        """Basic test to ensure imports work correctly"""
        # This is a simple test to ensure the module can be imported without errors
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()