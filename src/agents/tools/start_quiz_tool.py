"""
StartQuizTool - Single responsibility tool for starting a new quiz session
Follows SOLID principles with comprehensive error handling and child-friendly recovery
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from src.agents.interfaces import ITool, ToolExecutionContext
from src.models.agent_dtos import MainAgentData, QuizPackAssessment


logger = logging.getLogger(__name__)


class StartQuizTool(ITool):
    """Tool for starting a new quiz session with the student"""
    
    @property
    def name(self) -> str:
        return "start_quiz"
    
    @property
    def description(self) -> str:
        return (
            "Start a new quiz session for the student. Use this when the student is ready to begin "
            "learning or when they request to take a quiz. The tool will select an appropriate quiz "
            "pack based on the student's subject preference and create a new assessment session. "
            "This prepares the tutor for the quiz flow with question-by-question interaction."
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "quiz_type": {
                    "type": "string",
                    "enum": ["practice", "assessment", "review"],
                    "description": "Type of quiz: practice for learning, assessment for evaluation, review for reinforcement",
                    "default": "practice"
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Difficulty level of the quiz",
                    "default": "medium"
                },
                "question_count": {
                    "type": "integer",
                    "description": "Number of questions in the quiz (1-20)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                }
            },
            "required": []
        }
    
    async def execute(self, parameters: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        """
        Execute the tool to start a new quiz session
        
        Args:
            parameters: Dict containing quiz_type (optional), difficulty (optional), question_count (optional)
            context: Execution context with session data
            
        Returns:
            Dict with success status and quiz session information
        """
        try:
            session_data = context.session_data
            
            # Validate student information exists
            if not session_data.student_name or not session_data.subject:
                raise ValueError("Student name and subject must be set before starting a quiz")
            
            # Set default parameters
            quiz_type = parameters.get("quiz_type", "practice")
            difficulty = parameters.get("difficulty", "medium")
            question_count = parameters.get("question_count", 5)
            
            # Validate question count
            if not 1 <= question_count <= 20:
                question_count = 5
                logger.warning(f"Invalid question count {question_count}, using default 5")
            
            # Create new assessment record
            assessment = QuizPackAssessment(
                quiz_pack_id=f"{session_data.subject}_{quiz_type}_{difficulty}",
                student_name=session_data.student_name,
                score=None,
                total_questions=question_count,
                completed_questions=0,
                start_time=datetime.now(),
                end_time=None,
                subject=session_data.subject,
                difficulty_level=difficulty
            )
            
            # Update session data
            session_data.current_quiz_id = assessment.quiz_pack_id
            session_data.quiz_progress = 0
            session_data.assessment = assessment
            
            # Log quiz start
            logger.info(
                f"Started quiz for {session_data.student_name} in {session_data.subject}: "
                f"{quiz_type} mode, {difficulty} difficulty, {question_count} questions"
            )
            
            return {
                "success": True,
                "message": (
                    f"🎉 Great! Let's start your {quiz_type} quiz in {session_data.subject} "
                    f"at {difficulty} difficulty level with {question_count} questions! "
                    f"I'm going to ask you questions one by one. Ready to show what you know? "
                    f"Remember, it's okay to make mistakes - that's how we learn! 😊"
                ),
                "quiz_info": {
                    "quiz_type": quiz_type,
                    "difficulty": difficulty,
                    "question_count": question_count,
                    "subject": session_data.subject,
                    "student_name": session_data.student_name
                },
                "next_action": "get_next_question",
                "assessment_id": assessment.quiz_pack_id
            }
            
        except ValueError as ve:
            logger.error(f"Validation error starting quiz: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error starting quiz: {str(e)}")
            raise e
    
    def get_child_friendly_error(self, error: Exception) -> str:
        """
        Get child-friendly error message for quiz start failures
        
        Args:
            error: The exception that occurred
            
        Returns:
            Child-friendly error message with recovery guidance
        """
        error_msg = str(error).lower()
        
        if "student name" in error_msg or "subject" in error_msg:
            return (
                "Oops! I need to know your name and favorite subject before we can start the quiz. "
                "Could you please tell me your name and whether you like Science, English, or Geography? "
                "Once I know that, we can start learning together right away! 📝"
            )
        elif "question" in error_msg:
            return (
                "Hmm, I had trouble setting up the quiz questions. Don't worry! "
                "Let's try starting the quiz again. Would you like to learn Science, English, or Geography today? "
                "I'll make sure everything works perfectly this time! 🔄"
            )
        else:
            return (
                "Oh dear! Something went wrong when I tried to start your quiz. "
                "No worries at all - technology can be tricky sometimes! 😊 "
                "Let's try again. Tell me what subject you'd like to learn and we'll get started with some fun questions! "
                "Remember, learning is a journey and we'll get there together!"
            )