"""
Tools module for the MCP Server
Contains the MCP tools for the voice tutoring agent
"""
import logging
from typing import Dict, Any, List, Set
from fastmcp import FastMCP
from datetime import timedelta
from src.cache.manager import cache_manager
from src.config.settings import Config
from src.supabase.client import supabase_client
from src.models.question import Question
from src.utils.check_answer import get_semantic_similarity
from src.utils.user_validation import validate_user_name
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


def _handle_user_validation_and_errors(user_name: str) -> Dict[str, Any]:
    """
    Helper function to validate user name and handle common errors.
    
    Args:
        user_name (str): The user name to validate
        
    Returns:
        Dict[str, Any]: A dictionary containing the validation result with status and message
    """
    # Validate user name
    validation_result = validate_user_name(user_name)
    logger.info(f"User name validation result: {validation_result}")
    return validation_result

@mcp.tool()
def get_valid_subjects_to_choose_from() -> List[str]:
    """
    Retrieves a list of valid subjects available
    Returns:
        List[str]: A list of valid subjects. If an error occurs, returns an empty list.
    Raises:
        Exception: If there is an error loading the subjects.
    """
    try:
        logger.info("Loading valid subjects")
        return ["Science", "Geography", "Social Studies"]
    except Exception as e:
        logger.error(f"Error loading subjects: {str(e)}")
        return []


@mcp.tool()
@cache_result(ttl_seconds=Config.CACHE_TTL)  # 15 minutes cache
def start_quiz(user_name: str, subject: str, question_limit: int = 5) -> Dict[str, Any]:
    """
    Starts the quiz by loading a list of questions for a specified user and subject, with an optional limit on the number of questions.

    Args:
        user_name (str): Student's user ID.
        subject (str): The subject for which questions are requested.
        question_limit (int): The maximum number of questions to load.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and total number of questions loaded.
                        If an error occurs, returns an error status and message.
    Raises:
        Exception: If there is an error loading the questions.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_name)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate subject
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
                "total_questions": 0,
            }
            
        # Validate question_limit
        if not isinstance(question_limit, int) or question_limit <= 0:
            return {
                "status": "error",
                "message": "Invalid question limit provided. Please provide a positive integer.",
                "total_questions": 0,
            }

        # Create cache key
        cache_key = f"questions_{user_name}_{subject}"
        cache_key_question_index = f"question_index_{user_name}_{subject}"

        logger.info(
            f"Loading questions for user: {user_name}, subject: {subject}, cache_key: {cache_key}"
        )

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key)
        
        # Handle the case where cached_questions is a tuple with the list as the first element
        if isinstance(cached_questions, tuple):
            logger.info(f"Type of cached_questions in start_quiz: {type(cached_questions)}, Value: {cached_questions}")
            # Extract the list from the tuple
            questions_list = cached_questions[0] if len(cached_questions) > 0 else []
        else:
            questions_list = cached_questions
            
        if questions_list and isinstance(questions_list, list) and len(questions_list) > 0:
            # Convert Question objects to dictionaries for JSON serialization if needed
            return {
                "status": "success",
                "message": f"Loaded {len(questions_list)} questions",
                "total_questions": len(questions_list),
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
        # Set initial question index to -1
        cache_manager.set(cache_key_question_index, -1)

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
def evaluate_student_answer(
    user_name: str, subject: str, question: str, student_answer: str
) -> Dict[str, Any]:
    """
    Evaluates a student's answer to a specific question within a given subject for a particular user.
    The function checks if the question is available in the cache and compares the student's answer
    with the correct answer using semantic similarity. The semantic similarity score is returned as part
    of the result.

    Args:
        user_name (str): Student's user ID.
        subject (str): The subject of the question.
        question (str): The question that the student is answering.
        student_answer (str): The answer provided by the student.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and result of the evaluation.
        The result includes the semantic similarity score between the student's answer and the correct answer.
        If an error occurs, returns an error status and message.

    Raises:
        Exception: If there is an error in evaluating the student's answer or if the question is not found.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_name)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate inputs
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
            }
            
        if not question or not isinstance(question, str):
            return {
                "status": "error",
                "message": "Invalid question provided. Please provide a valid question.",
            }
            
        if not student_answer or not isinstance(student_answer, str):
            return {
                "status": "error",
                "message": "Invalid student answer provided. Please provide a valid answer.",
            }

        # Create cache key
        cache_key = f"questions_{user_name}_{subject}"

        logger.info(
            f"Evaluating answer for user: {user_name}, subject: {subject}, cache_key: {cache_key}"
        )

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key)
        
        # Handle the case where cached_questions is a tuple with the list as the first element
        if isinstance(cached_questions, tuple):
            logger.info(f"Type of cached_questions in evaluate_student_answer: {type(cached_questions)}, Value: {cached_questions}")
            # Extract the list from the tuple
            questions_list = cached_questions[0] if len(cached_questions) > 0 else []
        else:
            questions_list = cached_questions
            
        if not questions_list or not isinstance(questions_list, list) or len(questions_list) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        for q in questions_list:
            if isinstance(q, Question) and q.question == question:
                # Calculate semantic similarity between the student's answer and the correct answer
                similarity_score = get_semantic_similarity(q.answer, student_answer)
                return {
                    "status": "success",
                    "message": "Answer evaluated successfully",
                    "result": similarity_score,
                }

        return {
            "status": "error",
            "message": "The specified question was not found in the cached questions",
        }

    except Exception as e:
        logger.error(f"Error in evaluating the student's answer: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to evaluate the student's answer: {str(e)}",
        }


