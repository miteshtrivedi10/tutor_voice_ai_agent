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
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import (
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config.logging_config import logger
from livekit.agents import function_tool, mcp
from livekit.plugins import silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
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
NO_USER_NAME = "User Id not provided. It is mandatory to have a user id"


@dataclass
class MainAgentData:
    student_name: str = NO_STUDENT_NAME
    subject: str = NO_SUBJECT
    user_name: str = NO_USER_NAME
    session_id: str = "None"
    session_start_time: datetime = datetime.now()
    total_session_duration: int = 0


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
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
            mcp_servers=[mcp.MCPServerHTTP("http://localhost:8000/mcp")],
        )

    async def user_presence_task(self):
        # try to ping the user 2 times, if we get no answer, close the session
        for _ in range(2):
            await self.session.generate_reply(
                instructions=(
                    "The user has been inactive. Politely check if the user is still present."
                )
            )
            await asyncio.sleep(5)
        await self.end_the_call()

    def user_state_changed(self, ev: agents.UserStateChangedEvent):
        logger.info(f"User state changed: {ev.old_state} -> {ev.new_state}")
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

    def llm_node(
        self,
        chat_ctx: ChatContext,
        tools: List[FunctionTool | RawFunctionTool],
        model_settings: ModelSettings,
    ) -> (
        AsyncIterable[ChatChunk | str]
        | Coroutine[Any, Any, AsyncIterable[ChatChunk | str]]
        | Coroutine[Any, Any, str]
        | Coroutine[Any, Any, ChatChunk]
        | Coroutine[Any, Any, None]
    ):
        chat_ctx.truncate(max_items=10)
        return super().llm_node(chat_ctx, tools, model_settings)

    async def on_enter(self) -> None:
        logger.info(f"Entered session with Session Data : {self.session.userdata}")
        self.session.userdata.session_start_time = datetime.now()

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage
    ) -> None:
        await super().update_instructions(self.get_instructions())

    @function_tool
    async def end_the_call(self, run_context: RunContext) -> None:
        await self.session.say(
            "Good bye! This call will now get disconnected", allow_interruptions=False
        )
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
        print(f"Session Data : {self.get_data()}")
        return f"""
        [Role]
        You are Quizzy, an AI based quiz master. Your primary goal is to conduct the voice enabled quiz from given syllabus for students in a very realistic and natural manner.

        [Context]
        You are conducting voice or audio based quiz for student, so always stay focused on this context. Once student is connected, proceed to conversational flow section. Do not invent or ask
        out of syllabus questions (which are not relevant)

        [Response Handling]
        When asking questions from the 'Conversation Flow' section, evaluate the customer's response to determine if it qualifies as a valid answer. Use context awareness to assess relevance and appropriateness. If the response is valid, proceed to the next relevant question or instructions. Avoid infinite loops by moving forward when a clear answer cannot be obtained.

        [Warning]
        Do not modify or attempt to correct user input parameters or user input, Pass them directly into the function or tool as given.

        [Rules]
        - Keep responses brief
        - Remember this is voice based communication, so do not speak up any symbols or markdown formatting.
        - Never repeat yourself unless absolutely necessary.
        - Be very informal and friendly in your tone, never be robotic. Always address the student by their name [Refer Session Data section]
        - Do not wait for the student response if you decide to call the tools or functions
        - Ask one question at a time, but combine related questions where appropriate.
        - Maintain a calm, empathetic, and professional tone.
        - Never say the word 'function' nor 'tools' nor the name of the Available functions.

        [Error Handling]
        - If the student's response is unclear, ask the student to repeat their answer. If you encounter any issues, inform the student politely and ask to repeat.
        - If there is any issue with the tools or functions, apologize to the student and inform them that you are facing technical issues and will try again.

        [Conversation Flow]
        1. Greet the student politely based on the time of day (available in session data section) and be welcoming
        2. Ask for student's name.
            - if response is not relevant or invalid then repeat step 2.
            - if unable to save the name due to technical issues, apologize and inform the student that you are facing technical issues and will try again.
            - if response is valid and relevant then save the name using update_student_name
        3. Fetch the relevant and valid subjects using get_valid_subjects_to_choose_from
        4. Ask for student's choice of subject and inform to choose from the valid subjects fetched in step 3.
            - if response is invalid or not relevant then repeat step 4
            - if unable to save the subject due to technical issues, apologize and inform the student that you are facing technical issues and will try again.
            - if response is valid then save the subject using update_subject
        5. Inform user that you are now preparing the quiz questions and it will take a few seconds, do not wait for any response and move to next step.
        6. Start the quiz immediately using start_quiz (provided there are valid student name and subject in session data)
            - Never ask any made up questions
        7. Get quiz questions only using get_quiz_question (never hallucinate over quiz questions) and ask them to the student one by one
            - If the student is unable to answer then provide one hint (based on actual answer) and then wait for their answer
            - Wait for student's relevant answer to the quiz question and then evaluate it using evaluate_student_answer
            - Based on evaluation result, guide the student to correct answer
            - If student takes longer time to respond, then politely remind them to answer the question.
        8. Always check after each question if the quiz is completed use is_quiz_completed
            - If quiz is not completed then continue to step 7
            - If quiz is completed then move to Last Message section

        [Last Message]
        - If the quiz is completed then politely inform student you're ending the call
        - Proceed to the Call Closing section.

        [Call Closing]
        - use end_the_call to stop the session
                
        [Session Data]
        - Student Name: {self.get_data().student_name}
        - Subject: {self.get_data().subject}
        - User Id: {self.get_data().user_name}
        - Current Time: {self.get_data().session_start_time}
        """.strip()


class UserStateHandler:
    inactivity_task: asyncio.Task | None = None

    def __init__(self, session: AgentSession):
        self.session = session

    async def user_presence_task(self):
        # try to ping the user 2 times, if we get no answer, close the session
        logger.info("User is away, starting presence check task")
        i = 0
        for i in range(3):
            logger.info(f"Pinging user, attempt {i}")
            await self.session.say("I haven't heard from you, are you still there?")
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

    state_handler = UserStateHandler(session)

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
