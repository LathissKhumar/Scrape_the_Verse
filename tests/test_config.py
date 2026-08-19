import os
import logging
from app.config.settings import Settings, get_settings
from app.config.logging import get_logger, setup_logging, LOG_FORMAT


def test_default_settings():
    settings = Settings()
    assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
    assert settings.OLLAMA_MODEL == "qwen3:8b"
    assert settings.OLLAMA_TIMEOUT_SECONDS == 60.0
    assert settings.BRIGHTDATA_API_KEY is None
    assert settings.BRIGHTDATA_COLLECTOR_ID is None
    assert settings.APP_ENV == "development"
    assert settings.LOG_LEVEL == "INFO"


def test_settings_environment_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:8b-custom")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "30.0")
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "test_key_123")
    monkeypatch.setenv("APP_ENV", "production")

    settings = Settings()
    assert settings.OLLAMA_MODEL == "qwen3:8b-custom"
    assert settings.OLLAMA_TIMEOUT_SECONDS == 30.0
    assert settings.BRIGHTDATA_API_KEY == "test_key_123"
    assert settings.APP_ENV == "production"


def test_logger_setup():
    setup_logging()
    logger = get_logger("PLANNER")
    assert logger.name == "PLANNER"
    assert len(logger.handlers) > 0 or len(logging.getLogger().handlers) > 0
