import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, AsyncIterable
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
)
from collections.abc import AsyncIterable, Coroutine
from livekit.agents.llm import RawFunctionTool, FunctionTool
from livekit.agents.llm.llm import ChatChunk
import pandas as pd
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.api import DeleteRoomRequest
from livekit.plugins import silero
from livekit.api import LiveKitAPI, DeleteRoomRequest
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    get_job_context,
    JobContext,
    RunContext,
)
from .utils.open_telemtry import configure_opentelemetry
from collections.abc import AsyncIterable, Coroutine
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List
from livekit.agents import function_tool, metrics
from livekit.agents.llm import FunctionTool, RawFunctionTool
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.agents.llm.llm import ChatChunk
from livekit.agents.voice.agent import ModelSettings
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins import (
    silero,
)

from .config.logging_config import logger
from livekit.agents import function_tool, mcp
from livekit.plugins import silero, noise_cancellation
from livekit.api import DeleteRoomRequest
from livekit import agents
from .run_quiz_agent import (
    QuizTaskEngine,
    speech_to_text,
    text_to_speech,
    large_language_model,
)
from .config.logging_config import logger
from .models.agent_dtos import UsageMetrics
from .database.supabase_client import get_db_client

NO_STUDENT_NAME = "Student name not provided. It is mandatory to have a name"
NO_SUBJECT = "Subject not provided. It is mandatory to have a subject"
NO_USER_NAME = ""


TOTAL_SESSION_ACTIVITY_DURATION = 10


@dataclass
class MainAgentData:
    student_name: str = NO_STUDENT_NAME
    subject: str = NO_SUBJECT
    user_name: str = NO_USER_NAME
    session_id: str = "None"
    session_start_time: datetime = datetime.now()
    total_session_duration: int = 0
    current_state: str = "GREETINGS"


