import json
from groq import Groq
from config.settings import LLM_API_KEY
from search.search import enhanced_search
from config.logging_config import logger
from core.model_manager import get_embedding_processor, get_cross_encoder, get_response_synthesizer


def rag_tool_wrapper(query: str) -> str:
    """
    Wrapper to call enhanced_search and return the synthesized response.
    """
    # Load models on-demand using the model manager
    embedder = get_embedding_processor()
    cross_encoder = get_cross_encoder()
    synthesizer = get_response_synthesizer()
    
    result = enhanced_search(query)
    return result["synthesized_response"]


groq_client = Groq(api_key=LLM_API_KEY)


def evaluate_answer(question: str, student_answer: str) -> dict:
    """
    Evaluate student's answer.
    Returns dict with correctness, completeness, vocabulary, speech.
    """
    # Load models on-demand using the model manager
    embedder = get_embedding_processor()
    cross_encoder = get_cross_encoder()
    synthesizer = get_response_synthesizer()
    
    system_prompt = """You are a strict but friendly evaluator.
    Rate the student's answer between 0.0 and 1.0 on these metrics:
    - correctness (60%)
    - completeness (15%)
    - vocabulary (10%)
    - flawless speech (15%)
    Respond ONLY in valid JSON."""

    user_prompt = f"""
    Question: {question}
    Student's Answer: {student_answer}
    """

    completion = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = completion.choices[0].message.content
    try:
        if content is not None:
            return json.loads(content)
        else:
            logger.warning("LLM returned None content, returning fallback.")
            return {
                "correctness": 0.0,
                "completeness": 0.0,
                "vocabulary": 0.0,
                "flawless speech": 0.0,
            }
    except Exception:
        logger.warning("Failed to parse evaluation JSON, returning fallback.")
        return {
            "correctness": 0.0,
            "completeness": 0.0,
            "vocabulary": 0.0,
            "flawless speech": 0.0,
        }


# rag_tool = Tool(
#     name="Search",
#     description="Search the student's school books to answer questions. Input must be a string query.",
#     parameters={
#         "query": {
#             "type": "string",
#             "description": "Natural language question to look up in the school book knowledge base.",
#         }
#     },
#     func=lambda query: rag_tool_wrapper(query),
# )
