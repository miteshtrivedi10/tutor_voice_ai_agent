from typing import Dict, List
import uuid
import torch
import time
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
import os
from config.settings import (
    EMBED_MODEL_NAME,
    MILVUS_API_KEY,
    MILVUS_ENDPOINT,
    MODELS_DIR,
    COLLECTION,
)
from config.logging_config import logger
from core.model_manager import model_manager

from pymilvus import MilvusClient, DataType, CollectionSchema, FieldSchema


class EmbeddingProcessor:
    def __init__(self):
        self.embedder = None
        self.vector_size = 384  # Set default vector size for BAAI/bge-base-en-v1.5
        # Use local models only
        self.use_hf_api = False

        if not self.use_hf_api:
            self._load_model()

    def _load_model(self):
        """Load embedding model with fallback to download"""

        try:
            logger.info(f"Attempting to load embedding model from: {MODELS_DIR}")
            self.embedder = SentenceTransformer(
                EMBED_MODEL_NAME, cache_folder=MODELS_DIR, local_files_only=True
            )
            logger.info("Successfully loaded embedding model from local cache")
        except Exception as e:
            logger.warning(f"Failed to load embedding model from local cache: {e}")
            logger.info("Downloading embedding model...")
            self.embedder = SentenceTransformer(
                EMBED_MODEL_NAME, cache_folder=MODELS_DIR
            )
            logger.info("Embedding model downloaded successfully")

        self.vector_size = self.embedder.get_sentence_embedding_dimension()

        # Small delay to ensure system resources are available
        time.sleep(0.1)

    def embed_texts(self, texts: list):
        """Generate embeddings for a list of texts"""
        # Normalize via SentenceTransformer (already L2/cosine friendly)
        return self.embedder.encode(texts, normalize_embeddings=True).tolist()


