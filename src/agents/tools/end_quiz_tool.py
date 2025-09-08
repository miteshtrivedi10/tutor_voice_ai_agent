"""
EndQuizTool: Tool for completing and finalizing a quiz session
Follows Single Responsibility Principle - handles only quiz completion
"""

import logging
import pandas as pd
from typing import Any, Dict
from abc import ABC, abstractmethod

from src.services.session_manager import get_session_manager
from src.agents.interfaces import ITool

logger = logging.getLogger(__name__)


class EndQuizTool(ITool):
    """
    Tool implementation for ending a quiz session.
    Updates session state to mark quiz as completed and provides feedback.
    
    Attributes:
        session_manager: The session manager instance for state updates
    """

    def __init__(self, session_manager=None):
        """
        Initialize the EndQuizTool.
        
        Args:
            session_manager: Instance of SessionManager for session operations (optional, uses singleton if None)
        """
        self.name = "end_quiz"
        self.description = (
            "Use this tool to complete the current quiz session. "
            "This will finalize the quiz, save results, and provide completion feedback. "
            "Call this when all questions have been answered or the user wants to end early. "
            "Parameters: session_id (string) - The current session identifier"
        )
        self.session_manager = session_manager or get_session_manager()

    def execute(self, session_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the end quiz functionality.
        
        Args:
            session_id: The session ID to end the quiz for
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Dictionary containing the result message and status
            
        Raises:
            ValueError: If session_id is invalid or session not found
        """
        try:
            # Update session to mark quiz as ended
            session = self.session_manager.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Mark quiz as completed
            session['quiz_status'] = 'completed'
            session['quiz_ended_at'] = str(pd.Timestamp.now())
            self.session_manager.update_session(session_id, session)

            # Save final assessment if not already done
            if 'quiz_score' in session:
                self.session_manager.save_assessment(session_id, {
                    'type': 'quiz_completion',
                    'score': session.get('quiz_score', 0),
                    'total_questions': session.get('quiz_total_questions', 0),
                    'subject': session.get('current_subject', 'General')
                })

            logger.info(f"Quiz ended for session {session_id}")

            # Child-friendly completion message
            completion_message = (
                "🎉 Great job completing the quiz! You did wonderfully today. "
                "Your hard work and learning are something to be proud of! "
                "Let's take a moment to celebrate your achievements. "
                "Would you like to review what you learned or start a new adventure?"
            )

            return {
                "status": "success",
                "message": completion_message,
                "quiz_completed": True,
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"Error ending quiz for session {session_id}: {str(e)}")
            # Child-friendly error recovery
            recovery_message = (
                "Oops! Something went wrong while finishing the quiz. "
                "Don't worry, you're still a superstar learner! "
                "Let's try again or pick another fun activity. "
                "You can always come back to quizzes anytime!"
            )
            return {
                "status": "error",
                "message": recovery_message,
                "quiz_completed": False,
                "session_id": session_id,
                "error": str(e)
            }

    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for tool calling.
        
        Returns:
            Dictionary representing the tool schema for LLM integration
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The current session identifier"
                        }
                    },
                    "required": ["session_id"]
                }
            }
        }