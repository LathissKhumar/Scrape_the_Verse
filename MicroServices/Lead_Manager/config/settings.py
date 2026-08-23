"""
Lead Manager Configuration & Settings.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_SECRET_KEY: Optional[str] = None

    LEAD_MANAGER_API_PORT: int = 8082
    SDR_API_PORT: int = 8081
    LEADFINDER_API_PORT: int = 8000
    UI_FRONTEND_PORT: int = 3000

    LEAD_MANAGER_DB_PATH: str = ".lead_manager.sqlite"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_TIMEOUT_SECONDS: float = 120.0

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    FOLLOWUP_CHECK_INTERVAL_SECONDS: int = 3600
    STALE_LEAD_DAYS_CONTACTED: int = 3
    STALE_LEAD_DAYS_ENGAGED: int = 2
    STALE_LEAD_DAYS_PROPOSAL_READY: int = 2

    # Twenty CRM Integration
    TWENTY_CRM_ENABLED: bool = True
    TWENTY_CRM_BASE_URL: str = "http://localhost:3000"
    TWENTY_CRM_API_KEY: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
