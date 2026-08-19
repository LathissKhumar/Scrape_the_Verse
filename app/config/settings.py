from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama Local LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0

    # Bright Data Settings (Optional for Phase 1)
    BRIGHTDATA_API_KEY: Optional[str] = None
    BRIGHTDATA_COLLECTOR_ID: Optional[str] = None

    # Application Settings
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
