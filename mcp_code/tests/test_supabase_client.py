"""
Test file for Supabase client
"""

import unittest
from unittest.mock import patch, MagicMock
from src.supabase.client import SupabaseClient


class TestSupabaseClient(unittest.TestCase):
    
    @patch('src.supabase.client.create_client')
    def test_load_all_unique_user_names_success(self, mock_create_client):
        """Test successful loading of unique user names"""
        # Mock the Supabase client and response
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [
            {"user_name": "alice"},
            {"user_name": "bob"},
            {"user_name": "charlie"}
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        
        # Create client instance
        client = SupabaseClient()
        
        # Test the method
        result = client.load_all_unique_user_names()
        self.assertEqual(len(result), 3)
        self.assertIn("alice", result)
        self.assertIn("bob", result)
        self.assertIn("charlie", result)
    
    @patch('src.supabase.client.create_client')
    def test_load_all_unique_user_names_empty_data(self, mock_create_client):
        """Test loading user names when no data is returned"""
        # Mock the Supabase client and response
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = None
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        
        # Create client instance
        client = SupabaseClient()
        
        # Test the method
        result = client.load_all_unique_user_names()
        self.assertEqual(result, set())
    
    @patch('src.supabase.client.create_client')
    def test_load_all_unique_user_names_exception(self, mock_create_client):
        """Test loading user names when an exception occurs"""
        # Mock the Supabase client to raise an exception
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        mock_client.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
        
        # Create client instance
        client = SupabaseClient()
        
        # Test the method - should return empty set instead of raising exception
        result = client.load_all_unique_user_names()
        self.assertEqual(result, set())


if __name__ == '__main__':
    unittest.main()