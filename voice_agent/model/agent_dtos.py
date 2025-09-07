from typing import Dict, List, Literal
from pydantic import BaseModel
import re


class QnAFromDb(BaseModel):
    question_id: str
    question: str
    answer: str


class ChatTranscript:
    sender: Literal["user", "assistant"] = "user"
    transcript: str = ""

    def __init__(self, sender: Literal["user", "assistant"], transcript: str):
        self.sender = sender
        self.transcript = transcript

    def convert_to_str(self) -> str:
        cleaned_transcript = re.sub(r"[^a-zA-Z0-9\s]", "", self.transcript)
        print(f"cleaned_transcript: {cleaned_transcript}")
        return f"{self.sender}: {cleaned_transcript}"


class QuizPackFromDb(BaseModel):
    quiz_pack: List[QnAFromDb] = []
    message: str = ""


class QuizPackAssessment(BaseModel):
    quiz_pack: List[Dict] = []
    message: str = ""


class UsageMetrics(BaseModel):
    session_id: str = "Not Set"
    user_name: str = "Not Set"
    mt_stt_audioduration: float = 0.0
    mt_llm_duration: int = 0
    mt_llm_completiontokens: int = 0
    mt_llm_prompttokens: int = 0
    mt_llm_promptcachetokens: int = 0
    mt_llm_totaltokens: int = 0
    mt_llm_tokenspersecond: float = 0.0
    mt_llm_ttft: float = 0.0
    mt_tts_audioduration: float = 0.0
    mt_tts_characterscount: int = 0
    mt_tts_duration: int = 0
    mt_tts_ttfb: int = 0
    mt_eou_utterancedelay: int = 0
    mt_eou_transcriptiondelay: int = 0
