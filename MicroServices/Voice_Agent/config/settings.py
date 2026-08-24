"""
Voice Agent Configuration & Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VoiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_SECRET_KEY: str | None = None

    VOICE_AGENT_PORT: int = 8084
    LEAD_MANAGER_API_PORT: int = 8082
    SDR_API_PORT: int = 8081

    LEAD_MANAGER_URL: str = "http://127.0.0.1:8082"
    VOICE_PUBLIC_BASE_URL: str = "http://localhost:8084"

    # Twilio Telephony Credentials
    TWILIO_ACCOUNT_SID: str | None = None  # ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_API_KEY_SID: str | None = None  # SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_API_KEY_SECRET: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None
    PERSONAL_MOBILE_NUMBER: str | None = None

    # Audio & Voice Engines
    VOICE_TTS_VOICE: str = "en-US-JennyNeural"
    VOICE_VAD_THRESHOLD: int = 450
    VOICE_BARGE_IN_ENABLED: bool = True
    VOICE_SAMPLE_RATE: int = 8000

    # Local LLM Brain
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"


def get_voice_settings() -> VoiceSettings:
    return VoiceSettings()
