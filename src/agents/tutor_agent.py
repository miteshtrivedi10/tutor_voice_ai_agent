"""
Updated tutor agent entrypoint using the new single VoiceTutorAgent.
Removes all stepwise task dependencies and implements the prompt-driven architecture.
"""

import asyncio
from typing import Any
from livekit.agents import AgentSession, JobContext, RoomInputOptions, AutoSubscribe
from livekit.plugins import silero

from src.utils.open_telemtry import configure_opentelemetry
from src.config.logging_config import logger
from src.agents.single_agent import (
    agent_entrypoint as create_voice_tutor_agent_entrypoint,
)
from src.services.usage_service import UsageService
from src.models.agent_dtos import MainAgentData


async def agent_entrypoint(ctx: JobContext):
    """
    Main entrypoint for the refactored VoiceTutorAgent.
    Orchestrates the single prompt-driven agent with tool calling.
    """
    configure_opentelemetry()

    logger.info(
        f"TUTOR AGENT STARTING WITH ROOM: {ctx.room.name} (Session ID: {ctx.job.id})"
    )

    # Connect to room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create initial session data
    initial_session_data = MainAgentData(
        session_id=ctx.job.id,
        student_name="Student name is Missing. Required",
        subject="Subject is Missing. Required",
        user_name="User name is Missing. Required",
    )

    # Create and start agent session using new architecture
    session = AgentSession(userdata=initial_session_data)

    # Use the new single agent entrypoint
    await create_voice_tutor_agent_entrypoint(ctx)

    # Set up event handlers for the session
    @session.on("metrics_collected")
    def _on_metrics_collected(event):
        """Handle metrics collection for usage tracking."""
        if hasattr(event, "summary") and event.summary:
            asyncio.create_task(
                log_usage(
                    ctx.job.id,
                    (
                        initial_session_data.student_name
                        if initial_session_data.student_name
                        != "Student name is Missing. Required"
                        else "Unknown"
                    ),
                    event.summary,
                )
            )
            logger.info("Metrics collected and logged for new architecture")

    @session.on("conversation_item_added")
    def _on_conversation_item_added(event):
        """Handle conversation logging for the new tool-based flow."""
        if event is None or event.item is None:
            return

        try:
            message_content = (
                event.item.content[0] if event.item.content else "No content"
            )
            message = f"{event.item.role}: {message_content}"

            # Send to chat topic for monitoring
            asyncio.create_task(ctx.agent.send_text(message, topic="chat"))

            logger.debug(f"New architecture conversation: {message}")

        except Exception as e:
            logger.error(f"Error handling conversation item: {str(e)}")

    # Start the voice session with the new agent architecture
    await session.start(
        agent=None,  # Agent logic handled by single_agent.py entrypoint
        room=ctx.room,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            close_on_disconnect=True,
            video_enabled=False,
            pre_connect_audio=True,
        ),
    )

    logger.info(
        f"VoiceTutorAgent session started successfully with new architecture for {ctx.job.id}"
    )


async def log_usage(session_id: str, user_name: str, usage_collector: Any) -> None:
    """
    Log usage metrics for the new tool-based architecture.
    Compatible with existing UsageService.
    """
    try:
        if not usage_collector or not hasattr(usage_collector, "get_summary"):
            logger.warning("No usage collector summary available")
            return

        summary = usage_collector.get_summary()

        # Create metrics object (assuming existing UsageMetrics structure)
        metrics_data = {
            "session_id": session_id,
            "user_name": user_name,
            "mt_llm_completiontokens": getattr(summary, "llm_completion_tokens", 0),
            "mt_llm_prompttokens": getattr(summary, "llm_prompt_tokens", 0),
            "mt_llm_promptcachetokens": getattr(summary, "llm_prompt_cached_tokens", 0),
            "mt_stt_audioduration": getattr(summary, "stt_audio_duration", 0),
            "mt_tts_audioduration": getattr(summary, "tts_audio_duration", 0),
            "mt_tts_characterscount": getattr(summary, "tts_characters_count", 0),
            "architecture_version": "tool_based_v1",  # Track new architecture
            "session_timestamp": datetime.now().isoformat(),
        }

        # Use existing UsageService
        usage_service = UsageService()
        if usage_service.update_usage_metrics_in_db(metrics_data):
            logger.info(
                f"Usage metrics stored for user {user_name} with new architecture"
            )
        else:
            logger.error(f"Failed to store usage metrics for user {user_name}")

    except Exception as e:
        logger.error(f"Error logging usage for session {session_id}: {str(e)}")


# Legacy compatibility - will be removed after full migration
async def legacy_agent_entrypoint(ctx: JobContext):
    """
    Legacy entrypoint - REMOVE AFTER FULL MIGRATION TO NEW ARCHITECTURE.
    This maintains compatibility during transition phase.
    """
    logger.warning(
        "Using legacy agent entrypoint - please migrate to new tool-based architecture"
    )

    # Import legacy task system (to be removed)
    from src.agents.tasks.greeting_task import GreetingTask
    from src.agents.base_agent import BaseVoiceAgent
    from src.voice.voice_processing import (
        speech_to_text,
        text_to_speech,
        large_language_model,
    )

    # Legacy initialization (DEPRECATED)
    initial_agent = BaseVoiceAgent(
        ctx=ctx,
        stt=speech_to_text,
        tts=text_to_speech,
        llm=large_language_model,
        instructions="Legacy instructions - migrate to new system.",
        allow_interruptions=True,
    )

    greeting_task = GreetingTask(ctx, initial_agent)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    session = AgentSession(userdata=MainAgentData(session_id=ctx.job.id))

    await session.start(
        agent=greeting_task,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            close_on_disconnect=True,
            video_enabled=False,
            pre_connect_audio=True,
        ),
    )

    logger.info(f"Legacy agent started for {ctx.job.id} - MIGRATE TO NEW ARCHITECTURE")
