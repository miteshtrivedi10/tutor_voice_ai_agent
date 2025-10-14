"""
Supabase client module for the MCP Server
Handles Supabase database connections and queries
"""

from typing import List, Set, Optional
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

    def load_all_unique_user_names(self) -> Set[str]:
        """
        Load all unique user names from the database

        Returns:
            Set of unique user names
        """
        try:
            # Ensure client is initialized
            self._initialize_client()
            
            response = (
                self.client.table("question_and_answers")
                .select("user_name")
                .execute()
            )

            # Handle case where response.data might be None or empty
            if not response.data:
                logger.info("No user names found in database")
                return set()

            # Extract user names and remove duplicates using set
            user_names = set()
            for record in response.data:
                user_name = record.get("user_name")
                if user_name:
                    user_names.add(user_name)
                    
            logger.info(f"Loaded {len(user_names)} unique user names")
            return user_names

        except Exception as e:
            logger.error(f"Error loading user names: {str(e)}")
            # Return empty set instead of raising exception to prevent server startup failure
            return set()

    def load_unique_subjects_for_user(self, user_name: str) -> Set[str]:
        """
        Load all the unique subjects for given user_name

        Args:
            user_name: user name of the student
        Returns:
            List of subjects which are unique
        """
        try:
            # Ensure client is initialized
            self._initialize_client()

            response = (
                self.client.table("question_and_answers")
                .select("subject")
                .eq("user_name", user_name)
                .execute()
            )

            # Handle case where response.data might be None or empty
            if not response.data:
                logger.info(f"No subjects for user : {user_name} found in database")
                return set()

            # Extract subjects and remove duplicates using set
            subjects = set()
            for record in response.data:
                sub = record.get("subject")
                if sub:
                    subjects.add(sub)

            logger.info(f"Loaded {len(subjects)} unique subjects")
            return subjects

        except Exception as e:
            logger.error(f"Error loading subjects: {str(e)}")
            # Return empty set instead of raising exception to prevent server startup failure
            return set()

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
