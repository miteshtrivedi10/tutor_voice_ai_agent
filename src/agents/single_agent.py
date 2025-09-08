"""
VoiceTutorAgent: Single, prompt-driven agent replacing stepwise task system.
Implements comprehensive tool calling with error handling and child-friendly conversation flow.
Follows SOLID principles with dependency injection and single responsibility.
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

from livekit.agents import AgentSession, JobContext, AutoSubscribe
from livekit.agents.llm import ChatContext
from livekit.plugins import silero

from src.agents.interfaces import ITool, IToolRegistry, ISessionManager
from src.agents.tools.update_student_info_tool import UpdateStudentInfoTool
from src.agents.tools.start_quiz_tool import StartQuizTool
from src.agents.tools.get_next_question_tool import GetNextQuestionTool
from src.agents.tools.end_quiz_tool import EndQuizTool
from src.agents.tools.evaluate_answer_tool import EvaluateAnswerTool
from src.services.session_manager import get_session_manager
from src.services.tool_registry import ToolRegistry
from src.services.llm_service import LLMService
from src.config.logging_config import logger
from src.utils.open_telemtry import configure_opentelemetry
from src.config.settings import AppSettings as Settings


class VoiceTutorAgent:
    """
    Single responsibility: Orchestrate prompt-driven conversation using tools.
    Dependencies injected via constructor following Dependency Inversion Principle.
    """

    def __init__(
        self,
        ctx: JobContext,
        session_manager: ISessionManager,
        tool_registry: IToolRegistry,
        llm_service: LLMService,
        voice_config: Dict[str, Any],
    ):
        self.ctx = ctx
        self.session_manager = session_manager or get_session_manager()
        self.tool_registry = tool_registry or ToolRegistry()
        self.llm_service = llm_service or LLMService(model=Settings.LLM_MODEL_NAME)
        self.voice_config = voice_config or {
            "stt": "speech_to_text",  # From voice_processing
            "tts": "text_to_speech",
            "interruptions": True,
        }
        self.session_id = ctx.job.id
        self.session = None  # Set during initialization
        self.conversation_history = []

        # Initialize tools following Open/Closed Principle
        self._initialize_tools()

        # Comprehensive system prompt
        self.system_prompt = self._build_system_prompt()

        configure_opentelemetry()
        logger.info(f"VoiceTutorAgent initialized for session: {self.session_id}")

    def _initialize_tools(self) -> None:
        """Register all available tools with the registry."""
        tools = [
            UpdateStudentInfoTool(self.session_manager),
            StartQuizTool(self.session_manager),
            GetNextQuestionTool(self.session_manager),
            EvaluateAnswerTool(self.session_manager),
            EndQuizTool(self.session_manager),
        ]

        for tool in tools:
            self.tool_registry.register_tool(tool)

        logger.info(f"Registered {len(tools)} tools for session {self.session_id}")

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with tool information."""
        available_tools_info = self.tool_registry.get_available_tools()

        prompt = f"""
You are Quizzy, a friendly and encouraging voice tutor for children ages 6-12. 
Your role is to guide students through an educational quiz experience using the provided tools.

IMPORTANT CONVERSATION FLOW GUIDELINES:
1. Start by warmly greeting and using update_student_info tool to collect name/subject
2. Once student information is collected, use start_quiz tool to begin quiz session
3. Use get_next_question tool to present questions one by one  
4. After each student response, use evaluate_answer tool to score and provide feedback
5. When quiz is complete (all questions answered), use end_quiz tool for summary
6. Always use tools for ALL actions - never handle data directly in conversation
7. Maintain natural, engaging conversation while following the tool-based flow

CHILD-FRIENDLY COMMUNICATION RULES:
- Use simple, age-appropriate language (6-12 years old)
- Always be encouraging and positive - focus on effort, not just correctness
- Never reveal answers directly or give hints unless specifically requested
- Frame technical issues as normal/adventurous parts of learning
- Personify tools and technology (e.g., "Our question friends are getting ready!")
- End every interaction with encouragement and forward-looking statement

ERROR HANDLING GUIDELINES (Never mention to child):
- If tools fail, use provided recovery messages from tool responses
- Stay calm and encouraging - technical issues should never break immersion
- Use fallback strategies but maintain learning experience
- Log errors internally but keep conversation natural and positive

AVAILABLE TOOLS:
{json.dumps(available_tools_info, indent=2)}

CURRENT SESSION CONTEXT:
- Session ID: {self.session_id}
- Model: {self.llm_service.model_name}
- Voice Mode: Always use plain English, no symbols or formatting

CONVERSATION PRINCIPLES:
1. Be patient and understanding - children learn at different paces
2. Celebrate effort and curiosity more than perfect answers
3. Use questions to encourage thinking rather than just providing answers
4. Maintain consistent, warm, teacher-like tone throughout
5. Adapt complexity based on child's estimated age from session data

When responding:
- Base your response on tool results and conversation context
- Use the recovery_message from tools when tools encounter issues
- Always advance the conversation toward educational goals
- End responses naturally, ready for student input

Remember: Your success is measured by the child's engagement and learning experience, not perfect technical execution!
"""

        return prompt

    async def initialize_session(self, session: AgentSession) -> None:
        """Initialize the agent session with event handlers."""
        self.session = session

        # Set up event handlers
        @session.on("metrics_collected")
        def _on_metrics_collected(event):
            logger.info(f"Metrics collected for session {self.session_id}")
            # Integrate with usage service if needed

        @session.on("conversation_item_added")
        async def _on_conversation_item_added(event):
            if event is None or event.item is None:
                return

            message = f"{event.item.role}: {event.item.content.pop() if event.item.content else 'No content'}"
            asyncio.create_task(self.ctx.agent.send_text(message, topic="chat"))
            logger.debug(f"Conversation item added: {message}")

            # Save to conversation history
            await self._save_conversation_turn(
                "assistant" if "assistant" in message.lower() else "user", message
            )

        # Set initial userdata
        initial_data = await self.session_manager.get_session_data(self.session_id)
        session.userdata = initial_data

        logger.info(f"Session initialized for {self.session_id}")

    async def process_user_input(
        self, user_input: str, chat_context: ChatContext = None
    ) -> Dict[str, Any]:
        """
        Process user input through the tool-calling pipeline.

        Args:
            user_input: Raw user input from voice/text
            chat_context: Current chat context

        Returns:
            Response data including generated text and tool calls
        """
        try:
            logger.debug(
                f"Processing user input for session {self.session_id}: {user_input[:50]}..."
            )

            # Get current session context
            session_data = await self.session_manager.get_session_data(self.session_id)

            # Prepare conversation context for LLM
            conversation_context = {
                "session_id": self.session_id,
                "student_name": session_data.get("student_name", "Student"),
                "subject": session_data.get("subject", "General"),
                "session_status": session_data.get("session_status", "initializing"),
                "child_age": session_data.get("child_age", 9),
                "quiz_progress": {
                    "current_question": session_data.get("current_question_index", 0),
                    "total_questions": session_data.get("total_questions", 0),
                    "score": session_data.get("score", 0),
                },
                "timestamp": datetime.now().isoformat(),
                "retry_count": chat_context.retry_count if chat_context else 0,
            }

            # Get recent conversation history
            history = await self.session_manager.get_conversation_history(
                self.session_id, limit=10
            )

            # Call LLM with tools
            llm_response = await self.llm_service.generate_with_tools(
                system_prompt=self.system_prompt,
                user_input=user_input,
                conversation_history=history,
                available_tools=self.tool_registry.get_available_tools(),
                context=conversation_context,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=500,
                temperature=0.7,  # Balanced creativity for educational content
            )

            if not llm_response:
                # LLM call failed
                fallback_response = await self._generate_fallback_response(
                    user_input, conversation_context
                )
                await self._save_conversation_turn("user", user_input)
                await self._save_conversation_turn(
                    "assistant", fallback_response["content"]
                )
                return fallback_response

            # Handle tool calls
            response_data = {
                "generated_text": llm_response.get("content", ""),
                "tool_calls": llm_response.get("tool_calls", []),
                "session_context": conversation_context,
                "llm_confidence": llm_response.get("confidence", 0.5),
            }

            # Execute tool calls if present
            if response_data["tool_calls"]:
                tool_results = await self._execute_tool_calls(
                    response_data["tool_calls"], conversation_context
                )
                response_data["tool_results"] = tool_results

                # Generate final response incorporating tool results
                final_response = await self._generate_final_response(
                    user_input, tool_results, conversation_context
                )
                response_data["final_response"] = final_response
                await self._save_conversation_turn("assistant", final_response)
            else:
                await self._save_conversation_turn(
                    "assistant", response_data["generated_text"]
                )

            # Update session state based on conversation progress
            await self._update_session_state(conversation_context, response_data)

            logger.info(f"Successfully processed input for session {self.session_id}")
            return response_data

        except Exception as e:
            logger.error(
                f"Error processing user input for session {self.session_id}: {str(e)}"
            )

            # Generate emergency fallback response
            fallback_response = await self._generate_emergency_fallback(
                user_input, conversation_context
            )
            await self._save_conversation_turn("user", user_input)
            await self._save_conversation_turn(
                "assistant", fallback_response["content"]
            )

            return {
                "error": str(e),
                "fallback_used": True,
                "generated_text": fallback_response["content"],
                "tool_calls": [],
                "session_context": conversation_context,
            }

    async def _execute_tool_calls(
        self, tool_calls: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute multiple tool calls and return results."""
        tool_results = []

        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                if not tool_name:
                    tool_results.append(
                        {
                            "tool_name": "unknown",
                            "success": False,
                            "error": "MISSING_TOOL_NAME",
                            "recovery_message": "I tried to use a special learning tool but couldn't find its name! Let me try a different approach.",
                            "data": None,
                        }
                    )
                    continue

                # Get tool from registry
                tool = self.tool_registry.get_tool_by_name(tool_name)
                if not tool:
                    tool_results.append(
                        {
                            "tool_name": tool_name,
                            "success": False,
                            "error": "TOOL_NOT_FOUND",
                            "recovery_message": f"I couldn't find my {tool_name} helper right now! Let me use a different learning approach instead.",
                            "data": None,
                        }
                    )
                    continue

                # Execute tool
                tool_result = await tool.execute(tool_args, context)

                tool_results.append(
                    {
                        "tool_name": tool_name,
                        "success": tool_result.success,
                        "data": tool_result.data,
                        "recovery_message": tool_result.recovery_message,
                        "error": tool_result.error,
                        "fallback_action": tool_result.fallback_action,
                    }
                )

                logger.debug(
                    f"Tool {tool_name} executed: {'success' if tool_result.success else 'failed'}"
                )

            except Exception as e:
                logger.error(
                    f"Error executing tool {tool_call.get('name', 'unknown')}: {str(e)}"
                )
                tool_results.append(
                    {
                        "tool_name": tool_call.get("name", "unknown"),
                        "success": False,
                        "error": f"TOOL_EXECUTION_ERROR: {str(e)}",
                        "recovery_message": "My learning tool had a little hiccup! Don't worry, I'm using a backup plan to keep our learning adventure going smoothly!",
                        "data": None,
                    }
                )

        return tool_results

    async def _generate_final_response(
        self,
        user_input: str,
        tool_results: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        """Generate final response incorporating tool results."""
        try:
            # Analyze tool results for conversation guidance
            successful_tools = [r for r in tool_results if r["success"]]
            failed_tools = [r for r in tool_results if not r["success"]]

            # Build context for final response generation
            tool_context = {
                "successful_operations": len(successful_tools),
                "failed_operations": len(failed_tools),
                "conversation_stage": context.get("session_status", "initial"),
                "student_progress": context.get("quiz_progress", {}),
                "recovery_messages": [r["recovery_message"] for r in failed_tools],
                "tool_data_summary": {
                    r["tool_name"]: r["data"] for r in successful_tools
                },
            }

            # Generate final response using LLM with tool context
            final_prompt = f"""
Based on the tool execution results, generate a natural, child-friendly response.

USER INPUT: {user_input}

TOOL RESULTS SUMMARY:
{successful_tools}

RECOVERY MESSAGES FOR FAILED TOOLS:
{tool_context['recovery_messages']}

CURRENT CONTEXT:
{tool_context}

CONVERSATION GUIDELINES:
- Incorporate successful tool results naturally
- Use recovery messages for failed tools without technical jargon
- Maintain educational flow and encouragement
- Advance conversation toward learning goals
- Keep responses under 100 words for voice delivery

Generate a single, cohesive response that:
1. Acknowledges the user's input
2. Incorporates relevant tool results 
3. Provides appropriate feedback or next steps
4. Ends with encouragement and question to continue conversation

RESPONSE:
"""

            final_response = await self.llm_service.generate_response(
                prompt=final_prompt,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=150,
                temperature=0.7,
            )

            if final_response:
                return final_response
            else:
                # Fallback to simple acknowledgment
                return f"That's a great response! {' '.join([r['recovery_message'] for r in failed_tools[:1]])} What would you like to explore next in our learning adventure?"

        except Exception as e:
            logger.error(f"Error generating final response: {str(e)}")
            return "I love learning with you! Let me think for a moment... What would you like to explore next in our educational adventure?"

    async def _generate_fallback_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback response when LLM call fails."""
        student_name = context.get("student_name", "young learner")
        session_status = context.get("session_status", "initial")

        fallback_responses = {
            "initial": f"Hello {student_name}! I'm so excited to learn with you today! What's your name and what would you like to learn about - Science, English, or Geography?",
            "collecting": f"That's wonderful, {student_name}! I think I need a little help understanding. Could you tell me your name and favorite subject one more time? I'd love to get to know you better!",
            "quiz": f"Great thinking, {student_name}! Let me make sure I understood your answer correctly. Could you tell me a bit more about what you think? Your ideas are always so interesting!",
            "completed": f"You've been such an amazing learning partner today, {student_name}! We had such a wonderful educational adventure together. I can't wait to learn more with you next time!",
        }

        response = fallback_responses.get(session_status, fallback_responses["initial"])

        return {
            "generated_text": response,
            "tool_calls": [],
            "fallback_used": True,
            "session_context": context,
        }

    async def _generate_emergency_fallback(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate emergency fallback for critical failures."""
        return {
            "generated_text": "Wow, what an interesting thing you said! I love learning with you! Tell me more about what you're thinking!",
            "tool_calls": [],
            "emergency_fallback": True,
            "session_context": context,
        }

    async def _save_conversation_turn(self, role: str, content: str) -> None:
        """Save conversation turn to session history."""
        try:
            await self.session_manager.save_conversation_turn(
                self.session_id, role, content
            )
        except Exception as e:
            logger.error(f"Failed to save conversation turn: {str(e)}")

    async def _update_session_state(
        self, context: Dict[str, Any], response_data: Dict[str, Any]
    ) -> None:
        """Update session state based on conversation progress."""
        try:
            # Determine new session state based on tools used and context
            session_status = context.get("session_status", "initial")

            if "quiz_started" in str(response_data):
                new_status = "quiz_active"
            elif "student_info_collected" in str(response_data):
                new_status = "collecting_complete"
            elif "quiz_completed" in str(response_data):
                new_status = "quiz_completed"
            else:
                new_status = session_status

            # Update last interaction time and conversation metadata
            update_data = {
                "last_interaction_time": datetime.now().isoformat(),
                "session_status": new_status,
                "interaction_count": context.get("interaction_count", 0) + 1,
                "last_tool_calls": [
                    tc.get("name", "unknown")
                    for tc in response_data.get("tool_calls", [])
                ],
            }

            await self.session_manager.update_session_data(self.session_id, update_data)

        except Exception as e:
            logger.error(f"Error updating session state: {str(e)}")

    async def end_session(self, reason: str = "normal_completion") -> Dict[str, Any]:
        """Gracefully end the session."""
        try:
            # Final session cleanup
            final_stats = await self.session_manager.get_session_statistics(
                self.session_id
            )

            # Log final metrics
            logger.info(
                f"Session ended for {self.session_id}: {reason}, stats: {final_stats}"
            )

            # Save final conversation turn
            await self._save_conversation_turn("system", f"Sessions ended: {reason}")

            # Clean up cache
            if self.session_id in self.session_cache:
                del self.session_cache[self.session_id]

            return {
                "status": "session_ended",
                "reason": reason,
                "final_statistics": final_stats,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error ending session {self.session_id}: {str(e)}")
            return {
                "status": "session_ended_with_error",
                "reason": reason,
                "error": str(e),
                "success": False,
            }


async def create_voice_tutor_agent(ctx: JobContext) -> VoiceTutorAgent:
    """Factory function to create VoiceTutorAgent with dependency injection."""
    session_manager = get_session_manager()
    tool_registry = ToolRegistry()
    llm_service = LLMService(model="meta-llama/llama-3.1-8b-instruct:free")

    return VoiceTutorAgent(
        ctx=ctx,
        session_manager=session_manager,
        tool_registry=tool_registry,
        llm_service=llm_service,
    )


async def agent_entrypoint(ctx: JobContext):
    """Main entrypoint for the voice tutor agent."""
    logger.info(f"Starting VoiceTutorAgent for room: {ctx.room.name}")

    # Create agent
    agent = await create_voice_tutor_agent(ctx)

    # Connect and start session
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create session
    session = AgentSession(
        userdata=await agent.session_manager.get_session_data(ctx.job.id)
    )

    # Initialize agent session
    await agent.initialize_session(session)

    # Start voice pipeline
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options={
            "audio_enabled": True,
            "close_on_disconnect": True,
            "video_enabled": False,
            "pre_connect_audio": True,
        },
    )

    logger.info(f"VoiceTutorAgent started successfully for session: {ctx.job.id}")

    # Keep session running
    try:
        await asyncio.Event().wait()  # Keep alive until interrupted
    except asyncio.CancelledError:
        await agent.end_session("session_interrupted")
        logger.info(f"VoiceTutorAgent session ended for {ctx.job.id}")
