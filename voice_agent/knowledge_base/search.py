from voice_agent.knowledge_base.helper_class import (
    EfficientHybridRetriever,
    EmbeddingProcessor,
    LightweightResponseSynthesizer,
    QdrantProcessor,
)
from voice_agent.model.dtos import SearchResponse
from config.logging_config import logger


embedding_processor = EmbeddingProcessor()
qdrant_processor = QdrantProcessor()
hybrid_retriever = EfficientHybridRetriever(qdrant_processor, embedding_processor)
response_synthesizer = LightweightResponseSynthesizer()


def search(q: str, top_k: int = 5):
    """Semantic search across ALL indexed content (no segregation by file type)."""
    logger.info(f"Performing search for query: {q} with top_k: {top_k}")

    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)
    logger.info(f"Search completed with {len(results)} results")

    return SearchResponse(results=results)


def enhanced_search(q: str, top_k: int = 5):
    """Enhanced search with response synthesis."""
    logger.info(f"Performing enhanced search for query: {q} with top_k: {top_k}")

    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)
    logger.info(f"Search completed with {len(results)} results")

    # Generate a synthesized response
    synthesized_response = response_synthesizer.synthesize(q, results)
    logger.info("Response synthesis completed")

    return {
        "query": q,
        "search_results": results,
        "synthesized_response": synthesized_response,
    }
