"""Configuration for browser execution layer."""

from typing import Optional
from pydantic import BaseModel, Field


class CrawlerConfig(BaseModel):
    """Configuration for Playwright browser crawler."""
    headless: bool = Field(default=True, description="Run Chromium in headless mode")
    timeout_ms: int = Field(default=30000, description="Global page navigation timeout in milliseconds")
    viewport_width: int = Field(default=1920)
    viewport_height: int = Field(default=1080)
    user_agent: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    )
    locale: str = Field(default="en-US")
    timezone_id: str = Field(default="America/New_York")
    allow_private_ips: bool = Field(default=False)
    rate_limit_rps: float = Field(default=2.0)
    circuit_breaker_threshold: int = Field(default=3)
    max_concurrency: int = Field(default=10, description="Max concurrent browser tabs/contexts")
    block_media: bool = Field(default=False, description="Block heavy media assets (images/video/fonts) during crawl")
    recycle_after_pages: int = Field(default=500, description="Recycle browser instance after processing N pages")
