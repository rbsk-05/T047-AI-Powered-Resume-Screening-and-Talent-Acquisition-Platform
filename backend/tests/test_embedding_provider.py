from app.services.embedding_provider import EmbeddingProvider


def test_disabled_provider_returns_none() -> None:
    provider = EmbeddingProvider(model_name="does-not-matter", enabled=False)

    assert provider.similarity("backend developer python", "python engineer") is None


def test_model_load_failure_degrades_to_none_without_raising(monkeypatch) -> None:
    # Forces the same failure path a fresh install without
    # `sentence-transformers`, or no internet access to fetch weights, would
    # hit -- regardless of whether the real package happens to be installed
    # in whatever environment runs this test.
    provider = EmbeddingProvider(model_name="sentence-transformers/all-MiniLM-L6-v2", enabled=True)
    monkeypatch.setattr(provider, "_get_model", lambda: None)

    result = provider.similarity("backend developer python", "python engineer")

    assert result is None


def test_blank_text_returns_none() -> None:
    provider = EmbeddingProvider(model_name="does-not-matter", enabled=True)

    assert provider.similarity("", "python engineer") is None


class _FakeModel:
    """Stands in for a loaded SentenceTransformer for scoring-logic tests."""

    def __init__(self, vectors: dict[str, list[float]]):
        self._vectors = vectors

    def encode(self, texts: list[str]):
        return [self._vectors[text] for text in texts]


def test_identical_vectors_score_near_one_hundred(monkeypatch) -> None:
    provider = EmbeddingProvider(model_name="does-not-matter", enabled=True)
    fake_model = _FakeModel({"a": [1.0, 0.0], "b": [1.0, 0.0]})
    monkeypatch.setattr(provider, "_get_model", lambda: fake_model)

    assert provider.similarity("a", "b") == 100.0


def test_opposite_vectors_score_near_zero(monkeypatch) -> None:
    provider = EmbeddingProvider(model_name="does-not-matter", enabled=True)
    fake_model = _FakeModel({"a": [1.0, 0.0], "b": [-1.0, 0.0]})
    monkeypatch.setattr(provider, "_get_model", lambda: fake_model)

    assert provider.similarity("a", "b") == 0.0
