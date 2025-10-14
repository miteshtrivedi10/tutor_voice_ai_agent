from sentence_transformers import SentenceTransformer, util
from src.config.logging import logger
# Load a pre-trained model for sentence embeddings
# 'all-MiniLM-L6-v2' is a good choice for speed and quality.
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_semantic_similarity(correct_answer: str, student_answer: str) -> str:
    """
    Calculates the semantic similarity score between two sentences.
    """
    # Encode the sentences to get their embeddings
    embeddings = model.encode([correct_answer, student_answer], convert_to_tensor=True)

    # Compute cosine similarity between the two embeddings
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])

    scored_item = similarity.item()

    logger.info(f"Semantic similarity score: {scored_item}")

    if scored_item > 0.9:
        return "CORRECT"

    if scored_item > 0.7:
        return "MOSTLY CORRECT"

    if scored_item > 0.45:
        return "PARTIALLY CORRECT"

    return "INCORRECT"
