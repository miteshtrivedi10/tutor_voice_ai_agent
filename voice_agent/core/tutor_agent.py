import asyncio
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    RunContext,
    cli,
    function_tool,
    BuiltinAudioClip,
)
from livekit.plugins import sarvam, groq, silero, deepgram, noise_cancellation
from livekit.plugins.turn_detector.english import EnglishModel
from tavily import TavilyClient
from core.tools import evaluate_answer, rag_tool_wrapper

# Logger is configured via config.logging_config
from config.logging_config import logger
from config.settings import (
    DEEPGRAM_API_KEY,
    LLM_API_KEY,
    SARVAM_API_KEY,
    TAVILY_API_KEY,
)
from core.instructions import DEVELOPMENT
from langchain_core.messages import trim_messages
from langchain_core.messages.utils import count_tokens_approximately

# Load environment variables
_ = load_dotenv(override=True)

# Initialize Tavily client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Initialize components
speech_to_text = sarvam.STT(
    language="en-IN", model="saarika:v2.5", api_key=SARVAM_API_KEY
)


# text_to_speech = sarvam.TTS(
#     target_language_code="en-IN",
#     model="bulbul:v2",
#     api_key=SARVAM_API_KEY,
#     pitch=0.8,
#     speaker="manisha",
#     pace=1.1,
# )


def safe_history(messages, max_tokens=1000):
    return trim_messages(
        messages=messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )


text_to_speech = deepgram.TTS(api_key=DEEPGRAM_API_KEY, mip_opt_out=True)

large_language_model = groq.LLM(
    model="gemma2-9b-it",
    api_key=LLM_API_KEY,
    temperature=0.1,
    tool_choice="auto",
    top_p=0.85,
)


class TutorVoiceAgent(Agent):
    def __init__(self, ctx: JobContext):
        # Define tools
        self.answer_ratings = []

        def eval_tool_wrapper(question: str, student_answer: str):
            scores = evaluate_answer(question, student_answer)
            self.store_rating(question, student_answer, scores)
            return scores  # return so LLM can see it if needed

        # eval_tool = Tool(
        #     name="EvaluateAnswer",
        #     description="Evaluate a student's answer against the expected answer. Returns JSON with scores.",
        #     parameters={
        #         "question": {"type": "string"},
        #         "student_answer": {"type": "string"},
        #     },
        #     func=eval_tool_wrapper,
        # )

        @function_tool
        async def search_knowledge(self, context: RunContext, query: str) -> str:
            """
            Asynchronously searches for knowledge based on the provided query using a retrieval-augmented generation (RAG) tool.
            Args:
                context (RunContext): The current runtime context for the operation.
                query (str): The search query string.
            Returns:
                str: The response retrieved from the RAG tool based on the query.
            """

            response = rag_tool_wrapper(query)
            return response

        @function_tool
        async def evaluation_tool(
            self, context: RunContext, question: str, student_answer: str
        ) -> dict:
            """
            Evaluates a student's answer to a given question using an evaluation tool.

            Args:
                context (RunContext): The current execution context.
                question (str): The question posed to the student.
                student_answer (str): The student's answer to the question.

            Returns:
                dict: A dictionary containing the evaluation scores of the student's answer.
            """

            scores = eval_tool_wrapper(question, student_answer)
            return scores

        super().__init__(
            instructions=DEVELOPMENT,
            turn_detection=EnglishModel(),
            allow_interruptions=True,
            vad=silero.VAD.load(),
            stt=speech_to_text,
            tts=text_to_speech,
            llm=large_language_model,
            tools=[search_knowledge, evaluation_tool],
        )

    def store_rating(self, question: str, student_answer: str, scores: dict):
        self.answer_ratings.append(
            {"question": question, "student_answer": student_answer, **scores}
        )

    def export_ratings(self):
        return self.answer_ratings

    async def on_enter(self):
        self.session.generate_reply(
            instructions="""
            Greet user politely and ask how can I assist you today.
            """
        )

    def llm_node(self, chat_ctx, tools, model_settings):
        # Apply sliding window logic to limit context size
        chat_ctx.items = chat_ctx.items[-10:]  # Keep only the last 10 messages
        logger.info(f"Total Messages In Context : {len(chat_ctx.items)}")
        return Agent.default.llm_node(self, chat_ctx, tools, model_settings)


async def agent_entrypoint(ctx: JobContext):
    """Main entrypoint for the voice agent"""
    logger.info(f"Agent starting for room: {ctx.room.name}")

    try:
        await ctx.connect()
        logger.info(f"Connected to room: {ctx.room.name}")

        # Create agent session
        session = AgentSession()

        # Create background audio player
        background_audio = BackgroundAudioPlayer(
            ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.8),
            thinking_sound=[
                AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.8),
                AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.7),
            ],
        )

        # Start the agent session
        agent = TutorVoiceAgent(ctx=ctx)
        await session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(
                audio_enabled=True,
                video_enabled=False,
                text_enabled=False,
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        await background_audio.start(room=ctx.room, agent_session=session)

        # Keep the agent running
        try:
            while True:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            logger.info(f"Agent session cancelled for room: {ctx.room.name}")

    except Exception as e:
        logger.error(f"Error in agent entrypoint: {e}")
        raise
    finally:
        logger.info(f"Agent finished for room: {ctx.room.name}")


# For running as a standalone worker
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=agent_entrypoint))
