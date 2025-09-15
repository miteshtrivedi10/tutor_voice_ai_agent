"""
Supabase client module for the MCP Server
Handles Supabase database connections and queries
"""

from typing import List, Optional
from supabase import create_client, Client
from src.config.settings import Config
from src.models.question import Question
from src.config.logging import logger


class SupabaseClient:
    """Manages Supabase database connections and queries"""

    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self._initialized = False
        self._initialize_client()
        logger.info("Supabase client created")

    def _initialize_client(self) -> None:
        """Lazy initialization of the Supabase client"""
        if not self._initialized:
            try:
                self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                self._initialized = True
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise

    def load_questions(
        self, user_name: str, subject: str, question_limit: int
    ) -> List[Question]:
        """
        Load questions for a specific user and subject

        Args:
            user_name: The user name
            subject: The subject
            question_limit: Maximum number of questions to load

        Returns:
            List of Question objects with their answers
        """
        try:
            response = (
                self.client.table("question_and_answers")
                .select("question_id, question, answer, user_name, subject")
                .eq("user_name", user_name)
                .eq("subject", subject)
                .limit(question_limit)
                .execute()
            )

            questions = [Question.from_dict(record) for record in response.data]
            logger.info(
                f"Loaded {len(questions)} questions for user {user_name}, subject {subject}"
            )
            return questions

        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            raise


# Global Supabase client instance
supabase_client = SupabaseClient()
