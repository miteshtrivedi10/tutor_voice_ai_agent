
"""
DEPRECATED: DataCollectionTask - replaced by UpdateStudentInfoTool in new tool-based architecture.

MIGRATION NOTICE:
This task functionality has been completely integrated into the UpdateStudentInfoTool.
All name/subject collection, validation, and session updating now handled through single tool.

REPLACEMENT:
- Functionality: UpdateStudentInfoTool.execute()
- Orchestration: VoiceTutorAgent.process_user_input() with tool calling
- State Management: SessionManager.update_session_data()

This file is deprecated and will be removed after migration validation.
"""
from typing import Any
import warnings

warnings.warn("DataCollectionTask is DEPRECATED - use UpdateStudentInfoTool instead", DeprecationWarning)

# Legacy class definition - DO NOT USE IN NEW CODE
class DataCollectionTask:
    """
    DEPRECATED: Legacy data collection task class.
    All functionality migrated to tool-based system.
    """
    
    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "DataCollectionTask is no longer supported. "
            "Use UpdateStudentInfoTool from src/agents/tools/update_student_info_tool.py "
            "and the single VoiceTutorAgent from src/agents/single_agent.py instead. "
            "The new tool handles name extraction, subject validation, and session updates "
            "through LLM tool calling with comprehensive error handling."
        )
    
    async def on_enter(self) -> None:
        """DEPRECATED: Moved to tool execution in single agent."""
        raise DeprecationWarning("Use new tool-based architecture")
    
    async def on_user_turn_completed(self, *args, **kwargs) -> None:
        """DEPRECATED: Replaced by LLM tool calling and response processing."""
        raise DeprecationWarning("Use new tool-based architecture")
    
    async def on_exit(self) -> None:
        """DEPRECATED: Moved to session state management in SessionManager."""
        raise DeprecationWarning("Use new tool-based architecture")

# Migration helper for data collection specifically
class DataCollectionMigrationHelper:
    """Helper class to assist with migration from DataCollectionTask to tool-based system."""
    
    @staticmethod
    def get_replacement_tool():
        """Get the replacement tool for DataCollectionTask functionality."""
        from src.agents.tools.update_student_info_tool import UpdateStudentInfoTool
        return UpdateStudentInfoTool()
    
    @staticmethod
    def get_migration_guide():
        """Get detailed migration guide for data collection functionality."""
        return """
DATA COLLECTION TASK MIGRATION GUIDE:

OLD IMPLEMENTATION (DEPRECATED):
class DataCollectionTask(AgentTask):
    async def on_enter(self):
        # Prompt for name and subject
        await self.agent.session.generate_reply(...)

    async def on_user_turn_completed(self, ...):
        # Simple parsing of user input
        if "name" in user_input.lower():
            await update_student_name(...)
        # Check if data complete, switch tasks

NEW IMPLEMENTATION (TOOL-BASED):
1. Single UpdateStudentInfoTool handles ALL data collection:
   - Tool name: update_student_info
   - Parameters: {"student_input": raw_user_response, "session_id": "..."}
   - Automatic name extraction using regex patterns
   - Subject validation against allowed list
   - Session data updates through SessionManager
   - Comprehensive error handling with child-friendly recovery

2. Conversation flow in VoiceTutorAgent:
   # System prompt guides LLM: "use update_student_info tool to collect name/subject"
   await agent.process_user_input(user_input)
   # LLM automatically calls tool when appropriate
   tool_result = await update_student_info_tool.execute(params)
   # Natural response generation incorporating tool results

3. Key improvements in new system:
   - No rigid task switching - LLM decides flow naturally
   - Better error handling with fallback strategies
   - Single tool handles both name AND subject collection
   - Conversation history maintained for context
   - Age-appropriate recovery messages

MIGRATION STEPS:
1. Remove DataCollectionTask imports and references
2. Update system prompt to mention update_student_info tool
3. Test natural conversation flow for data collection
4. Verify session data persistence through SessionManager
5. Remove this file after validation

NEW TOOL FEATURES:
- Semantic name extraction from natural speech
- Subject validation with helpful suggestions
- Automatic session state updates
- Child-friendly error messages for validation failures
- Fallback strategies (retry, simplified, skip)
- Integration with conversation history for context
"""
__all__ = []  # No exports - deprecated module
__deprecated__ = True
__replacement_tool__ = "UpdateStudentInfoTool"
__migration_status__ = "complete"