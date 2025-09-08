"""
LLMService - Service layer for LLM integration with tool calling support
Implements dependency injection and error handling for the voice tutor agent
Uses meta-llama/llama-3.1-8b-instruct:free model as specified
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncIterable
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI

from src.config.settings import LLM_API_KEY, LLM_MODEL_NAME, LLM_BASE_URL
from src.agents.interfaces import ToolResult, ToolExecutionContext
from src.config.logging_config import logger


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROK = "grok"
    LLAMA = "llama"


@dataclass
class LLMResponse:
    """Structured response from LLM call"""
    content: str
    tool_calls: List[Dict[str, Any]] = None
    usage: Dict[str, int] = None  # token usage
    finish_reason: str = None
    error: Optional[str] = None
    model_used: str = None


class LLMService:
    """Service class for LLM operations with tool calling support"""
    
    def __init__(self):
        self.model_name = LLM_MODEL_NAME or "meta-llama/llama-3.1-8b-instruct:free"
        self.api_key = LLM_API_KEY
        self.base_url = LLM_BASE_URL or None
        
        # Initialize OpenAI client for compatibility with various providers
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=30.0
        )
        
        self.max_retries = 3
        self.retry_delay = 2.0
        self.logger = logger
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> LLMResponse:
        """
        Generate response from LLM with optional tool calling
        
        Args:
            messages: List of chat messages
            tools: List of tool definitions for function calling
            tool_choice: Tool choice strategy ("auto", "none", or specific tool name)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            LLMResponse with generated content and tool calls
        """
        for attempt in range(self.max_retries):
            try:
                # Prepare messages for tool calling
                formatted_messages = self._format_messages_for_tools(messages, tools)
                
                # Create tool definitions if provided
                tool_defs = None
                if tools:
                    tool_defs = {
                        "type": "function",
                        "functions": tools
                    }
                
                # Make API call
                if stream:
                    response = await self._stream_chat_completion(
                        formatted_messages, tool_defs, tool_choice, temperature, max_tokens
                    )
                else:
                    response = await self._chat_completion(
                        formatted_messages, tool_defs, tool_choice, temperature, max_tokens
                    )
                
                return LLMResponse(
                    content=response.get("content", ""),
                    tool_calls=response.get("tool_calls", []),
                    usage=response.get("usage", {}),
                    finish_reason=response.get("finish_reason", "stop"),
                    model_used=self.model_name
                )
                
            except Exception as e:
                self.logger.error(f"LLM generation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    return LLMResponse(
                        content="",
                        error=f"LLM service failed after {self.max_retries} attempts: {str(e)}",
                        model_used=self.model_name
                    )
                
                # Exponential backoff
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def execute_tool_call(
        self, 
        tool_call: Dict[str, Any], 
        context: ToolExecutionContext
    ) -> ToolResult:
        """
        Execute a tool call from LLM response
        
        Args:
            tool_call: Tool call from LLM response
            context: Execution context
            
        Returns:
            ToolResult with execution outcome
        """
        try:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})
            
            # Get tool from registry (implementation would use ToolRegistry)
            # For now, simulate tool execution
            tool_result = await self._simulate_tool_execution(tool_name, arguments, context)
            
            return tool_result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return ToolResult(
                status="error",
                data={},
                message="Tool execution failed",
                error=e,
                fallback_used=True
            )
    
    async def get_system_prompt(self, context: ToolExecutionContext) -> str:
        """
        Generate context-aware system prompt for the LLM
        
        Args:
            context: Current execution context
            
        Returns:
            Formatted system prompt
        """
        session_data = context.session_data
        
        base_prompt = f"""You are a friendly and encouraging educational assistant for children aged {getattr(session_data, 'child_age', 9)}.
You help students learn {session_data.subject} through interactive quizzes and conversations.

IMPORTANT GUIDELINES:
- Always be encouraging and positive
- Use simple language appropriate for children
- Break down complex concepts into easy steps
- Celebrate effort, not just correct answers
- Provide gentle corrections for wrong answers
- Use emojis to make responses engaging 🎉📚
- Keep responses conversational and natural
- Adapt difficulty based on student performance

CURRENT STUDENT: {session_data.student_name}
SUBJECT: {session_data.subject}
SESSION STATUS: {getattr(session_data, 'session_status', 'active')}