@mcp.tool()
def get_quiz_question(user_id: str, subject: str) -> Dict[str, Any]:
    """
    Retrieves the question for a specified user and subject.

    Args:
        user_id (str): Student's user ID.
        subject (str): The subject of the question.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the next question and answer.
                        If an error occurs, returns an error status and message.

    Raises:
        Exception: If there is an error loading the next question.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_id)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate subject
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
            }

        # Create cache key
        cache_key_questions = f"questions_{user_id}_{subject}"
        cache_key_question_index = f"question_index_{user_id}_{subject}"

        logger.info(
            f"Loading next question for user: {user_id}, subject: {subject}, cache_key_question_index: {cache_key_question_index}"
        )

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)
        
        # Handle the case where cached_questions is a tuple with the list as the first element
        if isinstance(cached_questions, tuple):
            # Extract the list from the tuple
            questions_list = cached_questions[0] if len(cached_questions) > 0 else []
        else:
            questions_list = cached_questions

        if not questions_list or not isinstance(questions_list, list) or len(questions_list) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Get current index
        current_index = cached_index if isinstance(cached_index, int) else -1
        logger.info(f"Current question index: {current_index}")
        
        # Check if we've reached the end
        if current_index >= len(questions_list) - 1:
            return {
                "status": "error",
                "message": f"There are no more questions available for subject: {subject}",
            }

        # Increment question index
        current_index += 1

        # Get the question at the new index
        next_question = questions_list[current_index]
        
        # Ensure it's a Question object
        if not isinstance(next_question, Question):
            return {
                "status": "error",
                "message": "Invalid question data in cache",
            }

        logger.info(f"Next question: {next_question.question} with Index : {current_index}")

        # Store in cache
        cache_manager.set(cache_key_question_index, current_index)

        return {
            "status": "success",
            "message": "Next question and answer is available",
            "question": next_question.question,
            "answer": next_question.answer,
        }
    except Exception as e:
        logger.error(f"Error loading next question: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load question: {str(e)}",
        }


@mcp.tool()
def is_quiz_completed(user_id: str, subject: str) -> Dict[str, Any]:
    """
    Checks if the quiz is completed for a specified user and subject.

    Args:
        user_id (str): Student's user ID.
        subject (str): The subject of the quiz.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and whether the quiz is completed.
                        If an error occurs, returns an error status and message.

    Raises:
        Exception: If there is an error checking quiz completion.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_id)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate subject
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
            }

        # Create cache key
        cache_key_questions = f"questions_{user_id}_{subject}"
        cache_key_question_index = f"question_index_{user_id}_{subject}"

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)

        logger.info(
            f"Checking quiz completion for user: {user_id}, subject: {subject}, cache_key_question_index: {cached_index}"
        )

        # Handle the case where cached_questions is a tuple with the list as the first element
        if isinstance(cached_questions, tuple):
            # Extract the list from the tuple
            questions_list = cached_questions[0] if len(cached_questions) > 0 else []
        else:
            questions_list = cached_questions

        if not questions_list or not isinstance(questions_list, list) or len(questions_list) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Get current index
        current_index = cached_index if isinstance(cached_index, int) else -1

        # Check if quiz is completed (no more questions)
        if current_index >= len(questions_list) - 1:
            return {
                "status": "success",
                "message": f"Quiz completed for subject: {subject}",
                "is_quiz_completed": True,
            }

        return {
            "status": "success",
            "message": f"There are pending questions for subject: {subject}",
            "is_quiz_completed": False,
        }
    except Exception as e:
        logger.error(f"Failed to check quiz completion: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to check if quiz is completed: {str(e)}",
        }


