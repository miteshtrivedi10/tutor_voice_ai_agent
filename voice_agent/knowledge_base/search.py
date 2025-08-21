from voice_agent.knowledge_base.helper_class import (
    EfficientHybridRetriever,
    EmbeddingProcessor,
    LightweightResponseSynthesizer,
    QdrantProcessor,
)
from voice_agent.model.dtos import SearchResponse


embedding_processor = EmbeddingProcessor()
qdrant_processor = QdrantProcessor()
hybrid_retriever = EfficientHybridRetriever(qdrant_processor, embedding_processor)
response_synthesizer = LightweightResponseSynthesizer()


def search(q: str, top_k: int = 5):
    """Semantic search across ALL indexed content (no segregation by file type)."""

    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)

    return SearchResponse(results=results)


def enhanced_search(q: str, top_k: int = 5):
    """Enhanced search with response synthesis."""

    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)

    # Generate a synthesized response
    synthesized_response = response_synthesizer.synthesize(q, results)

    return {
        "query": q,
        "search_results": results,
        "synthesized_response": synthesized_response,
    }