class EfficientHybridRetriever:
    def __init__(self, milvus_client, embedder):
        self.milvus_client = milvus_client
        self.embedder = embedder
        self.cross_encoder = None
        self.use_hf_api = False

        # Always use local models
        if True:  # not self.use_hf_api:
            try:
                # MiniLM-based cross-encoder (small and efficient)
                logger.info(
                    f"Attempting to load cross-encoder model from: {MODELS_DIR}"
                )
                self.cross_encoder = CrossEncoder(
                    "cross-encoder/ms-marco-MiniLM-L-2-v2",
                    cache_folder=MODELS_DIR,  # Ensure model is downloaded to the correct directory
                    local_files_only=True,  # Try to load from local cache first
                )
                logger.info("Successfully loaded cross-encoder model from local cache")
            except Exception as e:
                logger.warning(f"Failed to load cross-encoder from local cache: {e}")
                logger.info("Downloading cross-encoder model...")
                self.cross_encoder = CrossEncoder(
                    "cross-encoder/ms-marco-MiniLM-L-2-v2",
                    cache_folder=MODELS_DIR,  # Ensure model is downloaded to the correct directory
                )
                logger.info("Cross-encoder model downloaded successfully")

        # Small delay to ensure system resources are available
        time.sleep(0.1)

    def search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> List[Dict]:
        # Vector search results
        vector_results = self._vector_search(query, top_k * 2)

        # Keyword search results
        keyword_results = self._keyword_search(query, top_k * 2)

        # Hybrid combination with small model re-ranking
        combined_results = self._reciprocal_rank_fusion(
            vector_results, keyword_results, top_k
        )

        if self.cross_encoder:
            final_results = self._cross_encoder_rerank(query, combined_results, top_k)
        else:
            # Fallback to simple ranking
            final_results = combined_results[:top_k]

        return final_results

    def _vector_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Perform vector search using Milvus"""
        # Generate query embedding
        query_vector = self.embedder.embed_texts([query])[0]

        # Search in Milvus
        search_results = self.milvus_client.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        # Convert results to the expected format
        formatted_results = []
        for result in search_results:
            formatted_results.append(
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "modality": result.payload.get("modality", ""),
                    "source_file": result.payload.get("source_file", ""),
                    "page": result.payload.get("page"),
                    "extra": result.payload.get("extra"),
                }
            )

        return formatted_results

    def _keyword_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Perform keyword search using Milvus"""
        # For simplicity, we'll use the same Milvus client but with a different search strategy
        # In a more complex implementation, you might use a separate keyword-based search engine
        # Milvus doesn't have built-in full-text search like Qdrant,
        # so we'll perform a simple vector search as a placeholder
        # In a production environment, you might want to integrate with Elasticsearch or similar
        # Milvus doesn't support query_filter like Qdrant, so we'll just do a regular search
        try:
            # Note: Milvus doesn't support full-text search like Qdrant,
            # so we'll perform a simple vector search as a placeholder
            search_results = self.milvus_client.search(
                query_vector=self.embedder.embed_texts([query])[0],
                top_k=top_k,
            )

            # Convert results to the expected format
            formatted_results = []
            for result in search_results:
                formatted_results.append(
                    {
                        "id": result.id,
                        "score": result.score,
                        "text": result.payload.get("text", ""),
                        "modality": result.payload.get("modality", ""),
                        "source_file": result.payload.get("source_file", ""),
                        "page": result.payload.get("page"),
                        "extra": result.payload.get("extra"),
                    }
                )

            return formatted_results
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            # Fallback to vector search if keyword search is not supported
            return self._vector_search(query, top_k)

    def _reciprocal_rank_fusion(
        self, vector_results: List[Dict], keyword_results: List[Dict], top_k: int = 5
    ) -> List[Dict]:
        """Combine vector and keyword search results using reciprocal rank fusion"""
        # Create a dictionary to store fused scores
        fused_scores = {}

        # Process vector search results
        for i, result in enumerate(vector_results):
            doc_id = result["id"]
            # Reciprocal rank score (1 / rank)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (i + 1)

        # Process keyword search results
        for i, result in enumerate(keyword_results):
            doc_id = result["id"]
            # Reciprocal rank score (1 / rank)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (i + 1)

        # Sort by fused score (descending)
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        # Reconstruct the result objects with fused scores
        fused_results = []
        for doc_id, score in sorted_results[:top_k]:
            # Find the original result object (either from vector or keyword results)
            original_result = None
            for result in vector_results + keyword_results:
                if result["id"] == doc_id:
                    original_result = result
                    break

            if original_result:
                # Update the score with the fused score
                fused_result = original_result.copy()
                fused_result["score"] = score
                fused_results.append(fused_result)

        return fused_results

    def _cross_encoder_rerank(
        self, query: str, results: List[Dict], top_k: int = 5
    ) -> List[Dict]:
        """Rerank results using a cross-encoder model"""
        if not results:
            return results[:top_k]

        else:
            if not self.cross_encoder:
                return results[:top_k]

            # Prepare pairs of query and document texts
            pairs = []
            for result in results:
                pairs.append([query, result["text"]])

            # Get relevance scores from cross-encoder
            scores = self.cross_encoder.predict(pairs)

            # Add scores to results
            for i, result in enumerate(results):
                result["cross_encoder_score"] = float(scores[i])

            # Sort by cross-encoder score (descending)
            reranked_results = sorted(
                results, key=lambda x: x["cross_encoder_score"], reverse=True
            )

            return reranked_results[:top_k]


