"""
Tools module for the MCP Server
Contains the MCP tools for the voice tutoring agent
"""

from typing import Dict, Any, List
from fastmcp import FastMCP
from datetime import timedelta
from src.cache.manager import cache_manager
from src.config.settings import Config
from src.supabase.client import supabase_client
from src.models.question import Question
from src.utils.check_answer import get_semantic_similarity
from src.config.logging import logger

# Initialize FastMCP server
mcp = FastMCP("Tutor Agent MCP Toolkit")


def cache_result(ttl_seconds: int = Config.CACHE_TTL):
    """
    Decorator to cache function results with a specific TTL.

    Args:
        ttl_seconds: TTL in seconds, defaults to Config.CACHE_TTL
    """

    def decorator(func):
        # Don't wrap the function - just return it as-is to avoid FastMCP issues
        return func

    return decorator


@mcp.tool()
@cache_result(ttl_seconds=Config.CACHE_TTL)  # 15 minutes cache
def load_questions(
    user_name: str, subject: str, question_limit: int = 5
) -> Dict[str, Any]:
    """
    Loads a list of questions for a specified user and subject, with an optional limit on the number of questions.

    Args:
        user_name (str): The name of the user for whom questions are to be loaded.
        subject (str): The subject for which questions are requested.
        question_limit (int): The maximum number of questions to load.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and total number of questions loaded.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "Loaded 5 questions",
        "total_questions": 5
    }

    Raises:
        Exception: If there is an error loading the questions.
    """
    try:
        # Create cache key
        cache_key = f"questions_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key)
        if cached_questions:
            # Convert Question objects to dictionaries for JSON serialization
            return {
                "status": "success",
                "message": f"Loaded {len(cached_questions)} questions",
                "total_questions": len(cached_questions),
            }

        # Get Supabase client and query for questions
        questions: List[Question] = supabase_client.load_questions(
            user_name, subject, question_limit
        )

        if not questions:
            return {
                "status": "success",
                "message": "No questions available for the specified user and subject",
                "total_questions": 0,
            }

        # Store in cache
        ttl_timedelta = timedelta(seconds=Config.CACHE_TTL)
        cache_manager.set(cache_key, questions, ttl=ttl_timedelta)

        return {
            "status": "success",
            "message": f"Loaded {len(questions)} questions",
            "total_questions": len(questions),
        }

    except Exception as e:
        logger.error(f"Error loading questions: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load questions: {str(e)}",
            "total_questions": 0,
        }


@mcp.tool()
async def evaluate_student_answer(
    user_name: str, subject: str, question: str, student_answer: str
) -> Dict[str, Any]:
    """
    Evaluates a student's answer to a specific question within a given subject for a particular user.
    The function checks if the question is available in the cache and compares the student's answer
    with the correct answer using semantic similarity. The semantic similarity score is returned as part
    of the result.

    Args:
        user_name (str): The name of the user for whom the question is being evaluated.
        subject (str): The subject of the question.
        question (str): The question that the student is answering.
        student_answer (str): The answer provided by the student.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and result of the evaluation.
        The result includes the semantic similarity score between the student's answer and the correct answer.
        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "Correct answer",
        "result": 0.95  # Semantic similarity score
    }

    Raises:
        Exception: If there is an error in evaluating the student's answer or if the question is not found.
    """
    try:
        # Create cache key
        cache_key = f"questions_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key)
        if not cached_questions or len(cached_questions) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        for q in cached_questions:
            if q.question == question:
                # Calculate semantic similarity between the student's answer and the correct answer
                similarity_score = get_semantic_similarity(q.answer, student_answer)
                return {
                    "status": "success",
                    "message": "Correct answer",
                    "result": similarity_score,
                }

        return {
            "status": "error",
            "message": "Looks like the question is not available",
        }

    except Exception as e:
        logger.error(f"Error in evaluating the student's answer: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to evaluate the student's answer: {str(e)}",
        }


@mcp.tool()
async def get_first_question(user_name: str, subject: str) -> Dict[str, Any]:
    """
    Retrieves the first question for a specified user and subject.

    Args:
        user_name (str): The name of the user for whom the question is to be retrieved.
        subject (str): The subject of the question.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the first question and answer.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "First question and answer is available with current question index : 1",
        "question": "What is the capital of France?",
        "answer": "Paris"
    }

    Raises:
        Exception: If there is an error loading the first question.
    """
    try:
        # Create cache key
        cache_key_questions = f"questions_{user_name}_{subject}"
        cache_key_question_index = f"question_index_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        if not cached_questions or len(cached_questions) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Set question index to 1
        cache_manager.set(cache_key_question_index, 1)
        single_q: Question = cached_questions[0]

        logger.info(f"First question: {single_q.question}")

        return {
            "status": "success",
            "message": "First question and answer is available with current question index : 1",
            "question": single_q.question,
            "answer": single_q.answer,
        }
    except Exception as e:
        logger.error(f"Error loading first question: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load first question: {str(e)}",
        }


