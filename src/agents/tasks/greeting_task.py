"""
DEPRECATED: GreetingTask - replaced by UpdateStudentInfoTool in new tool-based architecture.

MIGRATION NOTICE:
This task has been completely replaced by the UpdateStudentInfoTool in src/agents/tools/
All greeting and initial data collection functionality now handled through LLM tool calling
in the single VoiceTutorAgent system.

REPLACEMENT:
- Functionality: UpdateStudentInfoTool.execute()
- Orchestration: VoiceTutorAgent.process_user_input()
- State Management: SessionManager service

This file is deprecated and will be removed after migration validation.
"""
from typing import Any
import warnings

warnings.warn("GreetingTask is DEPRECATED - use UpdateStudentInfoTool instead", DeprecationWarning)

# Legacy class definition - DO NOT USE IN NEW CODE
class GreetingTask:
    """
    DEPRECATED: Legacy greeting task class.
    All functionality migrated to tool-based system.
    """
    
    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "GreetingTask is no longer supported. "
            "Use UpdateStudentInfoTool from src/agents/tools/update_student_info_tool.py "
            "and VoiceTutorAgent from src/agents/single_agent.py instead. "
            "Migration guide available in src/agents/tasks/__init__.py"
        )
    
    async def on_enter(self) -> None:
        """DEPRECATED: Moved to tool initialization in single agent."""
        raise DeprecationWarning("Use new tool-based architecture")
    
    async def on_user_turn_completed(self, *args, **kwargs) -> None:
        """DEPRECATED: Replaced by tool calling in LLM response processing."""
        raise DeprecationWarning("Use new tool-based architecture")
    
    async def on_exit(self) -> None:
        """DEPRECATED: Moved to session cleanup in SessionManager."""
        raise DeprecationWarning("Use new tool-based architecture")

# Migration helper
class GreetingTaskMigrationHelper:
    """Helper class to assist with migration from task-based to tool-based system."""
    
    @staticmethod
    def get_replacement_tool():
        """Get the replacement tool for GreetingTask functionality."""
        from src.agents.tools.update_student_info_tool import UpdateStudentInfoTool
        return UpdateStudentInfoTool()
    
    @staticmethod
    def get_migration_guide():
        """Get detailed migration guide for this specific task."""
        return """
GREETING TASK MIGRATION GUIDE:

OLD IMPLEMENTATION (DEPRECATED):
class GreetingTask(AgentTask):
    async def on_enter(self):
        # Generate initial greeting
        await self.agent.session.generate_reply(...)

    async def on_user_turn_completed(self, ...):
        # Parse user input for name/subject
        if "name" in user_input:
            # Switch to DataCollectionTask

NEW IMPLEMENTATION (TOOL-BASED):
1. Single VoiceTutorAgent handles all conversation flow
2. Comprehensive system prompt guides initial greeting:
   "Start by warmly greeting and using update_student_info tool to collect name/subject"

3. UpdateStudentInfoTool replaces both GreetingTask and DataCollectionTask:
   - Tool name: update_student_info
   - Parameters: {"student_input": "user response", "session_id": "..."}
   - Handles name extraction, subject validation, session updates
   - Returns ToolResult with recovery messages

4. Conversation flow in single agent:
   await agent.process_user_input(user_input)
   # LLM decides to call update_student_info tool based on system prompt
   # Tool executes and returns structured result
   # Agent generates natural response incorporating tool result

MIGRATION STEPS:
1. Remove GreetingTask and DataCollectionTask imports
2. Update main entrypoint to use create_voice_tutor_agent_entrypoint()
3. Test initial greeting flow with new tool calling
4. Verify student info collection works through LLM tool selection
5. Remove this file after validation

NEW SYSTEM BENEFITS:
- Single agent handles all conversation stages (SRP)
- LLM decides when to collect info naturally (no rigid state transitions)
- Comprehensive error handling with child-friendly recovery
- Easy to extend with new tools without agent modification (OCP)
- Better context awareness through conversation history
"""

__all__ = []  # No exports - deprecated module
__deprecated__ = True
__replacement_tool__ = "UpdateStudentInfoTool"
__migration_status__ = "complete"