"""
ToolRegistry service implementing IToolRegistry interface.
Manages tool registration, discovery, and selection for the prompt-driven voice agent.
Follows Open/Closed Principle - new tools can be added without modifying registry.
"""
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from src.agents.interfaces import ITool, IToolRegistry

class ToolRegistry(IToolRegistry):
    """
    Concrete implementation of tool registry service.
    Single responsibility: Manage tool lifecycle and discovery.
    """
    
    def __init__(self):
        self._registered_tools: Dict[str, ITool] = {}
        self._tools_by_category: Dict[str, List[ITool]] = {}
        self._tool_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Define tool categories for context-aware selection
        self.categories = {
            "student_info": ["update_student_info"],
            "quiz_management": ["start_quiz", "get_next_question", "end_quiz"],
            "answer_evaluation": ["evaluate_answer"],
            "session_control": [],  # For future session management tools
            "logging": []  # For usage logging tools
        }
    
    def register_tool(self, tool: ITool) -> None:
        """
        Register a new tool with the registry.
        
        Args:
            tool: ITool implementation to register
            
        Raises:
            ValueError: If tool name already exists or tool is invalid
        """
        if not isinstance(tool, ITool):
            raise ValueError(f"Tool must implement ITool interface, got {type(tool)}")
        
        tool_name = tool.name
        
        if tool_name in self._registered_tools:
            raise ValueError(f"Tool with name '{tool_name}' is already registered")
        
        # Validate tool properties
        if not tool.description or len(tool.description) < 10:
            raise ValueError(f"Tool '{tool_name}' must have meaningful description")
        
        if not tool.parameters_schema or not isinstance(tool.parameters_schema, dict):
            raise ValueError(f"Tool '{tool_name}' must have valid parameters schema")
        
        # Register tool
        self._registered_tools[tool_name] = tool
        self._tool_schemas[tool_name] = self._build_tool_schema(tool)
        
        # Categorize tool for context-aware selection
        self._categorize_tool(tool)
        
        print(f"Tool '{tool_name}' registered successfully")  # Replace with logger
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of all available tools with complete schemas for LLM.
        
        Returns:
            List of tool descriptions with name, description, and parameters
        """
        available_tools = []
        
        for tool_name, tool in self._registered_tools.items():
            tool_info = {
                "type": "function",
                "function": self._tool_schemas[tool_name]
            }
            available_tools.append(tool_info)
        
        return available_tools
    
    def get_tool_by_name(self, name: str) -> ITool:
        """
        Retrieve a specific tool by name.
        
        Args:
            name: Tool name to retrieve
            
        Returns:
            Registered ITool instance or None if not found
        """
        return self._registered_tools.get(name)
    
    def get_tools_for_context(self, context_type: str) -> List[ITool]:
        """
        Get relevant tools for specific conversation context.
        
        Args:
            context_type: Context identifier (e.g., "initial_greeting", "quiz_active")
            
        Returns:
            List of relevant tools for the context
        """
        relevant_categories = self._get_categories_for_context(context_type)
        relevant_tools = []
        
        for category in relevant_categories:
            if category in self._tools_by_category:
                relevant_tools.extend(self._tools_by_category[category])
        
        return list(set(relevant_tools))  # Remove duplicates
    
    def get_tool_categories(self) -> Dict[str, List[str]]:
        """
        Get all tool categories and their associated tool names.
        
        Returns:
            Dictionary mapping categories to lists of tool names
        """
        categories_info = {}
        for category, tools in self._tools_by_category.items():
            categories_info[category] = [tool.name for tool in tools]
        return categories_info
    
    def get_tool_count(self) -> int:
        """Get total number of registered tools."""
        return len(self._registered_tools)
    
    def validate_tool_schema(self, tool_name: str) -> bool:
        """
        Validate that a tool's schema is properly formatted.
        
        Args:
            tool_name: Name of tool to validate
            
        Returns:
            True if schema is valid, False otherwise
        """
        schema = self._tool_schemas.get(tool_name)
        if not schema:
            return False
        
        # Basic schema validation
        required_fields = ["name", "description", "parameters"]
        for field in required_fields:
            if field not in schema:
                return False
        
        if not isinstance(schema["parameters"], dict):
            return False
        
        return True
    
    def _build_tool_schema(self, tool: ITool) -> Dict[str, Any]:
        """Build complete JSON schema for a tool."""
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters_schema
        }
    
    def _categorize_tool(self, tool: ITool) -> None:
        """Categorize tool based on its name and purpose."""
        tool_name = tool.name.lower()
        categories_assigned = []
        
        # Simple categorization based on tool name patterns
        if "student" in tool_name or "info" in tool_name or "name" in tool_name:
            categories_assigned.append("student_info")
        elif any(word in tool_name for word in ["quiz", "question", "start", "end"]):
            categories_assigned.append("quiz_management")
        elif "evaluate" in tool_name or "answer" in tool_name or "score" in tool_name:
            categories_assigned.append("answer_evaluation")
        elif "session" in tool_name or "log" in tool_name:
            categories_assigned.append("session_control")
        else:
            # Default category
            categories_assigned.append("general")
        
        # Register in categories
        for category in categories_assigned:
            if category not in self._tools_by_category:
                self._tools_by_category[category] = []
            if tool not in self._tools_by_category[category]:
                self._tools_by_category[category].append(tool)
    
    def _get_categories_for_context(self, context_type: str) -> List[str]:
        """Map conversation context to relevant tool categories."""
        context_mappings = {
            "initial_greeting": ["student_info"],
            "collecting_info": ["student_info"],
            "quiz_start": ["quiz_management"],
            "quiz_active": ["quiz_management", "answer_evaluation"],
            "quiz_completed": ["quiz_management"],
            "error_recovery": ["session_control"],
            "session_end": ["session_control"]
        }
        
        # Get primary categories for context
        primary_categories = context_mappings.get(context_type, ["general"])
        
        # Add fallback categories based on session state
        fallback_categories = []
        if "quiz" in context_type:
            fallback_categories.append("answer_evaluation")
        elif "info" in context_type:
            fallback_categories.append("student_info")
        
        return list(set(primary_categories + fallback_categories))
    
    def _validate_all_tools(self) -> Dict[str, List[str]]:
        """
        Validate all registered tools and return validation report.
        
        Returns:
            Dictionary with validation status for each tool
        """
        validation_report = {}
        
        for tool_name, tool in self._registered_tools.items():
            is_valid = self.validate_tool_schema(tool_name)
            validation_report[tool_name] = {
                "valid": is_valid,
                "description_length": len(tool.description),
                "has_parameters": bool(tool.parameters_schema and tool.parameters_schema.get("properties")),
                "categories": [cat for cat, tools in self._tools_by_category.items() if tool in tools]
            }
        
        return validation_report

# Global registry instance for dependency injection
tool_registry_instance = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return tool_registry_instance

# Auto-register common tools on import (following Open/Closed principle)
def initialize_default_tools():
    """Initialize registry with default tools."""
    from src.agents.tools.update_student_info_tool import UpdateStudentInfoTool
    from src.agents.tools.quiz_management_tools import StartQuizTool, GetNextQuestionTool
    from src.agents.tools.end_quiz_tool import EndQuizTool
    from src.agents.tools.evaluate_answer_tool import EvaluateAnswerTool
    
    registry = get_tool_registry()
    
    try:
        registry.register_tool(UpdateStudentInfoTool())
        registry.register_tool(StartQuizTool())
        registry.register_tool(GetNextQuestionTool())
        registry.register_tool(EndQuizTool())
        registry.register_tool(EvaluateAnswerTool())
        
        print(f"Default tools initialized: {registry.get_tool_count()} tools registered")
        return True
    except Exception as e:
        print(f"Error initializing default tools: {str(e)}")
        return False

# Initialize on import
initialize_default_tools()