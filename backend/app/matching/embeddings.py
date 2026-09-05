"""Semantic similarity via Sentence Transformers, with a safe fallback."""

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
                self._load_failed = True
                return None
        return self._model

    def similarity(self, text_a: str, text_b: str) -> float | None:
        """Cosine similarity between two texts, rescaled to 0-100."""
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
            return max(0.0, min(100.0, (cosine + 1) / 2 * 100))
        except Exception:
            self._load_failed = True
            return None


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Process-wide singleton so the model is loaded at most once."""
    settings = get_settings()
    return EmbeddingProvider(model_name=settings.embedding_model_name, enabled=settings.enable_embeddings)
