from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration sourced from the backend .env file and environment."""

    app_name: str = "TalentLens AI"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:change-me@localhost:5432/resume_screening"
    frontend_origin: str = "http://localhost:5173"

    # --- AI layer (Sentence Transformers + LLM) ---
    enable_embeddings: bool = True
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    enable_llm_extraction: bool = False
    groq_api_key: str | None = None
    llm_model: str = "openai/gpt-oss-120b"

    # Gemini AI Resume Agent settings
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    # --- Authentication ---
    jwt_secret_key: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
