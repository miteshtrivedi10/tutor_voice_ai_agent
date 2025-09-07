"""
Supabase client module for fetching Q&A data
"""

from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from config.logging_config import logger
from model.agent_dtos import QuizPackFromDb, QnAFromDb
from qa_metrics.pedant import PEDANT


class SupabaseQnAClient:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseQnAClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Supabase client"""
        # Prevent re-initialization
        if self._initialized:
            return

        self.client: Client
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")

        self._initialized = True

    def update_usage_metrics_in_db(self):
        pass

    def fetch_random_questions(
        self, user_id: str, subject: str, limit: int = 10
    ) -> QuizPackFromDb:
        """
        Fetch random questions and answers for a user and subject

        Args:
            user_id (str): The participant/user ID
            subject (str): The subject (Science, English, Social Studies)
            limit (int): Maximum number of questions to fetch (default: 10)

        Returns:
            QuizPackFromDb: Object containing list of questions and a message
        """
        # If client is not initialized, return empty quiz pack with error message
        if not self.client:
            logger.warning("Supabase client not initialized")
            return QuizPackFromDb(
                quiz_pack=[], message="Failed to initialize database connection"
            )

        try:
            # Validate subject
            valid_subjects = ["Science", "English", "Social Studies"]
            if subject not in valid_subjects:
                logger.warning(f"Invalid subject requested: {subject}")
                return QuizPackFromDb(
                    quiz_pack=[],
                    message=f"Invalid subject: {subject}. Valid subjects are: Science, English, Social Studies",
                )

            # Query the question_and_answers table
            # Using "question_id" as the ID field name instead of "id"
            response = (
                self.client.table("question_and_answers")
                .select("question_id, question, answer")
                .eq("user_name", user_id)
                .eq("subject", subject)
                .limit(limit)
                .execute()
            )

            # Extract the data
            questions_data = response.data if response.data else []

            # Convert to QnAFromDb objects
            quiz_pack = []
            for item in questions_data:
                # Create QnAFromDb object with proper field mapping
                qna = QnAFromDb(
                    question_id=str(item.get("question_id", "")),
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                )
                quiz_pack.append(qna)

            logger.info(
                f"Fetched {len(quiz_pack)} questions for user {user_id} in {subject}"
            )

            # Return success message if questions found, otherwise appropriate message
            if len(quiz_pack) == 0:
                return QuizPackFromDb(
                    quiz_pack=[],
                    message=f"No questions found for user {user_id} in {subject}",
                )
            else:
                return QuizPackFromDb(
                    quiz_pack=quiz_pack,
                    message=f"Successfully fetched {len(quiz_pack)} questions",
                )

        except Exception as e:
            logger.error(f"Error fetching questions from Supabase: {e}")
            return QuizPackFromDb(
                quiz_pack=[], message=f"Error fetching questions: {str(e)}"
            )


# Global instance of the Supabase client
_supabase_qna_client = None
_pedant = None


def initialise_pedant() -> PEDANT:
    global _pedant
    if _pedant is None:
        _pedant = PEDANT()
        logger.info("PEDANT module loaded")
    return _pedant


def intialise_db_client() -> SupabaseQnAClient:
    global _supabase_qna_client
    if _supabase_qna_client is None:
        _supabase_qna_client = SupabaseQnAClient()
        logger.info("Supabase client module loaded")
    return _supabase_qna_client
