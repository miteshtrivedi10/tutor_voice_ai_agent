"""
Base classes for implementing tools in the prompt-driven voice agent.
Provides common error handling and child-friendly recovery mechanisms.
"""
import asyncio
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from src.agents.interfaces import ITool, ToolResult

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

class BaseTool(ABC):
    """Base class for all tools providing common functionality and error handling."""
    
    def __init__(self, name: str, description: str, max_retries: int = 3):
        self._name = name
        self._description = description
        self.max_retries = max_retries
        self.recovery_configs = self._get_recovery_configs()
        self.circuit_breaker_open = False
        self.failure_count = 0
        self.last_failure_time = None
    
    @property
    def name(self) -> str:
        """Unique tool name for LLM function calling."""
        return self._name
    
    @property
    def description(self) -> str:
        """Description for LLM tool selection."""
        return self._description
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters - override in subclasses."""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with comprehensive error handling and fallbacks.
        
        Args:
            parameters: Tool-specific parameters from LLM
            context: Session and conversation context
            
        Returns:
            ToolResult with success status, data, and error handling info
        """
        # Check circuit breaker
        if self.circuit_breaker_open:
            return ToolResult(
                success=False,
                error="CIRCUIT_BREAKER_OPEN",
                fallback_action=FallbackStrategy.GRACEFUL_END.value,
                recovery_message=self._get_circuit_breaker_message(context),
                conversation_context=context
            )
        
        retry_count = context.get("retry_count", 0)
        
        try:
            # Validate parameters
            validation_result = await self._validate_parameters(parameters, context)
            if not validation_result.success:
                return validation_result
            
            # Execute core logic
            result = await self._execute_core(parameters, context)
            
            if result.success:
                self._reset_circuit_breaker()
                return result
            else:
                # Handle execution failure
                return await self._handle_execution_failure(result, context, retry_count)
                
        except Exception as e:
            # Catch unexpected errors
            error_result = ToolResult(
                success=False,
                error=f"UNEXPECTED_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.GRACEFUL_END.value,
                recovery_message=self._get_unexpected_error_message(context),
                retry_count=retry_count,
                conversation_context=context
            )
            await self._log_error(error_result, context)
            self._increment_failure_count()
            return error_result
    
    @abstractmethod
    async def _execute_core(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """Core execution logic - implement in subclasses."""
        pass
    
    async def _validate_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """Validate input parameters."""
        schema = self.parameters_schema
        # Simple validation - enhance with proper JSON schema validation
        if not isinstance(parameters, dict):
            return ToolResult(
                success=False,
                error="INVALID_PARAMETERS_TYPE",
                fallback_action=FallbackStrategy.RETRY.value,
                recovery_message=self._get_validation_message("invalid_type", context),
                conversation_context=context
            )
        
        required = schema.get("required", [])
        for required_param in required:
            if required_param not in parameters:
                return ToolResult(
                    success=False,
                    error=f"MISSING_PARAMETER: {required_param}",
                    fallback_action=FallbackStrategy.SIMPLIFIED.value,
                    recovery_message=self._get_validation_message("missing_param", context, {"param": required_param}),
                    conversation_context=context
                )
        
        return ToolResult(success=True)
    
    async def _handle_execution_failure(self, result: ToolResult, context: Dict[str, Any], retry_count: int) -> ToolResult:
        """Handle tool execution failure with fallback strategies."""
        error_type = result.error
        self._increment_failure_count()
        
        # Check retry limit
        if retry_count >= self.max_retries:
            result.fallback_action = FallbackStrategy.GRACEFUL_END.value
            result.recovery_message = self._get_max_retries_message(context)
            self._open_circuit_breaker()
            await self._log_error(result, context)
            return result
        
        # Try fallback strategies
        fallback_strategies = self.get_fallback_strategies()
        for strategy in fallback_strategies:
            fallback_result = await self._execute_fallback(strategy, result, context)
            if fallback_result.success:
                fallback_result.retry_count = retry_count + 1
                self._reset_circuit_breaker()
                await self._log_recovery(fallback_result, context, strategy)
                return fallback_result
        
        # All fallbacks failed
        final_result = ToolResult(
            success=False,
            error=f"FALLBACKS_EXHAUSTED: {error_type}",
            fallback_action=FallbackStrategy.GRACEFUL_END.value,
            recovery_message=self._get_all_fallbacks_failed_message(context),
            retry_count=retry_count + 1,
            conversation_context=context
        )
        self._open_circuit_breaker()
        await self._log_error(final_result, context)
        return final_result
    
    async def _execute_fallback(self, strategy: FallbackStrategy, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Execute specific fallback strategy."""
        fallback_methods = {
            FallbackStrategy.RETRY: self._fallback_retry,
            FallbackStrategy.SIMPLIFIED: self._fallback_simplified,
            FallbackStrategy.CACHED: self._fallback_cached,
            FallbackStrategy.EMERGENCY: self._fallback_emergency,
            FallbackStrategy.SKIP: self._fallback_skip,
            FallbackStrategy.HUMAN_HANDOFF: self._fallback_human_handoff,
            FallbackStrategy.GRACEFUL_END: self._fallback_graceful_end
        }
        
        fallback_method = fallback_methods.get(strategy)
        if fallback_method:
            return await fallback_method(original_result, context)
        else:
            return ToolResult(
                success=False,
                error="UNKNOWN_FALLBACK_STRATEGY",
                fallback_action=strategy.value,
                recovery_message="I need a moment to think of another way to help you!",
                conversation_context=context
            )
    
    async def _fallback_retry(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Retry the original operation with delay."""
        await asyncio.sleep(1)  # Simple delay
        # Re-execute core logic - in real implementation, this would be more sophisticated
        return await self._execute_core({}, context)
    
    async def _fallback_simplified(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Use simplified version of the operation."""
        # Subclasses should override this for specific simplified logic
        return ToolResult(
            success=True,
            data={"message": "Using simplified approach"},
            recovery_message="Let me try a simpler way to help you!",
            conversation_context=context
        )
    
    async def _fallback_cached(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Use cached data."""
        # Subclasses should implement cache retrieval
        return ToolResult(
            success=True,
            data={"message": "Using cached information"},
            recovery_message="I remember something from before that might help!",
            conversation_context=context
        )
    
    async def _fallback_emergency(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Use emergency/hardcoded fallback."""
        return ToolResult(
            success=True,
            data={"message": "Using emergency fallback"},
            recovery_message="Let me use our special backup plan!",
            conversation_context=context
        )
    
    async def _fallback_skip(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Skip this operation."""
        return ToolResult(
            success=True,
            data={"skipped": True},
            recovery_message="Let's skip that for now and try something else fun!",
            conversation_context=context
        )
    
    async def _fallback_human_handoff(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """Hand off to human intervention."""
        return ToolResult(
            success=False,
            error="HUMAN_HANDOFF_REQUIRED",
            fallback_action=FallbackStrategy.HUMAN_HANDOFF.value,
            recovery_message="I think a real teacher would be perfect for this! Let me get one for you.",
            conversation_context=context
        )
    
    async def _fallback_graceful_end(self, original_result: ToolResult, context: Dict[str, Any]) -> ToolResult:
        """End session gracefully."""
        return ToolResult(
            success=False,
            error="SESSION_END_REQUIRED",
            fallback_action=FallbackStrategy.GRACEFUL_END.value,
            recovery_message="We've had such a wonderful time learning together! Let's say goodbye for now and continue our adventure another day.",
            conversation_context=context
        )
    
    def get_fallback_strategies(self) -> List[str]:
        """Default fallback strategies - override in subclasses."""
        return [
            FallbackStrategy.RETRY.value,
            FallbackStrategy.SIMPLIFIED.value,
            FallbackStrategy.SKIP.value,
            FallbackStrategy.GRACEFUL_END.value
        ]
    
    def _get_recovery_configs(self) -> Dict[str, RecoveryMessageConfig]:
        """Default recovery message configurations - override in subclasses."""
        return {
            "INVALID_PARAMETERS_TYPE": RecoveryMessageConfig(
                error_type="INVALID_PARAMETERS_TYPE",
                primary_message="Hmm, I need a little help understanding that. Could you try saying it a different way?",
                fallback_message="No worries! We can always try something else fun instead.",
                tone="friendly_reminder",
                age_group="6-12",
                emotional_impact="low"
            ),
            "MISSING_PARAMETER": RecoveryMessageConfig(
                error_type="MISSING_PARAMETER",
                primary_message="I think I missed something important! Could you tell me {param} again?",
                fallback_message="That's okay! We can figure it out together step by step.",
                tone="helpful_reminder",
                age_group="6-12",
                emotional_impact="low"
            ),
            "DATABASE_CONNECTION_FAILED": RecoveryMessageConfig(
                error_type="DATABASE_CONNECTION_FAILED",
                primary_message="Our question treasure chest is taking a moment to open! Let me get it ready for you.",
                fallback_message="No problem at all! I have some special backup questions just for you!",
                tone="magical_adventure",
                age_group="6-12",
                emotional_impact="medium"
            ),
            "LLM_EVALUATION_FAILED": RecoveryMessageConfig(
                error_type="LLM_EVALUATION_FAILED",
                primary_message="That's such a wonderful answer! You put so much thought into it. I can tell you're really learning!",
                fallback_message="The most important thing is that you're thinking and trying your best!",
                tone="positive_reinforcement",
                age_group="6-12",
                emotional_impact="low"
            ),
            "MAX_RETRIES_EXCEEDED": RecoveryMessageConfig(
                error_type="MAX_RETRIES_EXCEEDED",
                primary_message="We've tried a few different ways, and I think that's enough for today. You did an amazing job!",
                fallback_message="Every learning adventure has its challenges, and you handled them like a champion!",
                tone="encouraging_closure",
                age_group="6-12",
                emotional_impact="medium"
            )
        }
    
    def get_recovery_message(self, error_type: str, context: Dict[str, Any]) -> str:
        """Generate child-friendly recovery message for specific error."""
        config = self.recovery_configs.get(error_type, self.recovery_configs.get("UNEXPECTED_ERROR", {}))
        message = config.primary_message
        
        # Context substitution
        if context:
            for key, value in context.items():
                if f"{{{key}}}" in message:
                    message = message.format(**{key: value})
        
        # Age-appropriate adjustments
        child_age = context.get("child_age", 9)
        if child_age < 8 and len(message.split()) > 15:
            # Simplify for younger children
            message = self._simplify_message(message)
        
        return message
    
    def _get_validation_message(self, error_subtype: str, context: Dict[str, Any], extra_context: Dict[str, Any] = None) -> str:
        """Get validation-specific recovery message."""
        base_error_type = f"VALIDATION_{error_subtype.upper()}"
        return self.get_recovery_message(base_error_type, {**context, **(extra_context or {})})
    
    def _get_max_retries_message(self, context: Dict[str, Any]) -> str:
        """Message when maximum retries are exceeded."""
        return self.get_recovery_message("MAX_RETRIES_EXCEEDED", context)
    
    def _get_all_fallbacks_failed_message(self, context: Dict[str, Any]) -> str:
        """Message when all fallback strategies fail."""
        return "Wow, we've had quite an adventure today! Sometimes even the best learning tools need a little rest. You were absolutely amazing, and I'm so proud of all your hard work!"
    
    def _get_circuit_breaker_message(self, context: Dict[str, Any]) -> str:
        """Message when circuit breaker is open."""
        return "Our learning tools are taking a quick break to recharge. Don't worry, we'll have even more fun next time we meet!"
    
    def _get_unexpected_error_message(self, context: Dict[str, Any]) -> str:
        """Message for unexpected errors."""
        return "Oops! Something went on a little adventure without me. No worries at all - you're still doing a fantastic job learning!"
    
    def _simplify_message(self, message: str) -> str:
        """Simplify message for younger children."""
        # Simple word replacement for younger kids
        simplifications = {
            "understanding": "hearing",
            "important": "special", 
            "adventure": "fun time",
            "treasure chest": "question box"
        }
        for complex_word, simple_word in simplifications.items():
            message = message.replace(complex_word, simple_word)
        return message[:100]  # Keep short
    
    async def _log_error(self, result: ToolResult, context: Dict[str, Any]) -> None:
        """Log error for monitoring and debugging."""
        # Implementation would integrate with existing logging system
        print(f"TOOL ERROR: {result.error} in {self.name} - Recovery: {result.recovery_message}")
        # In real implementation: logger.error(...), metrics collection
    
    async def _log_recovery(self, result: ToolResult, context: Dict[str, Any], strategy: str) -> None:
        """Log successful recovery."""
        print(f"TOOL RECOVERY: {strategy} successful for {self.name}")
        # In real implementation: logger.info(...), metrics collection
    
    def _increment_failure_count(self) -> None:
        """Increment failure counter and check circuit breaker."""
        self.failure_count += 1
        if self.failure_count >= 5:  # Circuit breaker threshold
            self._open_circuit_breaker()
    
    def _open_circuit_breaker(self) -> None:
        """Open circuit breaker to prevent further calls."""
        self.circuit_breaker_open = True
        # In real implementation: set timeout for auto-reset
    
    def _reset_circuit_breaker(self) -> None:
        """Reset circuit breaker after successful operation."""
        self.circuit_breaker_open = False
        self.failure_count = 0