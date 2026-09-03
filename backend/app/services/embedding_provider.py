"""Semantic similarity via Sentence Transformers, with a safe fallback.

Module 3 of the plan calls for embeddings-based semantic matching rather
than plain keyword overlap. Loading a transformer model requires downloading
weights and adds real latency, so this provider is deliberately lazy (the
model loads on first use, not at import time) and deliberately fault
tolerant (if the model can't be loaded -- no internet access, dependency not
installed, first-run download failure -- callers get `None` back instead of
an exception, and the caller decides on a lexical fallback).

This keeps Module 3's response contract stable regardless of whether the AI
layer is available in a given environment.
"""

from functools import lru_cache

from app.core.config import get_settings


class EmbeddingProvider:
    """Wraps a Sentence Transformers model to score semantic similarity."""

    def __init__(self, model_name: str, enabled: bool = True):
        self.model_name = model_name
        self.enabled = enabled
        self._model = None
        self._load_failed = False

    @property
    def is_ready(self) -> bool:
        """Whether embeddings are usable right now, without forcing a load."""
        return self.enabled and not self._load_failed

    def _get_model(self):
        if not self.enabled or self._load_failed:
            return None
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            except Exception:
                # Missing dependency, no network access to fetch weights,
                # corrupt cache, etc. Any of these should degrade quietly.
                self._load_failed = True
                return None
        return self._model

    def similarity(self, text_a: str, text_b: str) -> float | None:
        """Cosine similarity between two texts, rescaled to 0-100.

        Returns None (rather than raising) when embeddings are unavailable,
        so callers can fall back to a lexical scoring method.
        """
        if not text_a.strip() or not text_b.strip():
            return None
        model = self._get_model()
        if model is None:
            return None
        try:
            import numpy as np

            embeddings = model.encode([text_a, text_b])
            vector_a, vector_b = embeddings[0], embeddings[1]
            denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
            if denominator == 0:
                return None
            cosine = float(np.dot(vector_a, vector_b) / denominator)
            # Cosine similarity is in [-1, 1]; rescale to a 0-100 score.
            return max(0.0, min(100.0, (cosine + 1) / 2 * 100))
        except Exception:
            self._load_failed = True
            return None


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Process-wide singleton so the model is loaded at most once."""
    settings = get_settings()
    return EmbeddingProvider(model_name=settings.embedding_model_name, enabled=settings.enable_embeddings)
