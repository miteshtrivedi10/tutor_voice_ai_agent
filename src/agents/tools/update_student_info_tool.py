"""
UpdateStudentInfoTool - Single responsibility tool for updating student information
Follows SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution
"""

from typing import Dict, Any
import logging

from src.agents.interfaces import ITool, ToolExecutionContext, ToolResult
from src.services.session_manager import get_session_manager
from src.models.agent_dtos import MainAgentData

logger = logging.getLogger(__name__)


class UpdateStudentInfoTool(ITool):
    """Tool for updating student profile information"""
    
    def __init__(self, session_manager=None):
        self.session_manager = session_manager or get_session_manager()

    @property
    def name(self) -> str:
        return "update_student_info"
    
    @property
    def description(self) -> str:
        return (
            "Update student information including name, preferred subject, and learning preferences. "
            "Use this when the student provides new personal information or wants to change their "
            "learning preferences. This helps personalize the learning experience."
        )
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "Student's full name",
                    "maxLength": 100
                },
                "preferred_subject": {
                    "type": "string",
                    "enum": ["Science", "English", "Geography"],
                    "description": "Student's preferred subject for learning"
                },
                "learning_style": {
                    "type": "string",
                    "enum": ["visual", "auditory", "kinesthetic", "reading_writing"],
                    "description": "Student's preferred learning style (optional)"
                },
                "pace": {
                    "type": "string",
                    "enum": ["slow", "medium", "fast"],
                    "description": "Student's preferred learning pace (optional)"
                }
            },
            "required": ["student_name", "preferred_subject"]
        }
    
    async def execute(self, parameters: Dict[str, Any], context: ToolExecutionContext) -> ToolResult:
        """
        Execute the tool to update student information in session data
        
        Args:
            parameters: Dict containing student_name (required), preferred_subject (required), 
                       learning_style (optional), pace (optional)
            context: ToolExecutionContext with session data
            
        Returns:
            ToolResult with success status and updated information
        """
        try:
            # Validate required parameters
            if not parameters.get("student_name"):
                raise ValueError("Student name is required")
            if not parameters.get("preferred_subject"):
                raise ValueError("Preferred subject is required")
            
            # Get session data
            session_id = context.session_id
            session_data = context.session_data
            if not isinstance(session_data, MainAgentData):
                session_data = MainAgentData(**context.session_data)
            
            # Update session data
            session_data.student_name = parameters["student_name"]
            session_data.subject = parameters["preferred_subject"]
            
            # Update optional preferences
            if "learning_style" in parameters:
                session_data.learning_style = parameters["learning_style"]
            if "pace" in parameters:
                session_data.pace = parameters["pace"]
            
            # Update session in manager
            update_result = await self.session_manager.update_session_data(session_id, {
                "student_name": session_data.student_name,
                "subject": session_data.subject,
                "learning_style": getattr(session_data, 'learning_style', None),
                "pace": getattr(session_data, 'pace', None),
                "student_info_collected": True
            })
            
            # Log the update
            logger.info(
                f"Updated student info for session {session_id}: "
                f"{parameters['student_name']} - {parameters['preferred_subject']}"
            )
            
            return ToolResult(
                success=True,
                data={
                    "updated_fields": {
                        "student_name": parameters["student_name"],
                        "preferred_subject": parameters["preferred_subject"]
                    },
                    "next_action": "continue_conversation"
                },
                recovery_message=f"Successfully updated your information, {parameters['student_name']}! I'm excited to help you learn {parameters['preferred_subject']}!",
                conversation_context={"session_id": session_id}
            )
            
        except Exception as e:
            logger.error(f"Error updating student info: {str(e)}")
            recovery_message = self.get_child_friendly_error(e)
            return ToolResult(
                success=False,
                error=str(e),
                recovery_message=recovery_message,
                conversation_context={"session_id": context.session_id}
            )
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for tool calling.
        
        Returns:
            OpenAI-compatible tool schema dictionary
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def get_child_friendly_error(self, error: Exception) -> str:
        """
        Get child-friendly error message for recovery
        
        Args:
            error: The exception that occurred
            
        Returns:
            Child-friendly error message
        """
        error_msg = str(error).lower()
        
        if "name" in error_msg:
            return (
                "Oops! I had trouble with your name. Could you please tell me your name again? "
                "I promise I'll remember it this time! 😊"
            )
        elif "subject" in error_msg:
            return (
                "Hmm, I'm not sure about that subject. Could you tell me if you like Science, "
                "English, or Geography? I'll help you learn whichever one you choose! 📚"
            )
        else:
            return (
                "Oh no! Something went wrong when I tried to update your information. "
                "Don't worry, we can try again! Could you tell me your name and favorite subject? "
                "I'll make sure to get it right this time! 🌟"
            )