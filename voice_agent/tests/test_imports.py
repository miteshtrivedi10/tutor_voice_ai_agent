"""
Test that all modules can be imported correctly
"""

def test_imports():
    # Test config imports
    from src.config import settings, logging_config
    from src.config.settings import SUPABASE_URL, SUPABASE_KEY
    from src.config.logging_config import logger, get_logger
    
    # Test database imports
    from src.database import supabase_client
    from src.database.supabase_client import SupabaseQnAClient, get_db_client
    
    # Test models imports
    from src.models import agent_dtos
    from src.models.agent_dtos import (
        QnAFromDb,
        ChatTranscript,
        QuizPackFromDb,
        QuizPackAssessment,
        UsageMetrics,
    )
    
    # Test utils imports
    from src.utils import open_telemtry
    from src.utils.open_telemtry import configure_opentelemetry
    
    # Test main modules
    from src import tutor_agent, run_quiz_agent, main
    
    # If we get here without exceptions, all imports work
    assert True