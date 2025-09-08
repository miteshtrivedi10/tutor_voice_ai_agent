"""
Supabase client module for fetching Q&A data
"""
from supabase import create_client, Client
from src.config.settings import SUPABASE_URL, SUPABASE_KEY
from src.config.logging_config import logger
from src.models.agent_dtos import QuizPackFromDb, QnAFromDb, UsageMetrics
from src.database.interfaces import DatabaseRepository
from qa_metrics.pedant import PEDANT


class SupabaseQnAClient(DatabaseRepository):
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

    def update_usage_metrics_in_db(self, metrics: UsageMetrics) -> bool:
        """
        Update or create usage metrics in the database based on session_id.
        
        Args:
            metrics (UsageMetrics): The usage metrics to store
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        # If client is not initialized, return False
        if not self.client:
            logger.warning("Supabase client not initialized")
            return False

        try:
            # Convert metrics to dictionary, excluding default values
            metrics_dict = metrics.model_dump(exclude_defaults=True)

            # Ensure session_id is present
            if "session_id" not in metrics_dict or not metrics_dict["session_id"]:
                logger.error("Session ID is required to update usage metrics")
                return False

            # Get session_id and remove it from the dict for upsert
            session_id = metrics_dict.pop("session_id")

            # Handle default values for optional fields
            # For fields that might not be present, we'll set them to their default values
            # This ensures we don't miss any fields in the upsert operation
            default_values = {
                "user_name": "Not Set",
                "mt_stt_audioduration": 0.0,
                "mt_llm_duration": 0,
                "mt_llm_completiontokens": 0,
                "mt_llm_prompttokens": 0,
                "mt_llm_promptcachetokens": 0,
                "mt_llm_totaltokens": 0,
                "mt_llm_tokenspersecond": 0.0,
                "mt_llm_ttft": 0.0,
                "mt_tts_audioduration": 0.0,
                "mt_tts_characterscount": 0,
                "mt_tts_duration": 0,
                "mt_tts_ttfb": 0,
                "mt_eou_utterancedelay": 0,
                "mt_eou_transcriptiondelay": 0,
            }

            # Apply default values for any missing fields
            for key, default_value in default_values.items():
                if key not in metrics_dict:
                    metrics_dict[key] = default_value

            # Add session_id back to the dict for database operation
            metrics_dict["session_id"] = session_id

            # Perform upsert operation (insert or update)
            response = self.client.table("usage_metrics").upsert(metrics_dict).execute()

            # Check if the operation was successful
            if response.data:
                logger.info(
                    f"Successfully updated/created usage metrics for session: {session_id}"
                )
                return True
            else:
                logger.warning(
                    f"Failed to update/create usage metrics for session: {session_id}"
                )
                return False

        except Exception as e:
            logger.error(f"Error updating/creating usage metrics in Supabase: {e}")
            return False

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


def get_db_client() -> SupabaseQnAClient:
    global _supabase_qna_client
    if _supabase_qna_client is None:
        _supabase_qna_client = SupabaseQnAClient()
        logger.info("Supabase client module loaded")
    return _supabase_qna_client