# ---------- AGENT ----------
class TutorVoiceAgent(Agent):
    metrics_keeper: metrics.UsageCollector
    job_context: JobContext

    def get_data(self) -> MainAgentData:
        if not hasattr(self, "session") or not hasattr(self.session, "userdata"):
            logger.warning(
                "Session or userdata not found, returning default MainAgentData"
            )
            return MainAgentData()
        return self.session.userdata

    def __init__(self, ctx, stt, tts, llm):
        self.metrics_keeper = metrics.UsageCollector()
        super().__init__(
            instructions=self.get_instructions(),
            allow_interruptions=True,
            stt=stt,
            tts=tts,
            llm=llm,
            max_endpointing_delay=5,
            vad=silero.VAD.load(),
            turn_detection=EnglishModel(),
            mcp_servers=[mcp.MCPServerHTTP("http://localhost:8000/mcp")],
        )

    async def user_presence_task(self):
        # try to ping the user 2 times, if we get no answer, close the session
        for _ in range(2):
            await self.session.generate_reply(
                instructions=(
                    "The user has been inactive. Politely check if the user is still present and don't repeat same sentences"
                )
            )
            await asyncio.sleep(5)
        await self.end_the_call()

    def user_state_changed(self, ev: agents.UserStateChangedEvent):
        if ev.new_state == "away":
            self.inactivity_task = asyncio.create_task(self.user_presence_task())
            return

        # ev.new_state: listening, speaking, ..
        if self.inactivity_task is not None:
            self.inactivity_task.cancel()

    async def on_exit(self) -> None:
        self.session.userdata.total_session_duration = int(
            (datetime.now() - self.session.userdata.session_start_time).total_seconds()
        )
        logger.info(
            f"Total seconds generated : {self.session.userdata.total_session_duration}"
        )

    # def llm_node(
    #     self,
    #     chat_ctx: ChatContext,
    #     tools: List[FunctionTool | RawFunctionTool],
    #     model_settings: ModelSettings,
    # ) -> (
    #     AsyncIterable[ChatChunk | str]
    #     | Coroutine[Any, Any, AsyncIterable[ChatChunk | str]]
    #     | Coroutine[Any, Any, str]
    #     | Coroutine[Any, Any, ChatChunk]
    #     | Coroutine[Any, Any, None]
    # ):
    #     chat_ctx.truncate(max_items=10)
    #     return super().llm_node(chat_ctx, tools, model_settings)

    async def on_enter(self) -> None:
        logger.info(f"Entered session with Session Data : {self.session.userdata}")
        self.session.userdata.session_start_time = datetime.now()

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage
    ) -> None:
        await super().update_instructions(self.get_instructions())

    @function_tool
    async def update_minimum_delay(self, run_context: RunContext) -> None:
        logger.info("Updating the minimum delay since quiz is started")
        self.session.current_agent._min_endpointing_delay = 2

    @function_tool
    async def end_the_call(self, run_context: RunContext) -> None:
        await self.session.say(
            "Good bye! This call will now get disconnected", allow_interruptions=False
        )
        await asyncio.sleep(3)
        job_ctx = get_job_context()
        job_ctx.shutdown()
        await job_ctx.api.room.delete_room(DeleteRoomRequest(room=job_ctx.room.name))

    @function_tool
    async def update_student_name(
        self,
        run_context: RunContext,
        student_name: str,
    ) -> str:
        """
        Updates the student's name in the current session's user data.
        Args:
            context (RunContext): The current execution context.
            student_name (str): Student's name to be updated.
        Returns:
            str
        """
        # if student_name is None or student_name.lower() == "student":
        logger.info(
            f"Updating student name to: {student_name} : currently : {self.session.userdata.student_name}"
        )
        self.session.userdata.student_name = student_name
        return f"Student name set to {student_name}"

    @function_tool
    async def update_subject(
        self,
        run_context: RunContext,
        subject: str,
    ) -> str:
        """
        Updates the subject for the current student session.
        Args:
            subject (str): Student's chosen subject.
        Returns:
            str
        """
        logger.info(
            f"Updating subject to: {subject} : currently : {self.session.userdata.subject}"
        )
        self.session.userdata.subject = subject
        return f"Subject set to {subject}"

    def get_instructions(self) -> str:
        return f"""
You are Quizzy voice-based educator and quiz mentor guiding a student through an interactive learning session.
Your responsibility is to maintain a natural, human-sounding educational flow that moves smoothly from
understanding to questioning, from answering to feedback — all through tool usage.

CONTEXT:
- Student Name: {self.get_data().student_name}
- User Name: {self.get_data().user_name}
- Chosen Subject: {self.get_data().subject}
- Session Start Time: {self.get_data().session_start_time}
- Total Session Duration: {TOTAL_SESSION_ACTIVITY_DURATION} minutes

---------------------------------------------------------------------
ROLE DEFINITION:
You are a mentor-like teacher — confident, encouraging, and perceptive.
You lead each session with discipline and warmth, always adapting to the student’s intent and progress.

---------------------------------------------------------------------
CORE PRINCIPLES:

1. INTENT & CONTEXT AWARENESS:
   - Always interpret the full meaning of each response: words, tone, and implied readiness.
   - Detect when the student has already confirmed understanding or readiness — avoid repeating confirmations.
   - Before generating any response, consider what was already said and done in the current session context.

2. CONVERSATIONAL FLOW:
   - Every message should build naturally from the last student turn.
   - Never restate the same instruction, feedback, or question unless the student explicitly asks for repetition or clarification.
   - Ensure each response adds *new* meaning or action to the conversation.

3. FEEDBACK LOGIC:
   - Provide exactly one concise and relevant feedback message per student answer.
   - Do not give additional or repeated feedback after the evaluation has been completed.
   - Feedback must be precise: highlight what was right or wrong, then immediately transition forward.

4. TOOL-BASED REASONING:
   - Do not rely on external or internet knowledge.
   - For each decision (quiz creation, delivery, evaluation, pacing, or explanation),
     select and call the correct tool based on detected intent and current conversation state.
   - Always reason through tool selection — never hardcode steps.
   - Example tools may include: quiz_generation, question_delivery, answer_evaluation,
     feedback_analysis, pacing_adjustment, delay_control, context_memory.

5. TIMING AND FLOW CONTROL:
   - Adjust pacing dynamically — use pause, encouragement, or transition naturally.

6. SESSION MEMORY & STATE TRACKING:
   - Keep awareness of conversation state: what has been asked, answered, or fed back upon.
   - Do not repeat previous feedback or questions unless the student requests review or seems confused.
   - Use session context and state awareness to avoid redundancy.

7. TONE AND STYLE:
   - Speak with authority and empathy — a mentor who expects focus but keeps the student comfortable.
   - Use varied phrasing and sentence structures; never robotic or repetitive.
   - Encourage effort, acknowledge understanding, and correct with clarity.

8. EDUCATIONAL DYNAMICS:
   - When readiness is detected → begin or continue the quiz.
   - When an answer is received → evaluate once, give concise feedback, and move to the next logical step.
   - When confusion is sensed → clarify briefly before resuming the flow.

9. SESSION AWARENESS:
   - Maintain continuity: know what stage the session is in and what comes next.
   - Use information (subject, duration, previous interactions) to personalize the experience.

---------------------------------------------------------------------
OPERATIONAL OBJECTIVE:
Your purpose is to:
- Identify the student’s intent and emotional readiness from their voice and phrasing.
- Select and call the appropriate tool dynamically.
- Maintain forward-moving, non-repetitive dialogue.
- Provide one clear feedback per answer and move forward naturally.

---------------------------------------------------------------------
SUMMARY:
You are a conversational quiz mentor who senses intent, maintains flow, and controls repetition intelligently.
Each turn is contextually aware, feedback-efficient, and guided entirely by dynamic tool use.
You never sound mechanical or redundant — you sound like a real educator guiding learning with purpose.

""".strip()