class MilvusProcessor:
    def __init__(self):
        # Initialize Milvus client with cloud endpoint and API key
        logger.info(f"Connecting to Milvus at {MILVUS_ENDPOINT}")

        self.client = MilvusClient(
            uri=MILVUS_ENDPOINT,  # Cloud endpoint
            token=MILVUS_API_KEY,  # API key and secret
        )
        self.collection = COLLECTION
        self._validate_collection()

    def _validate_collection(self):
        """Validate that the Milvus collection exists"""
        try:
            # Check if collection exists
            if not self.client.has_collection(self.collection):
                error_msg = f"Collection {self.collection} not available. Please ensure the collection exists in Milvus."
                logger.error(error_msg)
                raise SystemExit(error_msg)

            # Get vector size from embeddings module for validation
            from search.helper_class import EmbeddingProcessor

            embedder = EmbeddingProcessor()
            self.vector_size = embedder.vector_size

            # Load collection
            self.client.load_collection(self.collection)

            logger.info(
                f"Collection {self.collection} validated and loaded successfully"
            )

        except SystemExit:
            # Re-raise SystemExit to exit the application
            raise
        except Exception as e:
            error_msg = f"Error validating collection: {e}"
            logger.error(error_msg)
            raise SystemExit(error_msg)

    def search(self, query_vector: list, top_k: int = 5):
        """Search for similar vectors in Milvus"""
        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10},
            }

            results = self.client.search(
                collection_name=self.collection,
                data=[query_vector],
                anns_field="vector",
                search_params=search_params,
                limit=min(max(top_k, 1), 50),
                output_fields=[
                    "id",
                    "text",
                    "modality",
                    "source_file",
                    "page",
                    "extra",
                ],
            )

            # Format results to match the expected interface (mimic Qdrant result structure)
            formatted_results = []
            if results:
                for hit in results[0]:
                    # Create a mock object that mimics the Qdrant result structure
                    class MockResult:
                        def __init__(self, id, score, payload):
                            self.id = id
                            self.score = score
                            self.payload = payload

                    formatted_results.append(
                        MockResult(
                            id=hit.get("id", ""),
                            score=hit.get("distance", 0),
                            payload={
                                "text": hit.get("text", ""),
                                "modality": hit.get("modality", ""),
                                "source_file": hit.get("source_file", ""),
                                "page": hit.get("page"),
                                "extra": hit.get("extra", {}),
                            },
                        )
                    )

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            # Return empty list as fallback
            return []


