"""
Interfaces for the voice tutor agent tools and services
Defines contracts following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class FallbackStrategy(Enum):
    """Standard fallback strategies for tool failures."""
    RETRY = "retry"
    SIMPLIFIED = "simplified"
    CACHED = "cached"
    EMERGENCY = "emergency"
    SKIP = "skip"
    HUMAN_HANDOFF = "human_handoff"
    GRACEFUL_END = "graceful_end"


@dataclass
class RecoveryMessageConfig:
    """Configuration for child-friendly recovery messages."""
    error_type: str
    primary_message: str
    fallback_message: str
    tone: str  # e.g., "friendly_reminder", "magical_adventure"
    age_group: str  # e.g., "6-12"
    emotional_impact: str  # e.g., "low", "medium"


@dataclass
class ToolExecutionContext:
    """
    Context for tool execution containing session information
    """
    session_id: str
    session_data: Any  # MainAgentData or session dict


@dataclass
class ToolResult:
    """
    Result from tool execution with error handling information
    """
    success: bool
    data: Any = None
    error: str = ""
    fallback_action: str = ""
    recovery_message: str = ""
    retry_count: int = 0
    conversation_context: Dict[str, Any] = None


class ITool(ABC):
    """
    Interface for all agent tools following Single Responsibility Principle
    Each tool implements one specific educational function
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the tool"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for LLM tool selection"""
        pass

    @abstractmethod
    async def execute(self, args: Dict[str, Any], context: ToolExecutionContext) -> ToolResult:
        """
        Execute the tool functionality
        
        Args:
            args: Tool arguments from LLM call
            context: ToolExecutionContext for session data
            
        Returns:
            ToolResult with success status, data, and error handling info
        """
        pass

    @abstractmethod
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool calling integration
        
        Returns:
            OpenAI-compatible tool schema dictionary
        """
        pass


class IToolRegistry(ABC):
    """
    Interface for tool registry following Open/Closed Principle
    Allows adding new tools without modifying existing code
    """

    @abstractmethod
    def register_tool(self, tool: ITool) -> None:
        """Register a new tool in the registry"""
        pass

    @abstractmethod
    def get_tool_by_name(self, name: str) -> ITool:
        """
        Get tool by name
        
        Args:
            name: Tool name
            
        Returns:
            ITool instance or None if not found
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools with schemas
        
        Returns:
            List of tool schemas for LLM integration
        """
        pass

    @abstractmethod
    def get_tool_count(self) -> int:
        """Get number of registered tools"""
        pass


class ISessionManager(ABC):
    """
    Interface for session management following Dependency Inversion Principle
    Abstracts data persistence and session state operations
    """

    @abstractmethod
    async def create_session(self, session_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create new session"""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data"""
        pass

    @abstractmethod
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        pass

    @abstractmethod
    async def end_session(self, session_id: str, reason: str = "completed") -> bool:
        """End session and cleanup"""
        pass

    @abstractmethod
    async def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history"""
        pass

    @abstractmethod
    async def save_conversation_turn(self, session_id: str, role: str, content: str) -> bool:
        """Save single conversation turn"""
        pass

    @abstractmethod
    async def save_assessment(self, session_id: str, assessment_data: Dict[str, Any]) -> bool:
        """Save assessment results"""
        pass

    @abstractmethod
    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        pass

    @abstractmethod
    def get_session_manager(self) -> 'ISessionManager':
        """Get singleton instance"""
        pass