class UserStateHandler:
    inactivity_task: asyncio.Task | None = None

    def __init__(self, session: AgentSession, job_ctx: JobContext):
        self.session = session
        self.job_ctx = job_ctx
        asyncio.create_task(self.close_room_after_timeout())  # 10 Minutes

    async def close_room_after_timeout(self):
        await asyncio.sleep(
            TOTAL_SESSION_ACTIVITY_DURATION * 60
        )  # wait for the timeout period
        await self.session.say(
            "This session has timed out and we're sorry to disconnect"
        )
        await asyncio.sleep(3)
        self.job_ctx.shutdown()
        await self.job_ctx.api.room.delete_room(
            DeleteRoomRequest(room=self.job_ctx.room.name)
        )

    async def user_presence_task(self):
        # try to ping the user 2 times, if we get no answer, close the session
        logger.info("User is away, starting presence check task")
        i = 0
        for i in range(3):
            await self.session.generate_reply(
                instructions="The user has been inactive. Politely check if the user is still present and don't repeat same sentences"
            )
            await asyncio.sleep(5)
            i = i + 1

        if i >= 3:
            await self.session.aclose()


async def log_usage(
    session_id: str,
    user_name: str,
    total_session_duration: int,
    usage_collector: metrics.UsageCollector,
) -> None:
    summary = usage_collector.get_summary()
    metrics = UsageMetrics(
        session_id=session_id,
        user_name=user_name,
        mt_total_session_duration=total_session_duration,
        mt_llm_completiontokens=summary.llm_completion_tokens,
        mt_llm_prompttokens=summary.llm_prompt_tokens,
        mt_llm_promptcachetokens=summary.llm_prompt_cached_tokens,
        mt_stt_audioduration=summary.stt_audio_duration,
        mt_tts_audioduration=summary.tts_audio_duration,
        mt_tts_characterscount=summary.tts_characters_count,
    )
    if get_db_client().update_usage_metrics_in_db(metrics):
        logger.info(f"Usage Metrics Stored for user : {user_name}")
        return

    logger.error(f"Unable to store metrics for user : {user_name}")


# ---------- ENTRYPOINT ----------
async def agent_entrypoint(ctx: JobContext):
    configure_opentelemetry()
    usage_collector = metrics.UsageCollector()

    logger.info(f"AGENT STARTING WITH ROOM : {ctx.room.name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    session = AgentSession(
        userdata=MainAgentData(
            session_id=ctx.job.id,
            total_session_duration=0,
            # user_name="mitst",
            session_start_time=datetime.now(),
        ),
        user_away_timeout=10,
        max_tool_steps=10,
    )

    state_handler = UserStateHandler(session, ctx)

    @session.on("metrics_collected")
    def _on_metrics_collected(event: agents.MetricsCollectedEvent):
        usage_collector.collect(event.metrics)

    @session.on("conversation_item_added")
    def _on_conversation_item_added(event: agents.ConversationItemAddedEvent):
        if event is None or event.item is None:
            return
        message = f"{event.item.role}: {event.item.content.pop()}"
        asyncio.create_task(
            get_job_context().agent.send_text(message, topic=f"{user_name}.chat")
        )
        logger.info(f"{message}")

    await session.start(
        agent=TutorVoiceAgent(
            ctx=ctx,
            stt=speech_to_text,
            tts=text_to_speech,
            llm=large_language_model,
        ),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            close_on_disconnect=True,
            video_enabled=False,
            pre_connect_audio=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    @session.on("user_state_changed")
    def _on_user_state_changed(ev: agents.UserStateChangedEvent):
        if ev.new_state == "away":
            state_handler.inactivity_task = asyncio.create_task(
                state_handler.user_presence_task()
            )
            return

        # ev.new_state: listening, speaking, ..
        if state_handler.inactivity_task is not None:
            state_handler.inactivity_task.cancel()

    user_name = list(ctx.room.remote_participants.values())[0].identity
    session.userdata.user_name = user_name
    ctx.add_shutdown_callback(
        lambda: log_usage(
            session_id=ctx.job.id,
            user_name=user_name,
            total_session_duration=session.userdata.total_session_duration,
            usage_collector=usage_collector,
        )
    )


if __name__ == "__main__":
    from livekit import agents

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=agent_entrypoint))
