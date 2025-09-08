"""
DEPRECATED: Task implementations - replaced by tool-based architecture.

All functionality from these tasks has been migrated to the new single VoiceTutorAgent
with tool calling system in src/agents/single_agent.py and tools in src/agents/tools/.

MIGRATION STATUS: COMPLETE
- GreetingTask → UpdateStudentInfoTool
- DataCollectionTask → UpdateStudentInfoTool
- QuizTask → StartQuizTool, GetNextQuestionTool, EvaluateAnswerTool, EndQuizTool

This module and its contents are deprecated and will be removed in future versions.
Current implementation uses prompt-driven single agent with comprehensive tool system.

For new development, use:
- src/agents/single_agent.py (main agent)
- src/agents/tools/ (individual operation tools)
- src/services/session_manager.py (state management)
"""
# DEPRECATED IMPORTS - DO NOT USE IN NEW CODE
# from .greeting_task import GreetingTask  # Replaced by UpdateStudentInfoTool
# from .data_collection_task import DataCollectionTask  # Replaced by UpdateStudentInfoTool
# from .quiz_task import QuizTask  # Replaced by quiz management tools

# Migration guidance
class MigrationNotice:
    """Migration notice for developers transitioning from task-based to tool-based system."""
    def __init__(self):
        self.deprecated = True
        self.replacement = "src/agents/single_agent.VoiceTutorAgent"
        self.tools_directory = "src/agents/tools/"
        self.services_directory = "src/services/"
    
    def get_migration_guide(self):
        return """
MIGRATION GUIDE: Task-Based → Tool-Based Architecture

REMOVED COMPONENTS:
├── src/agents/tasks/ (entire directory - DEPRECATED)
├── src/agents/fsm.py (state management moved to SessionManager)
└── Sequential task methods (on_enter, on_user_turn_completed, on_exit)

NEW ARCHITECTURE:
├── src/agents/single_agent.py (VoiceTutorAgent - single orchestrator)
├── src/agents/tools/ (individual operation tools)
│   ├── update_student_info_tool.py
│   ├── quiz_management_tools.py
│   └── evaluate_answer_tool.py
├── src/services/session_manager.py (state persistence)
├── src/services/tool_registry.py (dynamic tool discovery)
└── src/services/llm_service.py (model integration)

KEY CHANGES:
1. Single agent replaces multiple task classes (SRP compliance)
2. Tools handle specific operations with error handling (OCP compliance)
3. SessionManager handles state (DIP compliance)
4. Comprehensive system prompt drives conversation flow
5. LLM tool calling replaces sequential method calls

MIGRATION STEPS:
1. Update imports to use new single agent entrypoint
2. Remove task-specific logic - use tool calls instead
3. Update session data access to use SessionManager
4. Test tool-based conversation flow
5. Remove deprecated task files after validation
"""

__all__ = []  # No exports - deprecated module
__deprecated__ = True
__version__ = "deprecated-v1"
__replacement__ = "tool-based-architecture-v2"