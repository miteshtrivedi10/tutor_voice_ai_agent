from typing import Dict, List
import uuid
import torch
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.settings import EMBED_MODEL_NAME, MODELS_DIR, QDRANT_HOST, QDRANT_PORT, COLLECTION
from config.logging_config import logger


class EmbeddingProcessor:
    def __init__(self):
        self.embedder = None
        self.vector_size = None
        self._load_model()

    def _load_model(self):
        """Load embedding model with fallback to download"""
        try:
            self.embedder = SentenceTransformer(
                EMBED_MODEL_NAME, cache_folder=MODELS_DIR, local_files_only=True
            )
        except Exception as e:
            logger.warning(f"Failed to load embedding model from local cache: {e}")
            logger.info("Downloading embedding model...")
            self.embedder = SentenceTransformer(
                EMBED_MODEL_NAME, cache_folder=MODELS_DIR
            )
            logger.info("Embedding model downloaded successfully")

        self.vector_size = self.embedder.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list):
        """Generate embeddings for a list of texts"""
        # Normalize via SentenceTransformer (already L2/cosine friendly)
        return self.embedder.encode(texts, normalize_embeddings=True).tolist()


class EfficientHybridRetriever:
    def __init__(self, qdrant_client, embedder):
        self.qdrant_client = qdrant_client
        self.embedder = embedder

        # Use small cross-encoder model
        try:
            # MiniLM-based cross-encoder (small and efficient)
            self.cross_encoder = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-2-v2"
            )  # 34MB
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder, will use basic ranking: {e}")
            self.cross_encoder = None

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
        """Perform vector search using Qdrant"""
        # Generate query embedding
        query_vector = self.embedder.embed_texts([query])[0]
        
        # Search in Qdrant
        search_results = self.qdrant_client.search(
            collection_name=COLLECTION,
            query_vector=query_vector,
            limit=top_k,
        )
        
        # Convert results to the expected format
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "modality": result.payload.get("modality", ""),
                "source_file": result.payload.get("source_file", ""),
                "page": result.payload.get("page"),
                "extra": result.payload.get("extra")
            })
            
        return formatted_results

    def _keyword_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Perform keyword search using Qdrant"""
        # For simplicity, we'll use the same Qdrant client but with a different search strategy
        # In a more complex implementation, you might use a separate keyword-based search engine
        try:
            # Use Qdrant's full-text search capability
            search_results = self.qdrant_client.search(
                collection_name=COLLECTION,
                query_filter={
                    "must": [
                        {
                            "key": "text",
                            "match": {
                                "text": query
                            }
                        }
                    ]
                },
                limit=top_k,
            )
            
            # Convert results to the expected format
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "modality": result.payload.get("modality", ""),
                    "source_file": result.payload.get("source_file", ""),
                    "page": result.payload.get("page"),
                    "extra": result.payload.get("extra")
                })
                
            return formatted_results
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _reciprocal_rank_fusion(self, vector_results: List[Dict], keyword_results: List[Dict], top_k: int = 5) -> List[Dict]:
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

    def _cross_encoder_rerank(self, query: str, results: List[Dict], top_k: int = 5) -> List[Dict]:
        """Rerank results using a cross-encoder model"""
        if not self.cross_encoder or not results:
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
        reranked_results = sorted(results, key=lambda x: x["cross_encoder_score"], reverse=True)
        
        return reranked_results[:top_k]


class QdrantProcessor:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.collection = COLLECTION
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists"""
        if self.collection not in [
            c.name for c in self.client.get_collections().collections
        ]:
            # Get vector size from embeddings module
            from knowledge_base.helper_class import EmbeddingProcessor

            embedder = EmbeddingProcessor()
            vector_size = embedder.vector_size

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_chunks(self, chunks: list, vectors: list):
        """Upsert chunks with their vectors into Qdrant"""
        if not chunks:
            return
        points = [
            PointStruct(id=str(uuid.uuid4()), vector=v, payload=c)
            for v, c in zip(vectors, chunks)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list, top_k: int = 5):
        """Search for similar vectors in Qdrant"""
        return self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=min(max(top_k, 1), 50),
        )


class LightweightResponseSynthesizer:
    def __init__(self):
        # Try Phi-3 Mini first (recommended approach), then TinyLlama, then fallback
        models_in_order = [
            (
                "microsoft/Phi-3-mini-4k-instruct",
                "Phi-3 Mini (2.2GB)",
            ),  # 2.2GB - recommended
            (
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                "TinyLlama (1.1GB)",
            ),  # 1.1GB - fallback
            (
                "stabilityai/stablelm-2-zephyr-1_6b",
                "StableLM (1.6GB)",
            ),  # 1.6GB - alternative
        ]

        self.generator = None
        self.model_name = None

        for model_path, model_description in models_in_order:
            try:
                self.generator = pipeline(
                    "text-generation",
                    model=model_path,
                    device=0 if torch.cuda.is_available() else -1,
                    torch_dtype=(
                        torch.float16 if torch.cuda.is_available() else torch.float32
                    ),
                    trust_remote_code=True,  # Some models need this
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

    def synthesize(self, query: str, retrieved_chunks: List[Dict]) -> str:
        if not self.generator:
            # Template-based fallback (no model needed)
            return self._template_based_synthesis(query, retrieved_chunks)

        # Prepare context for small model
        context = self._prepare_compact_context(retrieved_chunks)

        # Create efficient prompt - model-specific formatting
        if "Phi-3" in self.model_name:
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