@mcp.tool()
async def get_next_question(user_name: str, subject: str) -> Dict[str, Any]:
    """
    Retrieves the next question for a specified user and subject.

    Args:
        user_name (str): The name of the user for whom the question is to be retrieved.
        subject (str): The subject of the question.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the next question and answer.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "Next question and answer is available",
        "question": "What is the capital of Germany?",
        "answer": "Berlin"
    }

    Raises:
        Exception: If there is an error loading the next question.
    """
    try:
        # Create cache key
        cache_key_questions = f"questions_{user_name}_{subject}"
        cache_key_question_index = f"question_index_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)

        if not cached_index or not cached_questions or len(cached_questions) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Set question index to 1
        cached_index = cache_manager.get(cache_key_question_index)
        current_index = (
            cached_index[0] if isinstance(cached_index, tuple) else cached_index
        )
        if current_index is None:
            current_index = -1

        if current_index >= len(cached_questions):
            return {
                "status": "error",
                "message": f"There are no more questions available for subject: {subject}",
            }

        # Increment question index
        current_index += 1

        single_q: Question = cached_questions[current_index]

        logger.info(f"Next question: {single_q.question}")

        # Store in cache
        cache_manager.set(cache_key_question_index, current_index)

        return {
            "status": "success",
            "message": "Next question and answer is available",
            "question": single_q.question,
            "answer": single_q.answer,
        }
    except Exception as e:
        logger.error(f"Error loading next question: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load question: {str(e)}",
        }


@mcp.tool()
async def is_quiz_completed(user_name: str, subject: str) -> Dict[str, Any]:
    """
    Checks if the quiz is completed for a specified user and subject.

    Args:
        user_name (str): The name of the user for whom the quiz completion is to be checked.
        subject (str): The subject of the quiz.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and whether the quiz is completed.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "There are no pending questions available for subject: Mathematics",
        "is_quiz_completed": True
    }

    Raises:
        Exception: If there is an error checking quiz completion.
    """
    try:
        # Create cache key
        cache_key_questions = f"questions_{user_name}_{subject}"
        cache_key_question_index = f"question_index_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)

        if not cached_index or not cached_questions or len(cached_questions) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Set question index to 1
        cached_index = cache_manager.get(cache_key_question_index)
        current_index = (
            cached_index[0] if isinstance(cached_index, tuple) else cached_index
        )
        if current_index is None:
            current_index = -1

        if current_index >= len(cached_questions) or current_index == -1:
            return {
                "status": "success",
                "message": f"There are no questions available for subject: {subject}",
                "is_quiz_completed": True,
            }

        return {
            "status": "success",
            "message": f"There are pending questions available for subject: {subject}",
            "is_quiz_completed": False,
        }
    except Exception as e:
        logger.error(f"Failed to check quiz completion: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to check if quiz is completed: {str(e)}",
        }


@mcp.tool()
async def get_previous_question(user_name: str, subject: str) -> Dict[str, Any]:
    """
    Retrieves the previous question for a specified user and subject.

    Args:
        user_name (str): The name of the user for whom the question is to be retrieved.
        subject (str): The subject of the question.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the previous question and answer.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "Previous question and answer is available",
        "question": "What is the capital of France?",
        "answer": "Paris"
    }

    Raises:
        Exception: If there is an error loading the previous question.
    """
    try:
        # Create cache key
        cache_key_questions = f"questions_{user_name}_{subject}"
        cache_key_question_index = f"question_index_{user_name}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)

        if not cached_index or not cached_questions or len(cached_questions) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Set question index to 1
        cached_index = cache_manager.get(cache_key_question_index)
        current_index = (
            cached_index[0] if isinstance(cached_index, tuple) else cached_index
        )
        if current_index is None:
            current_index = 0

        if current_index <= 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Decrement question index
        current_index -= 1

        single_q: Question = cached_questions[current_index]

        logger.info(f"Previous question: {single_q.question}")

        # Store in cache
        cache_manager.set(cache_key_question_index, current_index)

        return {
            "status": "success",
            "message": "Previous question and answer is available",
            "question": single_q.question,
            "answer": single_q.answer,
        }
    except Exception as e:
        logger.error(f"Error loading previous question: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load question: {str(e)}",
        }


@mcp.tool()
@cache_result(ttl_seconds=Config.CACHE_TTL)  # 15 minutes cache
def update_question_index(
    user_name: str, subject: str, question_index: int
) -> Dict[str, Any]:
    """
    Maintains and updates the question index for a specified user and subject.

    Args:
        user_name (str): The name of the user for whom the question index is to be updated.
        subject (str): The subject of the question.
        question_index (int): The new question index to be set.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the updated question index.
                        If an error occurs, returns an error status and message.

    Example:
    {
        "status": "success",
        "message": "question index updated",
        "index": 3
    }

    Raises:
        Exception: If there is an error updating the question index.
    """
    try:
        # Create cache key for index
        index_key = f"question_index_{user_name}_{subject}"

        # Store in cache
        ttl_timedelta = timedelta(seconds=Config.CACHE_TTL)
        cache_manager.set(index_key, question_index, ttl=ttl_timedelta)

        return {
            "status": "success",
            "message": "question index updated",
            "index": question_index,
        }

    except Exception as e:
        logger.error(f"Error updating question index: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update question index: {str(e)}",
            "index": -1,
        }
