"""
Usage service for handling usage metrics in the voice tutor application
"""
from src.database.supabase_client import get_db_client
from src.models.agent_dtos import UsageMetrics
from src.config.logging_config import logger


class UsageService:
    """Service for handling usage metrics"""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    def update_usage_metrics_in_db(self, metrics: UsageMetrics) -> bool:
        """
        Update or create usage metrics in the database based on session_id.
        
        Args:
            metrics (UsageMetrics): The usage metrics to store
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        return self.db_client.update_usage_metrics_in_db(metrics)