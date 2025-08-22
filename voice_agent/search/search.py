from model.dtos import SearchResponse
from config.logging_config import logger


def search(q: str, top_k: int = 5):
    """Semantic search across ALL indexed content (no segregation by file type)."""
    # Lazy initialization of search components
    global embedding_processor, milvus_processor, hybrid_retriever
    
    if 'embedding_processor' not in globals():
        from .helper_class import EmbeddingProcessor
        embedding_processor = EmbeddingProcessor()
        
    if 'milvus_processor' not in globals():
        from .helper_class import MilvusProcessor
        milvus_processor = MilvusProcessor()
        
    if 'hybrid_retriever' not in globals():
        from .helper_class import EfficientHybridRetriever
        hybrid_retriever = EfficientHybridRetriever(milvus_processor, embedding_processor)
    
    logger.info(f"Performing search for query: {q} with top_k: {top_k}")
    
    # Use the new hybrid retriever with query rewriting
    results = hybrid_retriever.search(q, top_k)
    logger.info(f"Search completed with {len(results)} results")
    
    return SearchResponse(results=results)


def enhanced_search(q: str, top_k: int = 5):
    """Enhanced search with response synthesis."""
    # Lazy initialization of search components
    global embedding_processor, milvus_processor, hybrid_retriever, response_synthesizer
    
    if 'embedding_processor' not in globals():
        from .helper_class import EmbeddingProcessor
        embedding_processor = EmbeddingProcessor()
        
    if 'milvus_processor' not in globals():
        from .helper_class import MilvusProcessor
        milvus_processor = MilvusProcessor()
        
    if 'hybrid_retriever' not in globals():
        from .helper_class import EfficientHybridRetriever
        hybrid_retriever = EfficientHybridRetriever(milvus_processor, embedding_processor)
        
    if 'response_synthesizer' not in globals():
        from .helper_class import LightweightResponseSynthesizer
        response_synthesizer = LightweightResponseSynthesizer()
    
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