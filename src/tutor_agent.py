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
)
from src.utils.open_telemtry import configure_opentelemetry
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

from src.config.logging_config import logger
from livekit.agents import function_tool
from livekit.plugins import silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.api import DeleteRoomRequest
from livekit import agents

from src.run_quiz_agent import (
    QuizTaskEngine,
    speech_to_text,
    text_to_speech,
    large_language_model,
)
from src.config.logging_config import logger
from src.models.agent_dtos import UsageMetrics
from src.database.supabase_client import get_db_client

NO_STUDENT_NAME = "Student name is Missing. Required"
NO_SUBJECT = "Subject is missing. Required"
NO_USER_NAME = "User name is missing. Required"


@dataclass
class MainAgentData:
    student_name: str = NO_STUDENT_NAME
    subject: str = NO_SUBJECT
    user_name: str = NO_USER_NAME
    session_id: str = "None"


# ---------- AGENT ----------
class TutorVoiceAgent(Agent):
    metrics_keeper: metrics.UsageCollector
    job_context: JobContext

    def get_data(self) -> MainAgentData:
        if not hasattr(self, "session") or not hasattr(self.session, "userdata"):
            return MainAgentData()

        session_data: MainAgentData = self.session.userdata
        return session_data

    @property
    def lable(self) -> str:
        return "Quizzy Tutor"

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
        await self.session.generate_reply(
            instructions="Start conversation by saying `Hi` or `Hello` and then continue the conversation",
            allow_interruptions=False,
        )

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage
    ) -> None:
        await super().update_instructions(self.get_instructions())

    @function_tool
    async def end_the_call(self, message: str) -> None:
        self.session.say(
            "Good bye! This call will now get disconnected", allow_interruptions=False
        )
        job_ctx = get_job_context()
        job_ctx.shutdown()
        await job_ctx.api.room.delete_room(DeleteRoomRequest(room=job_ctx.room.name))

    @function_tool
    async def update_student_name(
        self, student_name: Annotated[str, "The student's name"]
    ) -> str:
        """
        Updates the student's name in the current session's user data.
        Args:
            context (RunContext): The current execution context.
            student_name (str): The new name to assign to the student.
        Returns:
            None
        """
        # if student_name is None or student_name.lower() == "student":
        self.session.userdata.student_name = student_name
        logger.info(
            f"Updating student name to: {student_name} : currently : {self.session.userdata.student_name}"
        )
        return "Alright I've updated the name"

    @function_tool
    async def update_subject(
        self, subject: Annotated[str, "Student's chosen subject"]
    ) -> str:
        """
        Updates the subject for the current student session.

        Args:
            subject (str): Student's chosen subject.

        Returns:
            None

        Notes:
            If the student's name is not set or is "student", the update is skipped.
            Updates the session's student_name and logs the change.
        """
        self.session.userdata.subject = subject
        logger.info(
            f"Updating subject to: {subject} : currently : {self.session.userdata.subject}"
        )
        return "Alright I've updated the subject"

    @function_tool
    async def start_quiz(self, message: str) -> str:
        """
        Initiates a quiz session for the student based on the provided message.
        Args:
            message (str): The input message triggering the quiz.
        Returns:
            str: A response message indicating the result of the quiz initiation or any validation errors.
        Raises:
            None
        Notes:
            - Validates the presence of a student name and subject in the session data.
            - Calls the QuizTaskEngine asynchronously to retrieve quiz data.
            - Returns a success message if all answers are correct, or an error message if validation fails.
        """

        stud_name = self.session.userdata.student_name
        sub = self.session.userdata.subject

        if stud_name == NO_STUDENT_NAME or stud_name == "":
            return "Invalid student name. Update the session data with a valid and relevant name and then retry again"
        if sub == NO_SUBJECT:
            return "Invalid subject. Update the session data with a valid and relevant subject and then retry again"

        user_name = "mitst"
        print(f"Calling the Quiz Enginer with stud_name: {stud_name}, sub: {sub}")
        quiz_data = await QuizTaskEngine(stud_name, sub, user_name)
        print(f"Quiz Data Retrieved : {quiz_data.assessments}")
        # Convert the list of dictionaries to a pandas DataFrame

        if quiz_data and quiz_data.assessments:
            # Create a list of all values from the dictionaries
            values = [list(d.values())[0] for d in quiz_data.assessments]
            # Create a pandas Series from the list of values and use value_counts()
            value_counts = pd.Series(values).value_counts()

            # Convert the Series to a dictionary
            results_summary = value_counts.to_dict()
        else:
            results_summary = "Looks like we're having some issues"
        print(f"Results summary : {results_summary}")
        await self.session.generate_reply(
            instructions=f"Inform the student politely that quiz is completed and share their results : {results_summary} and then end the call",
            allow_interruptions=False,
        )
        await self.end_the_call("End the call")
        return "You gave correct answers to all the questions"

    def get_instructions(self) -> str:
        print(f"Session Data : {self.get_data()}")
        return f"""
        You are Quizzy, a warm and patient voice tutor for kids aged 5 to 15.
        Your role is to only gather required information from the student and start the quiz.

        SPEAKING RULES:
        - Always greet the student warmly, encourage them and speak in plain spoken text that a child can understand.
        - Never mention tools, functions, code, JSON, or system details out loud.
        - Never describe or read function calls.
        - Sound natural, like a kind teacher: friendly, supportive, never robotic.
        - Voice mode: no symbols, no formatting, just natural English.
        - Valid subjects are only Science, English, Geography. Always ask student to choose a valid subject.

        BACKGROUND RULES (never spoken):
        - All system actions happen silently in the background.
        - Do not output explanations of tools. Only produce structured tool calls.

        SESSION DATA:
        - Student Name: {self.get_data().student_name}
        - Subject: {self.get_data().subject}
        - Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        INSTRUCTIONS:
        - If student name is missing or outdated → CALL `update_student_name`.
        - If subject is missing or outdated → CALL `update_subject`.
        - Once student name and subject are set → CALL `start_quiz`.
        - If `start_quiz` fails twice → politely tell the student there was a problem and end the session.
        - End the quiz session -> CALL `end_the_call`.
        """


async def log_usage(
    session_id: str, user_name: str, usage_collector: metrics.UsageCollector
) -> None:
    summary = usage_collector.get_summary()
    metrics = UsageMetrics(
        session_id=session_id,
        user_name=user_name,
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

    user_name = list(ctx.room.remote_participants.values())[0].identity
    session_id = ctx.job.id

    logger.info(f"AGENT STARTING WITH ROOM : {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    session = AgentSession(userdata=MainAgentData(session_id=ctx.job.id))

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

    ctx.add_shutdown_callback(
        lambda: log_usage(
            session_id=session_id,
            user_name=user_name,
            usage_collector=usage_collector,
        )
    )
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


if __name__ == "__main__":
    from livekit import agents

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=agent_entrypoint))
