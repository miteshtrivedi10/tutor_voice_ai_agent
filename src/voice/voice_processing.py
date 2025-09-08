"""
Voice processing components for the voice tutor application
"""
from livekit.plugins import deepgram, silero, openai, sarvam, groq


# Initialize components
# speech_to_text = deepgram.STT(
#     language="en-IN",
#     profanity_filter=True,
#     punctuate=False,
#     detect_language=False,
#     interim_results=False,
#     filler_words=False,
#     mip_opt_out=True,
#     smart_format=True,
#     model="nova-3-general",
# )

speech_to_text = sarvam.STT(
    model="saarika:v2.5",
    language="en-IN",
)

# text_to_speech = deepgram.TTS(mip_opt_out=True, model="aura-2-thalia-en")

text_to_speech = sarvam.TTS(
    model="bulbul:v2",
    target_language_code="en-IN",
    speaker="karun",
    # pitch=0.7,
    # pace=0.7,
    enable_preprocessing=True,
)

large_language_model = groq.LLM(
    model="moonshotai/kimi-k2-instruct",
    temperature=0.4,
    tool_choice="auto",
    top_p=0.8,
)

# Alternative LLM implementations (commented out)
# large_language_model = openai.LLM.with_ollama(
#     model="deepseek-chat",
#     temperature=0.4,
#     tool_choice="auto",
#     top_p=0.7,
#     reasoning_effort="low",
# )

# large_language_model = openai.LLM(
#     model="meta-llama/llama-3.3-70b-instruct:free",
#     api_key="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",
#     base_url="https://openrouter.ai/api/v1",
#     temperature=0.4,
#     top_p=0.7,
#     reasoning_effort="low",
#     tool_choice="auto",
# )