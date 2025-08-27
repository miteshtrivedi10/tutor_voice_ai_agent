from model.dtos import SearchResponse
from config.logging_config import logger
from core.model_manager import (
    get_embedding_processor,
    get_cross_encoder,
    get_response_synthesizer,
)
from .helper_class import (
    EmbeddingProcessor,
    LightweightResponseSynthesizer,
    MilvusProcessor,
)
from .helper_class import EfficientHybridRetriever

# embedding_processor = get_embedding_processor()
embedding_processor = EmbeddingProcessor()

# For MilvusProcessor, we still need to initialize it directly since it's not cached
milvus_processor = MilvusProcessor()

# For EfficientHybridRetriever, we need to initialize it directly as well
hybrid_retriever = EfficientHybridRetriever(milvus_processor, embedding_processor)

# For response synthesizer, use the ModelManager
# response_synthesizer = get_response_synthesizer()
response_synthesizer = LightweightResponseSynthesizer()


# Use ModelManager to load models on-demand
# def get_search_components():

#     return embedding_processor, milvus_processor, hybrid_retriever, response_synthesizer


def search(q: str, top_k: int = 5):
    """Semantic search across ALL indexed content (no segregation by file type)."""
    logger.info(f"Performing search for query: {q} with top_k: {top_k}")

    # Load components on-demand
    # embedding_processor, milvus_processor, hybrid_retriever, response_synthesizer = (
    #     get_search_components()
    # )

    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)
    logger.info(f"Search completed with {len(results)} results")

    return SearchResponse(results=results)


def enhanced_search(q: str, top_k: int = 5):
    """Enhanced search with response synthesis."""
    logger.info(f"Performing enhanced search for query: {q} with top_k: {top_k}")

    # Load components on-demand
    # embedding_processor, milvus_processor, hybrid_retriever, response_synthesizer = (
    #     get_search_components()
    # )

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