If the student is taking a quiz:
- Ask one question at a time
- Provide clear multiple choice options when appropriate
- Give positive feedback after each answer
- Track progress and celebrate milestones
- Offer hints if the student asks or seems stuck

For tool usage:
- Use tools only when necessary for the conversation flow
- Always explain what you're doing when using tools
- Handle tool errors gracefully with child-friendly messages

Remember: Learning is about growth and curiosity, not perfection!"""

        return base_prompt
    
    def _format_messages_for_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format messages for tool calling compatibility
        
        Args:
            messages: Original messages
            tools: Tool definitions
            
        Returns:
            Formatted messages with tool context
        """
        formatted = []
        
        for message in messages:
            formatted_message = {"role": message["role"], "content": message["content"]}
            
            # Add tool_calls if present and format them
            if "tool_calls" in message:
                formatted_message["tool_calls"] = message["tool_calls"]
            
            formatted.append(formatted_message)
        
        # Add system message about available tools if tools exist
        if tools:
            formatted.insert(0, {
                "role": "system",
                "content": "You have access to the following tools. Use them when appropriate for the conversation. Always respond in a child-friendly manner."
            })
        
        return formatted
    
    async def _chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict]]],
        tool_choice: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Internal method for non-streaming chat completion"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if tools else None
            )
            
            choice = response.choices[0]
            message = choice.message
            
            result = {
                "content": message.content or "",
                "tool_calls": [tc.model_dump() for tc in message.tool_calls] if message.tool_calls else [],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": choice.finish_reason
            }
            
            self.logger.debug(f"LLM response generated: {len(result['content'])} chars, {len(result['tool_calls'])} tool calls")
            return result
            
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"LLM API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected LLM error: {str(e)}")
            raise e
    
    async def _stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict]]],
        tool_choice: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncIterable[Dict[str, Any]]:
        """Internal method for streaming chat completion"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield {
                        "delta": chunk.choices[0].delta.content,
                        "finish_reason": chunk.choices[0].finish_reason
                    }
                    
        except Exception as e:
            self.logger.error(f"Streaming LLM error: {str(e)}")
            yield {"error": str(e)}
    
    async def _simulate_tool_execution(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        context: ToolExecutionContext
    ) -> ToolResult:
        """Simulate tool execution for testing (replace with actual tool registry)"""
        # This would integrate with actual ToolRegistry in production
        simulated_results = {
            "update_student_info": {
                "success": True,
                "message": f"Simulated update for {arguments.get('student_name', 'Student')}",
                "data": arguments
            },
            "start_quiz": {
                "success": True,
                "message": f"Quiz started for {context.session_data.student_name}",
                "data": {"quiz_id": f"sim_{tool_name}_{datetime.now().timestamp()}"}
            },
            "get_next_question": {
                "success": True,
                "message": "Here's your question!",
                "data": {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": "4"
                }
            },
            "evaluate_answer": {
                "success": True,
                "message": "Great answer!",
                "data": {"is_correct": True, "explanation": "Well done!"}
            },
            "end_quiz": {
                "success": True,
                "message": "Quiz completed!",
                "data": {"final_score": 85, "total_questions": 5}
            }
        }
        
        if tool_name in simulated_results:
            return ToolResult(
                status="success",
                data=simulated_results[tool_name]["data"],
                message=simulated_results[tool_name]["message"]
            )
        else:
            return ToolResult(
                status="error",
                data={},
                message=f"Unknown tool: {tool_name}",
                error=ValueError(f"Tool {tool_name} not implemented")
            )
    
    async def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool parameters against schema"""
        # Implementation would use tool registry to get parameter schema
        # For now, basic validation
        valid_params = parameters.copy()
        
        if tool_name == "update_student_info":
            if "student_name" in valid_params and len(valid_params["student_name"]) > 100:
                valid_params["student_name"] = valid_params["student_name"][:100]
            if "preferred_subject" in valid_params and valid_params["preferred_subject"] not in ["Science", "English", "Geography"]:
                valid_params["preferred_subject"] = "Science"  # Default fallback
        
        return valid_params


# Global instance for dependency injection
llm_service_instance = LLMService()

async def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    return llm_service_instance