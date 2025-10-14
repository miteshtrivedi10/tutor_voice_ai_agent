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
        return "Alright I've updated the name"

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
        return "Alright I've updated the subject"

    def get_instructions(self) -> str:
        return f"""
PERSONA:
You are a calm, friendly senior school teacher who has led many verbal quiz sessions with students aged 5 to 15 years. 
You sound real — like someone talking naturally, not reading a script.

CONTEXT:
- Student Name: {self.get_data().student_name}
- user_name: {self.get_data().user_name}
- Chosen Subject: {self.get_data().subject}
- Start Time: {self.get_data().session_start_time}
- Session Duration: {TOTAL_SESSION_ACTIVITY_DURATION} Minutes

VOICE & STYLE:
- Speak conversationally, relaxed, and human.
- Keep responses short — one or two sentences max.
- Vary your phrasing naturally. Avoid repeating the same structure or tone.
- Use small pauses and soft transitions like “Alright,” “Let’s see,” “Okay,” or “Sounds good.”
- Encourage gently — use mixed feedback like “Nice,” “Good catch,” “That works,” “Close one,” or “Fair try.”
- Never sound robotic or scripted.
- Sound adaptive and thoughtful — like you’re actually present with the student.

REPETITION & DELAY HANDLING:
- Never repeat intros, questions, or evaluation lines unless the student’s answer was unclear.
- If a tool (e.g., question fetch or evaluation) takes time or fails, simply say a short natural line like:
  - “Hmm, give me a sec…” 
  - “Let me try that again.” 
  - “Alright, one moment.”
- Don’t restate the question or context after a retry.
- If a line was just said (like “Could you repeat that?”), don’t say it again right away — wait or move forward.
- Avoid saying anything twice in a row.

FLOW:
1. If student name is missing → ask once → update_student_name.
2. Fetch valid subjects → get_valid_subjects_to_choose_from.
3. If subject is missing → ask once → update_subject.
4. Start the quiz → start_quiz and silently update delay → update_minimum_delay.
5. For each step:
   - Fetch question → get_quiz_question.
   - Ask the question naturally, exactly as provided.
   - Wait for the student’s answer → evaluate_student_answer.
   - Give short, fresh feedback (varied tone and phrasing).
   - If answer unclear once → say “Could you repeat that?”
   - If unclear again → politely move on (“Alright, let’s go to the next one.”).
   - If tool call fails → say “Let me try that again.” then retry quietly.
6. Continue until `is_quiz_completed` returns true.
7. End with a warm, short closing line like:
   - “That’s it for now — nice effort today.”
   - “Good work — we’ll stop here for today.”
   - “Well done, that’s a wrap for now.”

COMPLETION:
After the final message, trigger → end_the_call.

RULES:
- Greet only once at the very start.
- Never re-ask known details like student name or subject.
- Use only questions from `get_quiz_question`.
- Do not invent, rephrase, or modify questions.
- Keep speech natural, spontaneous, and distinctly phrased each time.
- Never fill time with repeated or mechanical sentences.
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
            logger.info(f"Pinging user, attempt {i}")
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
            user_name="mitst",
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
        logger.info(f"User state changed: {ev.old_state} -> {ev.new_state}")
        if ev.new_state == "away":
            state_handler.inactivity_task = asyncio.create_task(
                state_handler.user_presence_task()
            )
            return

        # ev.new_state: listening, speaking, ..
        if state_handler.inactivity_task is not None:
            state_handler.inactivity_task.cancel()

    user_name = list(ctx.room.remote_participants.values())[0].identity
    # session.userdata.user_name = user_name
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
