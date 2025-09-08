"""
DEPRECATED: QuizTask - replaced by quiz management tools in new tool-based architecture.

MIGRATION NOTICE:
This entire quiz task has been replaced by four specialized tools:
1. StartQuizTool - Initializes quiz session
2. GetNextQuestionTool - Retrieves and presents questions
3. EvaluateAnswerTool - Scores answers with semantic analysis
4. EndQuizTool - Generates completion summary

All quiz flow now handled through LLM tool calling in single VoiceTutorAgent.

REPLACEMENT SYSTEM:
- Orchestration: VoiceTutorAgent.process_user_input()
- Tools: src/agents/tools/quiz_management_tools.py and evaluate_answer_tool.py
- State Management: SessionManager tracks quiz progress
- Error Handling: Comprehensive tool-level error handling with child-friendly recovery

This file is deprecated and will be removed after migration validation.
"""
from typing import Any
import warnings

warnings.warn("QuizTask is DEPRECATED - use quiz management tools instead", DeprecationWarning)

# Legacy class definition - DO NOT USE IN NEW CODE
class QuizTask:
    """
    DEPRECATED: Legacy quiz task class.
    All quiz functionality migrated to tool-based system.
    """
    
    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "QuizTask is no longer supported. The new tool-based architecture uses:\n"
            "1. StartQuizTool for quiz initialization\n"
            "2. GetNextQuestionTool for question presentation\n"
            "3. EvaluateAnswerTool for answer scoring\n"
            "4. EndQuizTool for quiz completion\n\n"
            "Use VoiceTutorAgent from src/agents/single_agent.py with comprehensive system prompt.\n"
            "Migration guide available in src/agents/tasks/__init__.py"
        )
    
    async def on_enter(self) -> None:
        """DEPRECATED: Moved to StartQuizTool execution."""
        raise DeprecationWarning("Use StartQuizTool in new architecture")
    
    async def _ask_next_question(self) -> None:
        """DEPRECATED: Replaced by GetNextQuestionTool."""
        raise DeprecationWarning("Use GetNextQuestionTool in new architecture")
    
    async def on_user_turn_completed(self, *args, **kwargs) -> None:
        """DEPRECATED: Replaced by EvaluateAnswerTool tool calling."""
        raise DeprecationWarning("Use EvaluateAnswerTool in new architecture")
    
    async def _evaluate_answer(self, *args, **kwargs) -> Any:
        """DEPRECATED: Moved to EvaluateAnswerTool semantic analysis."""
        raise DeprecationWarning("Use EvaluateAnswerTool in new architecture")
    
    async def _end_quiz(self) -> None:
        """DEPRECATED: Moved to EndQuizTool completion handling."""
        raise DeprecationWarning("Use EndQuizTool in new architecture")
    
    async def on_exit(self) -> None:
        """DEPRECATED: Moved to session cleanup in SessionManager."""
        raise DeprecationWarning("Use new tool-based architecture")

# Migration helper for quiz functionality specifically
class QuizTaskMigrationHelper:
    """Helper class to assist with migration from QuizTask to tool-based system."""
    
    @staticmethod
    def get_replacement_tools():
        """Get all replacement tools for QuizTask functionality."""
        from src.agents.tools.quiz_management_tools import StartQuizTool, GetNextQuestionTool, EndQuizTool
        from src.agents.tools.evaluate_answer_tool import EvaluateAnswerTool
        return {
            "start_quiz": StartQuizTool(),
            "get_next_question": GetNextQuestionTool(),
            "evaluate_answer": EvaluateAnswerTool(),
            "end_quiz": EndQuizTool()
        }
    
    @staticmethod
    def get_quiz_flow_diagram():
        """Get visual representation of new quiz flow."""
        return """
NEW QUIZ FLOW (TOOL-BASED ARCHITECTURE):

[User Input] → [VoiceTutorAgent.process_user_input()]
                    ↓
            [LLM with System Prompt]
                    ↓
    ┌─────────────────┬─────────────────┬─────────────────┐
    │   Greeting/     │   Quiz Active   │   Quiz End      │
    │   Info Phase    │   Phase         │   Phase         │
    └─────────────────┼─────────────────┼─────────────────┘
                     │                 │                 │
              ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
              │update_      │  │get_next_    │  │end_quiz     │
              │student_info │  │question     │  │tool         │
              └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                     │                 │                 │
              ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
              │start_quiz   │  │evaluate_    │  │Session      │
              │tool         │  │answer tool  │  │Manager      │
              └──────┬──────┘  └──────┬──────┘  │updates      │
                     │                 │         └──────────────┘
              ┌──────▼──────┐         │
              │Session      │         │
              │updates      │         │
              └──────────────┘         │
                                     │
                              ┌──────▼──────┐
                              │Next User    │
                              │Input        │
                              └──────────────┘

KEY IMPROVEMENTS:
1. No rigid state transitions - LLM decides flow naturally
2. Each tool has single responsibility with error handling
3. Comprehensive session state management
4. Child-friendly recovery messages for all failures
5. Easy to extend with new tools (Open/Closed Principle)
"""
    
    @staticmethod
    def get_migration_guide():
        """Get detailed migration guide for quiz functionality."""
        return """
QUIZ TASK MIGRATION GUIDE:

OLD IMPLEMENTATION (DEPRECATED):
class QuizTask(AgentTask):
    async def on_enter(self):
        # Initialize quiz engine
        self.quiz_engine = await QuizTaskEngine(...)
        await self._ask_next_question()

    async def on_user_turn_completed(self, ...):
        # Sequential evaluation and next question
        evaluation = await self._evaluate_answer(user_answer)
        self.current_question += 1
        await self._ask_next_question()

NEW IMPLEMENTATION (TOOL-BASED):
1. FOUR specialized tools replace entire QuizTask:
   a. StartQuizTool - Replaces on_enter initialization
   b. GetNextQuestionTool - Replaces _ask_next_question method
   c. EvaluateAnswerTool - Replaces _evaluate_answer with semantic LLM analysis
   d. EndQuizTool - Replaces _end_quiz with comprehensive summary

2. Conversation flow in single VoiceTutorAgent:
   # System prompt guides: "use get_next_question tool to ask questions one by one"
   await agent.process_user_input(user_input)
   # LLM calls appropriate tool based on conversation context
   tool_result = await get_next_question_tool.execute(params)
   # Natural response: "Here's question 2: What color is the sky?"

3. Key improvements:
   - No sequential method calls - LLM decides flow dynamically
   - Semantic answer evaluation with LLM (not simple string matching)
   - Emergency fallback questions when database fails
   - Child-friendly error messages for all failure scenarios
   - SessionManager tracks progress across tool calls
   - Easy to add new quiz types by adding tools

MIGRATION STEPS:
1. Remove QuizTask imports and references
2. Update system prompt to mention quiz management tools
3. Test complete quiz flow: start → question → answer → evaluation → end
4. Verify session state persistence and score tracking
5. Remove this file after full validation

NEW TOOL INTEGRATION:
- StartQuizTool: Fetches questions, initializes session state
- GetNextQuestionTool: Presents questions with progress tracking
- EvaluateAnswerTool: Semantic scoring with encouragement feedback
- EndQuizTool: Generates celebratory completion summary

All tools include comprehensive error handling with child-friendly recovery messages.
"""
__all__ = []  # No exports - deprecated module
__deprecated__ = True
__replacement_tools__ = ["StartQuizTool", "GetNextQuestionTool", "EvaluateAnswerTool", "EndQuizTool"]
__migration_status__ = "complete"