# @mcp.tool()
def get_previous_question(user_id: str, subject: str) -> Dict[str, Any]:
    """
    Retrieves the previous question for a specified user and subject.

    Args:
        user_id (str): Student's user ID.
        subject (str): The subject of the question.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the previous question and answer.
                        If an error occurs, returns an error status and message.

    Raises:
        Exception: If there is an error loading the previous question.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_id)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate subject
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
            }

        # Create cache key
        cache_key_questions = f"questions_{user_id}_{subject}"
        cache_key_question_index = f"question_index_{user_id}_{subject}"

        logger.info(
            f"Loading previous question for user: {user_id}, subject: {subject}, cache_key_question_index: {cache_key_question_index}"
        )

        # Check if already in cache
        cached_questions = cache_manager.get(cache_key_questions)
        cached_index = cache_manager.get(cache_key_question_index)
        
        # Handle the case where cached_questions is a tuple with the list as the first element
        if isinstance(cached_questions, tuple):
            logger.info(f"Type of cached_questions in get_previous_question: {type(cached_questions)}, Value: {cached_questions}")
            # Extract the list from the tuple
            questions_list = cached_questions[0] if len(cached_questions) > 0 else []
        else:
            questions_list = cached_questions

        if not questions_list or not isinstance(questions_list, list) or len(questions_list) == 0:
            return {
                "status": "error",
                "message": f"There are no questions available for subject: {subject}",
            }

        # Get current index
        current_index = cached_index if isinstance(cached_index, int) else 0

        # Check if we're at the first question (no previous)
        if current_index <= 0:
            return {
                "status": "error",
                "message": "There are no previous questions available",
            }

        # Decrement question index
        current_index -= 1

        # Get the question at the new index
        previous_question = questions_list[current_index]
        
        # Ensure it's a Question object
        if not isinstance(previous_question, Question):
            return {
                "status": "error",
                "message": "Invalid question data in cache",
            }

        logger.info(f"Previous question: {previous_question.question}")

        # Store in cache
        cache_manager.set(cache_key_question_index, current_index)

        return {
            "status": "success",
            "message": "Previous question and answer is available",
            "question": previous_question.question,
            "answer": previous_question.answer,
        }
    except Exception as e:
        logger.error(f"Error loading previous question: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to load question: {str(e)}",
        }


# @mcp.tool()
# @cache_result(ttl_seconds=Config.CACHE_TTL)  # 15 minutes cache
def update_question_index(
    user_id: str, subject: str, question_index: int
) -> Dict[str, Any]:
    """
    Maintains and updates the question index for a specified user and subject.

    Args:
        user_id (str): Student's user ID.
        subject (str): The subject of the question.
        question_index (int): The new question index to be set.

    Returns:
        Dict[str, Any]: A dictionary containing the status, message, and the updated question index.
                        If an error occurs, returns an error status and message.

    Raises:
        Exception: If there is an error updating the question index.
    """
    # Validate user name
    validation_result = _handle_user_validation_and_errors(user_id)
    if validation_result["status"] != "success":
        return validation_result
    
    try:
        # Validate subject
        if not subject or not isinstance(subject, str):
            return {
                "status": "error",
                "message": "Invalid subject provided. Please provide a valid subject.",
                "index": -1,
            }
            
        # Validate question_index
        if not isinstance(question_index, int) or question_index < 0:
            return {
                "status": "error",
                "message": "Invalid question index provided. Please provide a non-negative integer.",
                "index": -1,
            }

        # Create cache key for index
        index_key = f"question_index_{user_id}_{subject}"

        logger.info(
            f"Updating question index for user: {user_id}, subject: {subject}, cache_key: {index_key}, new_index: {question_index}"
        )

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
