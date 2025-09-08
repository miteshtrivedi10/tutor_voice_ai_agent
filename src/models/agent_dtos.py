"""
DTOs for agent, using Pydantic for validation.
"""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .usage_metrics import UsageMetrics  # Assume exists


class QnAFromDb(BaseModel):
    id: str
    question: str
    answer: str


class QuizPackFromDb(BaseModel):
    id: str
    subject: str
    questions: List[QnAFromDb]


class QuizDataFromDb(BaseModel):
    assessments: List[Dict]


class QuizPackAssessment(BaseModel):
    """Assessment data for quiz packs"""

    quiz_pack_id: str
    student_name: str
    score: Optional[float] = None
    total_questions: int = 0
    completed_questions: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subject: str
    difficulty_level: Optional[str] = "medium"


class ChatMessage(BaseModel):
    """Individual message in chat transcript"""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None


class ChatTranscript(BaseModel):
    """Complete conversation transcript with timestamps and metadata"""

    session_id: str
    user_id: str
    messages: List[ChatMessage]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_messages: int = Field(default=0)
    total_tool_calls: int = 0
    quiz_progress: Optional[Dict] = None

    def __post_init__(self):
        self.total_messages = len(self.messages)
        self.total_tool_calls = sum(1 for msg in self.messages if msg.tool_calls)


class MainAgentData(BaseModel):
    """Pydantic model for session data with validation."""

    student_name: str = Field(..., min_length=1, description="Student's name")
    subject: Literal[
        "Science", "English", "Geography", "Subject is Missing. Required"
    ] = Field(..., description="Valid subjects only")
    user_name: str = Field(..., min_length=1, description="User name")
    session_id: str = Field(..., description="Session ID")
    state: str = Field(
        default="greeting", description="FSM state: greeting, collecting, quiz, ended"
    )
    chat_transcript: Optional[ChatTranscript] = None
    current_quiz_id: Optional[str] = None
    quiz_progress: Optional[int] = None
    assessment: Optional[QuizPackAssessment] = None


# Existing UsageMetrics
class UsageMetrics(BaseModel):
    session_id: str = "Not Set"
    user_name: str = "Not Set"
    mt_stt_audioduration: float = 0.0
    mt_llm_completiontokens: int = 0
    mt_llm_prompttokens: int = 0
    mt_llm_promptcachetokens: int = 0
    mt_tts_audioduration: float = 0.0
    mt_tts_characterscount: int = 0
    # Add more as needed
