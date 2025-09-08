"""
QA evaluation module for the voice tutor application
"""
from src.database.supabase_client import initialise_pedant


def initialise_answer_evaluator():
    """Initialize and return the answer evaluator"""
    return initialise_pedant()


# For backward compatibility
initialise_pedant = initialise_answer_evaluator