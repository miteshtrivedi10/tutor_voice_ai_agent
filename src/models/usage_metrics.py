"""
Usage metrics models for tracking agent performance and resource consumption
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MetricType(Enum):
    """Types of usage metrics tracked"""

    LLM_TOKENS = "llm_tokens"
    STT_PROCESSING_TIME = "stt_processing_time"
    TTS_GENERATION_TIME = "tts_generation_time"
    TOOL_EXECUTION_COUNT = "tool_execution_count"
    SESSION_DURATION = "session_duration"
    ERROR_RATE = "error_rate"


@dataclass
class UsageMetric:
    """Individual usage metric record"""

    metric_type: MetricType
    value: float
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    tool_name: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class SessionMetrics:
    """Aggregated metrics for a single session"""

    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tokens: int = 0
    tool_calls: int = 0
    processing_time: float = 0.0
    errors: int = 0
    metrics: List[UsageMetric] = []

    def __post_init__(self):
        self.metrics = []


@dataclass
class UsageMetrics:
    """Collection of usage metrics for agent operations"""

    session_metrics: List[SessionMetrics]
    total_sessions: int = 0
    total_tokens: int = 0
    total_errors: int = 0
    creation_time: datetime = datetime.now()

    def __post_init__(self):
        self.total_sessions = len(self.session_metrics)


@dataclass
class DailyUsageReport:
    """Daily usage statistics for reporting and monitoring"""

    date: datetime
    total_sessions: int
    total_users: int
    avg_session_duration: float
    total_tokens_used: int
    total_errors: int
    most_used_tools: dict[str, int]
    peak_hours: List[tuple[int, int]]  # (hour, session_count)
