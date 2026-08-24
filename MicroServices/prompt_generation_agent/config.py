from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    seo_report_dir: str = (
        r"C:\Users\msuke\Documents\Scrape_the_Verse\MicroServices\SDR\seo\report"
    )
    business_report_dir: str = (
        r"C:\Users\msuke\Documents\Scrape_the_Verse\business_analysis_agent\outputs"
    )
    output_dir: str = r"C:\Users\msuke\Documents\Scrape_the_Verse\MicroServices\prompt_generation_agent\outputs"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
