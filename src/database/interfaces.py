"""
Database interfaces for the voice tutor application
"""
from abc import ABC, abstractmethod
from typing import List
from src.models.agent_dtos import QuizPackFromDb, UsageMetrics


class QuizRepository(ABC):
    """Interface for quiz-related database operations"""
    
    @abstractmethod
    def fetch_random_questions(self, user_id: str, subject: str, limit: int = 10) -> QuizPackFromDb:
        """
        Fetch random questions and answers for a user and subject
        
        Args:
            user_id (str): The participant/user ID
            subject (str): The subject (Science, English, Social Studies)
            limit (int): Maximum number of questions to fetch (default: 10)
            
        Returns:
            QuizPackFromDb: Object containing list of questions and a message
        """
        pass


class UsageMetricsRepository(ABC):
    """Interface for usage metrics database operations"""
    
    @abstractmethod
    def update_usage_metrics_in_db(self, metrics: UsageMetrics) -> bool:
        """
        Update or create usage metrics in the database based on session_id.
        
        Args:
            metrics (UsageMetrics): The usage metrics to store
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        pass


class DatabaseRepository(QuizRepository, UsageMetricsRepository):
    """Combined interface for all database operations"""
    pass