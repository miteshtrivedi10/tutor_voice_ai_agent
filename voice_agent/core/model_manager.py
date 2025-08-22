#!/usr/bin/env python3
"""
Model Manager for efficient model loading and memory management
"""

import os
import gc
import time
import weakref
from typing import Any, Dict, Optional
from config.logging_config import logger
from config.settings import MODELS_DIR


class ModelManager:
    """
    Manages model loading with caching to prevent memory issues.
    Uses a singleton pattern to ensure only one instance exists.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization
        if self._initialized:
            return

        self._models: Dict[str, Any] = {}
        self._model_refs: Dict[str, weakref.ref] = {}
        self._initialized = True
        logger.info("ModelManager initialized")

    def get_model(self, model_name: str, model_factory_func, *args, **kwargs):
        """
        Get a model by name, loading it if necessary.
        Uses weak references to allow garbage collection when memory is low.
        """
        # Check if model is already loaded
        if model_name in self._models:
            model = self._models[model_name]
            # Verify the model is still valid
            if model is not None:
                logger.debug(f"Returning cached model: {model_name}")
                return model

        # Load the model
        logger.info(f"Loading model: {model_name}")
        try:
            model = model_factory_func(*args, **kwargs)
            self._models[model_name] = model

            # Create a weak reference for memory monitoring
            self._model_refs[model_name] = weakref.ref(
                model, self._model_cleanup_callback
            )

            logger.info(f"Model {model_name} loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def _model_cleanup_callback(self, weakref_obj):
        """Callback when a model is garbage collected"""
        # Find and remove the model from our cache
        for model_name, ref in list(self._model_refs.items()):
            if ref is weakref_obj:
                logger.info(f"Model {model_name} garbage collected")
                self._models.pop(model_name, None)
                self._model_refs.pop(model_name, None)
                break

    def unload_model(self, model_name: str):
        """Explicitly unload a model to free memory"""
        if model_name in self._models:
            logger.info(f"Unloading model: {model_name}")
            self._models.pop(model_name, None)
            self._model_refs.pop(model_name, None)
            # Force garbage collection
            gc.collect()

    def unload_all_models(self):
        """Unload all models to free memory"""
        logger.info("Unloading all models")
        self._models.clear()
        self._model_refs.clear()
        gc.collect()

    def get_model_stats(self):
        """Get statistics about loaded models"""
        return {
            "loaded_models": list(self._models.keys()),
            "model_count": len(self._models),
        }


# Global model manager instance
model_manager = ModelManager()


def get_embedding_processor():
    """Get or load the embedding processor"""
    from search.helper_class import EmbeddingProcessor

    return model_manager.get_model("embedding_processor", EmbeddingProcessor)


def get_cross_encoder():
    """Get or load the cross-encoder model"""
    from sentence_transformers.cross_encoder import CrossEncoder

    def _load_cross_encoder():
        return CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-2-v2",
            cache_folder=MODELS_DIR,
            local_files_only=True,
        )

    return model_manager.get_model("cross_encoder", _load_cross_encoder)


def get_response_synthesizer():
    """Get or load the response synthesizer"""
    from search.helper_class import LightweightResponseSynthesizer

    return model_manager.get_model(
        "response_synthesizer", LightweightResponseSynthesizer
    )


def unload_all_models():
    """Unload all models to free memory"""
    model_manager.unload_all_models()



