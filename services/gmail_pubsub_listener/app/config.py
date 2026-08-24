"""Configuration settings for the Communication Service."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_service_dir, ".env")


class Settings(BaseSettings):
    # Server settings
    PORT: int = 8083
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Gmail credentials
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""

    # OAuth fallback credentials
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REFRESH_TOKEN: str | None = None

    # IMAP settings
    IMAP_SERVER: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    IMAP_USE_SSL: bool = True
    IMAP_MAILBOX: str = "INBOX"
    IDLE_DURATION_SECONDS: int = 1500  # 25 minutes (recommended max is 29 mins)
    INITIAL_SYNC_MESSAGES: int = 50

    # SMTP settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USE_SSL: bool = True

    # Database
    DATABASE_PATH: str = os.path.join(_service_dir, "communication.db")

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"

    # Auto-Reply Engine
    AUTO_REPLY_ENABLED: bool = True

    # Downstream Microservices
    LEAD_MANAGER_URL: str = "http://localhost:8082"
    SDR_SERVICE_URL: str = "http://localhost:8084"

    model_config = SettingsConfigDict(
        env_file=(_env_path, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
