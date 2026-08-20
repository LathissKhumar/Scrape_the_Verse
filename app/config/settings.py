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
    OLLAMA_TIMEOUT_SECONDS: float = 120.0

    # Bright Data Settings
    BRIGHTDATA: bool = False
    BRIGHTDATA_API_KEY: Optional[str] = None
    BRIGHTDATA_COLLECTOR_ID: Optional[str] = None
    BRIGHTDATA_DISCOVERY_COLLECTOR_ID: Optional[str] = None
    BRIGHTDATA_COMPANY_COLLECTOR_ID: Optional[str] = None

    # Crawler & Browser Automation Settings
    SCRAPER_PROVIDER: str = "auto"  # "auto", "browser", "local", "brightdata"
    CRAWLER_HEADLESS: bool = True
    CRAWLER_TIMEOUT_MS: int = 30000
    CRAWLER_MAX_CONCURRENCY: int = 10
    CRAWLER_BLOCK_MEDIA: bool = False
    CRAWLER_RECYCLE_PAGES: int = 500

    # Self-Healing & Adaptive Enhancements Settings
    MULTI_PAGE_VALIDATION_ENABLED: bool = True
    MAX_VALIDATION_PAGES: int = 3
    MIN_PAGES_FOR_HIGH_CONFIDENCE: int = 2
    FAILED_REPAIR_TTL_SECONDS: int = 3600
    SEMANTIC_MEMORY_ENABLED: bool = True
    STRUCTURAL_DRIFT_THRESHOLD: float = 0.35
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.65

    # Application Settings
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
