from livekit.agents.metrics import LLMMetrics, TTSMetrics
from model.dtos import LlmMetricCollectorDto, TtsMetricCollectorDto


# Metrics Collections
async def llm_metrics_collection(
    user_id: str, session_id: str, llm_metrics: LLMMetrics
):
    metrics = LlmMetricCollectorDto(
        user_id=user_id,
        session_id=session_id,
        speech_id=llm_metrics.speech_id if llm_metrics.speech_id else "",
        time_to_first_token=llm_metrics.ttft,
        cancelled=llm_metrics.cancelled,
        completion_tokens=llm_metrics.completion_tokens,
        tokens_per_second=llm_metrics.tokens_per_second,
        prompt_tokens=llm_metrics.prompt_tokens,
        timestamp=llm_metrics.timestamp,
    )
    print(f"LLM Metrics Collected: {metrics}")


async def tts_metrics_collection(
    user_id: str, session_id: str, tts_metrics: TTSMetrics
):
    metrics = TtsMetricCollectorDto(
        user_id=user_id,
        session_id=session_id,
        speech_id=tts_metrics.speech_id if tts_metrics.speech_id else "",
        request_id=tts_metrics.request_id if tts_metrics.request_id else "",
        time_to_first_byte=tts_metrics.ttfb,
        cancelled=tts_metrics.cancelled,
        audio_duration=tts_metrics.audio_duration,
        characters_count=tts_metrics.characters_count,
        duration=tts_metrics.duration,
        timestamp=tts_metrics.timestamp,
    )
    print(f"TTS Metrics Collected: {metrics}")