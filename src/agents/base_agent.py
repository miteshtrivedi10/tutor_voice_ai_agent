"""
Base agent class for voice agents in the tutor application
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, AsyncGenerator
import asyncio
import logging
from opentelemetry import trace

from livekit.agents import Agent, JobContext
from livekit.rtc import AudioFrame
from livekit.agents.llm import LLM
from livekit.plugins.silero import VAD
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins.deepgram import STT, TTS

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class BaseVoiceAgent(Agent, ABC):
    """Abstract base class for voice agents"""
    
    def __init__(
        self,
        ctx: JobContext,
        stt: STT,
        tts: TTS,
        llm: LLM,
        instructions: str = "",
        allow_interruptions: bool = True,
    ):
        super().__init__(
            instructions=instructions,
            allow_interruptions=allow_interruptions,
            stt=stt,
            tts=tts,
            llm=llm,
            vad=VAD.load(),
            turn_detection=MultilingualModel(),
        )
        self.ctx = ctx

    async def stt_node(
        self, audio: AsyncIterable[AudioFrame], model_settings: Any
    ) -> AsyncIterable[Any]:
        """Override STT node for custom processing, e.g., logging or input validation."""
        # Example: Add OpenTelemetry span for STT processing
        with tracer.start_as_current_span("stt_processing") as span:
            span.set_attribute("custom.input.validation", True)
            # Delegate to default STT
            return await super().stt_node(audio, model_settings)

    async def llm_node(
        self,
        chat_ctx: Any,
        tools: list[Any],
        model_settings: Any,
    ) -> AsyncIterable[Any]:
        """Override LLM node for custom tool orchestration and spans."""
        with tracer.start_as_current_span("llm_processing") as span:
            span.set_attribute("tools.count", len(tools))
            # Custom validation: Ensure context is not empty
            if not chat_ctx:
                logger.warning("Empty chat context in LLM node")
            # Delegate to default LLM with potential custom chaining
            return await super().llm_node(chat_ctx, tools, model_settings)

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: Any
    ) -> AsyncGenerator[AudioFrame, None]:
        """Override TTS node for streaming prosody adjustments (e.g., enthusiastic for kids)."""
        with tracer.start_as_current_span("tts_processing") as span:
            span.set_attribute("prosody.mode", "engaging_kids")
            # Example: Custom prosody (implement via TTS plugin params if supported)
            # For now, delegate to default with logging
            logger.info("Applying engaging prosody for TTS")
            
            # Properly delegate to super tts_node as async generator
            async for frame in super().tts_node(text, model_settings):
                yield frame

    @abstractmethod
    async def on_enter(self) -> None:
        """Called when the agent enters the session"""
        pass

    @abstractmethod
    async def on_exit(self) -> None:
        """Called when the agent exits the session"""
        pass