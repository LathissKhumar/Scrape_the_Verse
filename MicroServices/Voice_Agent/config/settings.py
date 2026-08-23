"""
Voice Agent Configuration & Settings.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class VoiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_SECRET_KEY: Optional[str] = None

    VOICE_AGENT_PORT: int = 8084
    LEAD_MANAGER_API_PORT: int = 8082
    SDR_API_PORT: int = 8081

    LEAD_MANAGER_URL: str = "http://127.0.0.1:8082"
    VOICE_PUBLIC_BASE_URL: str = "http://localhost:8084"

    # Twilio Telephony Credentials
    TWILIO_ACCOUNT_SID: Optional[str] = None  # ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_API_KEY_SID: Optional[str] = None  # SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_API_KEY_SECRET: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    PERSONAL_MOBILE_NUMBER: Optional[str] = None

    # Audio & Voice Engines
    VOICE_TTS_VOICE: str = "en-US-JennyNeural"
    VOICE_VAD_THRESHOLD: int = 450
    VOICE_BARGE_IN_ENABLED: bool = True
    VOICE_SAMPLE_RATE: int = 8000

    # Local LLM Brain
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"


def get_voice_settings() -> VoiceSettings:
    return VoiceSettings()
