from livekit.agents import Agent
from livekit.plugins import sarvam, groq, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import noise_cancellation
from livekit.plugins import turn_detector
from livekit.plugins.turn_detector.english import EnglishModel


speech_to_text = sarvam.STT(language="en", model="saarika:v2.5", api_key="")

text_to_speech = sarvam.TTS(
    target_language_code="en-IN", model="bulbul:v2", api_key="", pitch=0.3, pace=1.2
)

large_language_model = groq.LLM(
    model="gpt-4", api_key="", tool_choice="auto", temperature=0.15, top_p=0.85
)


class TutorVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful tutor who will be talking to students.",
            tools=[],
            turn_detection=EnglishModel(),
            allow_interruptions=True,
            vad=silero.VAD.load(),
            stt=speech_to_text,
            tts=text_to_speech,
            llm=large_language_model,
        )
