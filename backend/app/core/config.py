from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration sourced from the backend .env file and environment."""

    app_name: str = "TalentLens AI"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:change-me@localhost:5432/resume_screening"
    frontend_origin: str = "http://localhost:5173"

    # --- AI layer (Sentence Transformers + LLM) ---
    # Embeddings are attempted whenever enabled; if the model cannot be loaded
    # (no internet access, dependency missing, etc.) services fall back to a
    # deterministic lexical baseline automatically.
    enable_embeddings: bool = True
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM extraction/explanation is off by default so the deterministic
    # baseline remains the out-of-the-box behaviour. Set
    # ENABLE_LLM_EXTRACTION=true and GROQ_API_KEY once you want to turn
    # it on; see console.groq.com for available model names.
    enable_llm_extraction: bool = False
    groq_api_key: str | None = None
    llm_model: str = "openai/gpt-oss-120b"

    # --- Authentication ---
    # In production, set JWT_SECRET_KEY to a long random value via the
    # environment -- never rely on the default outside local development.
    jwt_secret_key: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