class LightweightResponseSynthesizer:
    def __init__(self):
        # Try Phi-3 Mini first (recommended approach), then TinyLlama, then fallback
        models_in_order = [
            (
                "microsoft/Phi-3-mini-4k-instruct",
                "Phi-3 Mini (2.2GB)",
            ),  # 2.2GB - recommended
            # (
            #     "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            #     "TinyLlama (1.1GB)",
            # ),  # 1.1GB - fallback
            # (
            #     "stabilityai/stablelm-2-zephyr-1_6b",
            #     "StableLM (1.6GB)",
            # ),  # 1.6GB - alternative
        ]

        self.generator = None
        self.model_name = None
        self.use_hf_api = False
        self.use_llama_cpp = False

        if not self.use_hf_api:
            # Try to load with llama-cpp-python first
            try:
                from llama_cpp import Llama

                # Path to the GGUF model file
                gguf_model_path = os.path.join(
                    MODELS_DIR, "phi-3-mini-4k-instruct.Q4_K_M.gguf"
                )

                if os.path.exists(gguf_model_path):
                    logger.info(f"Loading GGUF model from: {gguf_model_path}")
                    self.generator = Llama(
                        model_path=gguf_model_path,
                        n_ctx=4096,  # Context length
                        n_threads=4,  # Number of CPU threads
                        n_gpu_layers=(
                            -1 if torch.cuda.is_available() else 0
                        ),  # Use GPU if available
                    )
                    self.model_name = "Phi-3 Mini (GGUF)"
                    self.use_llama_cpp = True
                    logger.info("Successfully loaded GGUF model")
                else:
                    logger.warning(f"GGUF model not found at: {gguf_model_path}")
            except ImportError:
                logger.warning(
                    "llama-cpp-python not installed, falling back to transformers"
                )
            except Exception as e:
                logger.warning(f"Failed to load GGUF model: {e}")

            # Fallback to transformers if GGUF model is not available
            if not self.use_llama_cpp:
                for model_path, model_description in models_in_order:
                    try:
                        logger.info(
                            f"Attempting to load {model_description} from: {MODELS_DIR}"
                        )
                        self.generator = pipeline(
                            "text-generation",
                            model=model_path,
                            device=0 if torch.cuda.is_available() else -1,
                            torch_dtype=(
                                torch.float16
                                if torch.cuda.is_available()
                                else torch.float32
                            ),
                            trust_remote_code=True,  # Some models need this
                            cache_dir=MODELS_DIR,  # Ensure models are downloaded to the correct directory
                        )
                        self.model_name = model_description
                        logger.info(f"Successfully loaded {model_description}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {model_description}: {e}")
                        continue

            if self.generator:
                logger.info(f"Using {self.model_name} for response synthesis")
            else:
                logger.info("Falling back to template-based approach")

        # Small delay to ensure system resources are available
        time.sleep(0.1)

    def synthesize(self, query: str, retrieved_chunks: List[Dict]) -> str:
        if not self.generator:
            # Template-based fallback (no model needed)
            return self._template_based_synthesis(query, retrieved_chunks)

        # Prepare context for small model
        context = self._prepare_compact_context(retrieved_chunks)

        # Create efficient prompt - model-specific formatting
        if "Phi-3" in (self.model_name or ""):
            # Phi-3 specific prompt format
            prompt = f"""
<|user|>
Context: {context[:800]}  # Limit context for small models

Question: {query}
<|end|>
<|assistant|>"""
        else:
            # Generic prompt format
            prompt = f"""
Context: {context[:800]}  # Limit context for small models

Question: {query}
Answer:"""

        if self.use_llama_cpp:
            # Use llama-cpp-python for text generation
            try:
                response = self.generator(
                    prompt,
                    max_tokens=200,  # Limit output length
                    temperature=0.7,
                    top_p=0.9,
                    repeat_penalty=1.2,
                    stop=[
                        "<|end|>",
                        "<|user|>",
                        "<|assistant|>",
                    ],  # Stop tokens for Phi-3
                )

                # Extract generated text
                if isinstance(response, dict) and "choices" in response:
                    generated_text = response["choices"][0]["text"]
                    return generated_text.strip()
                else:
                    # Handle unexpected response format
                    return str(response).strip()
            except Exception as e:
                logger.error(
                    f"Generation failed with llama-cpp-python, falling back to template: {e}"
                )
                return self._template_based_synthesis(query, retrieved_chunks)
        else:
            # Generate response with conservative parameters
            try:
                response = self.generator(
                    prompt,
                    max_new_tokens=200,  # Limit output length
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.2,
                )

                # Extract generated text (handling different response formats)
                if isinstance(response, list) and len(response) > 0:
                    generated_text = response[0]["generated_text"]
                    # Remove prompt from response
                    if prompt in generated_text:
                        return generated_text.replace(prompt, "").strip()
                    else:
                        # For Phi-3 format
                        if "<|assistant|>" in generated_text:
                            return generated_text.split("<|assistant|>")[-1].strip()
                        return generated_text.strip()
                else:
                    # Handle case where response is a string
                    generated_text = response
                    # Remove prompt from response
                    if prompt in generated_text:
                        return generated_text.replace(prompt, "").strip()
                    else:
                        # For Phi-3 format
                        if "<|assistant|>" in generated_text:
                            return generated_text.split("<|assistant|>")[-1].strip()
                        return generated_text.strip()
            except Exception as e:
                logger.error(f"Generation failed, falling back to template: {e}")
                return self._template_based_synthesis(query, retrieved_chunks)

    def _prepare_compact_context(self, chunks: List[Dict]) -> str:
        """Prepare compact context with proper formatting"""
        context_parts = []
        for i, chunk in enumerate(chunks[:3], 1):  # Top 3 chunks
            text = chunk.get("text", "")
            source = chunk.get("source_file", "Unknown")
            page = chunk.get("page", "N/A")
            context_parts.append(f"Source {i} ({source}, Page {page}): {text}")

        return "\n\n".join(context_parts)

    def _template_based_synthesis(self, query: str, chunks: List[Dict]) -> str:
        """Template-based response generation"""
        if not chunks:
            return "I couldn't find relevant information to answer your query."

        # Simple template - can be enhanced with more sophisticated templates
        response_templates = [
            "Based on the information available, {query} can be understood as follows:\n\n{content}",
            "Here's what I found about {query}:\n\n{content}",
            "Regarding {query}, the information suggests:\n\n{content}",
        ]

        # Extract content from chunks
        content_parts = []
        for chunk in chunks:
            content_parts.append(chunk.get("text", ""))

        content = "\n\n".join(content_parts[:2])  # Limit content length
        return response_templates[0].format(query=query, content=content)
