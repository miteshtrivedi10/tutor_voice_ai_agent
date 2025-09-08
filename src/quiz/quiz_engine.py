"""
Quiz engine implementation for the voice tutor application
"""
from collections.abc import AsyncIterable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from dotenv import load_dotenv

from livekit.agents import AgentTask, function_tool
from livekit.agents.llm import FunctionTool, RawFunctionTool
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.agents.llm.llm import ChatChunk
from livekit.agents.voice.agent import ModelSettings
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import RunContext
from livekit.plugins import silero

from src.config.logging_config import logger
from src.models.agent_dtos import QuizPackFromDb
from src.database.supabase_client import get_db_client
from src.voice.voice_processing import speech_to_text, text_to_speech, large_language_model
from src.qa_metrics.evaluator import initialise_pedant


# Load environment variables
load_dotenv(override=True)


@dataclass
class QuizTaskData:
    quiz_pack_from_db: QuizPackFromDb = field(default_factory=lambda: QuizPackFromDb())
    current_question_and_answer: Dict = field(default_factory=dict)
    current_q_index: int = field(default_factory=int)
    total_qna: int = field(default_factory=int)
    assessments: List[Dict] = field(default_factory=list)


class QuizTaskEngine(AgentTask[QuizTaskData]):
    student_name: str
    subject: str
    user_name: str

    def get_data(self) -> QuizTaskData:
        # Handle case where session userdata might not be initialized yet
        if not hasattr(self, "session") or not hasattr(self.session, "userdata"):
            empty_data = QuizTaskData()
            empty_data.current_question_and_answer = {
                "question": "",
                "answer": "",
                "question_id": "",
            }
            return empty_data
        session_data: QuizTaskData = self.session.userdata
        return session_data

    def __init__(self, student_name: str, subject: str, user_name: str):
        self.student_name = student_name
        self.subject = subject
        self.user_name = user_name

        super().__init__(
            instructions=self.get_instructions(),
            allow_interruptions=True,
            stt=speech_to_text,
            tts=text_to_speech,
            llm=large_language_model,
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )

    async def on_enter(self) -> None:
        self.session.userdata = QuizTaskData()
        self.prefill_questions_to_session_data()
        self.session.say(f"Shall we start {self.student_name}?")

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage
    ) -> None:
        # logger.info(f"Current Instructions : {self.instructions}")
        await super().update_instructions(self.get_instructions())

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

    @function_tool
    async def evaluation_tool(
        self,
        context: RunContext,
        question_id: str,
        question: str,
        answer: str,
        student_answer: str,
    ) -> str:
        """
        Evaluates a student's answer to a given question and returns an assessment result.
        """
        logger.info(f"Evaluating answer for question with id: {question_id}")
        quiz_data: QuizTaskData = self.session.userdata
        scores = initialise_pedant().get_score(
            answer, student_answer, question=question
        )
        logger.info(f"SCORES : {scores} for QUESTION-ID : {question_id}")
        quiz_data.assessments.append({question_id: "Correct"})
        return "You're answer is correct"

    def prefill_questions_to_session_data(self) -> None:
        logger.info("Prefilling questions to session data")
        session_data = self.session.userdata
        try:
            # Fetch questions from Supabase
            logger.info(
                f"Fetching questions for user: {self.user_name}, subject: {self.subject}"
            )
            quiz_pack_from_db = get_db_client().fetch_random_questions(
                self.user_name, self.subject, 3
            )

            if len(quiz_pack_from_db.quiz_pack) == 0:
                logger.warning(quiz_pack_from_db.message)
                session_data.quiz_pack_from_db.message = f"No questions for subject : {self.subject} retrieved from database. Message : {quiz_pack_from_db.message}"

            session_data.quiz_pack_from_db = quiz_pack_from_db
            session_data.current_q_index = 1
            session_data.total_qna = len(quiz_pack_from_db.quiz_pack)

            session_data.current_question_and_answer["question"] = (
                session_data.quiz_pack_from_db.quiz_pack[
                    session_data.current_q_index
                ].question
            )
            session_data.current_question_and_answer["question_id"] = (
                session_data.quiz_pack_from_db.quiz_pack[
                    session_data.current_q_index
                ].question_id
            )
            session_data.current_question_and_answer["answer"] = (
                session_data.quiz_pack_from_db.quiz_pack[
                    session_data.current_q_index
                ].answer
            )
            print(
                f"Total questions fetched are {len(session_data.quiz_pack_from_db.quiz_pack)}"
            )
        except Exception as e:
            session_data.quiz_pack_from_db.message = (
                f"Looks like system issue, since there are no questions available"
            )
            logger.error(f"Unable to fetch the questions {e}")

    @function_tool
    async def is_quiz_completed(
        self, total_quiz_questions: int, current_question_number: int
    ) -> str:
        """
        Determines whether the quiz has been completed based on the current question number.
        """
        if current_question_number <= total_quiz_questions:
            return "Quiz is not completed yet."
        return "Quiz is now completed"

    @function_tool
    async def quiz_completed(
        self, total_quiz_questions: int, current_quiz_question: int
    ) -> None:
        """
        Handles the completion of the quiz by the user.
        """
        print(
            f"Quiz completed with {current_quiz_question} out of {total_quiz_questions} questions"
        )
        self.complete(self.session.userdata)

    @function_tool
    async def fetch_qna(self, current_question_number: int) -> Dict:
        """
        Asynchronously fetches the question, answer, and question ID for the specified question number
        from the user's current quiz session data.
        """
        tool_output = dict(question="", answer="", question_id="", error_message="")
        session_data: QuizTaskData = self.session.userdata
        logger.info(
            f"Fetching the questions for question number {current_question_number} and session index is {session_data.current_q_index}"
        )
        try:
            if session_data.total_qna > 0:
                session_data.current_question_and_answer["question"] = (
                    session_data.quiz_pack_from_db.quiz_pack[
                        current_question_number - 1
                    ].question
                )
                session_data.current_question_and_answer["question_id"] = (
                    session_data.quiz_pack_from_db.quiz_pack[
                        current_question_number - 1
                    ].question_id
                )
                session_data.current_question_and_answer["answer"] = (
                    session_data.quiz_pack_from_db.quiz_pack[
                        current_question_number - 1
                    ].answer
                )

                tool_output["question"] = session_data.current_question_and_answer[
                    "question"
                ]
                tool_output["answer"] = session_data.current_question_and_answer[
                    "answer"
                ]
                tool_output["question_id"] = session_data.current_question_and_answer[
                    "question_id"
                ]
                session_data.current_q_index = current_question_number + 1
            logger.info(f"Fetched Question Details : {tool_output}")
            return tool_output
        except Exception as e:
            logger.error(f"Unable to fetch the question from FETCH_QNA {e}")
            tool_output["error_message"] = (
                f"Technical difficulty in fetching the next question"
            )
            return tool_output

    def get_instructions(self) -> str:
        return f"""
            Your role is to conduct a spoken quiz with descriptive questions.
            Do not greet or wish the student, it is already done earlier.
            Continue with the conversation and don't wait for the student's response.
            Generate response in plain english only — no markdown, symbols, code, or JSON.
            Be natural and kind, like a patient teacher. Never robotic.
            Do not mention tools, functions, or internal steps. Do not hallucinate.
            Only pause when waiting for the student's response.
            Your role is only guide and mentor so never ever give away any answers to the student.

            VOICE MODE: No symbols. No formatting. Just plain spoken English.

            Context:
            - Date/Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            - Name: {self.student_name}
            - Subject: {self.subject}
            - Current Question Number: {self.get_data().current_q_index}
            - Total Questions: {self.get_data().total_qna}
            - Details : {self.get_data().current_question_and_answer}
            - Remaining Questions: {self.get_data().total_qna - self.get_data().current_q_index}

            Instructions:
            - Use words like Excellent, Good Job, Great, Nice one, You're doing great, Very Good, Cool, No problem, let me explain, Good try, Could have been better, but don't be repetitive.
            - For asking question use `fetch_qna` function, never create your own questions. Only ask questions which are officially coming from fetch_qna function
            - Never provide the answer for a quiz question to the student.
            - Evaulate the answer using `evaluation_tool` only and pass relevant parameters to the function.
            - Evaluation response does not require any student response, always continue.
            - To check, if the quiz is complete, use `is_quiz_completed` function
            - Mark the quiz complete using `quiz_completed` function, congratulate the student and inform student that session is over.
        """