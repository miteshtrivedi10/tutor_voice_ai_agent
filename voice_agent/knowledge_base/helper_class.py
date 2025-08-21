from typing import Dict, List


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
            print(f"Failed to load embedding model from local cache: {e}")
            print("Downloading embedding model...")
            self.embedder = SentenceTransformer(
                EMBED_MODEL_NAME, cache_folder=MODELS_DIR
            )
            print("Embedding model downloaded successfully")

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
            print(f"Failed to load cross-encoder, will use basic ranking: {e}")
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
            from src.core.embeddings import EmbeddingProcessor

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
                print(f"Successfully loaded {model_description}")
                break
            except Exception as e:
                print(f"Failed to load {model_description}: {e}")
                continue

        if self.generator:
            print(f"Using {self.model_name} for response synthesis")
        else:
            print("Falling back to template-based approach")

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
                return generated_text.strip()
        except Exception as e:
            print(f"Generation failed, falling back to template: {e}")
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
