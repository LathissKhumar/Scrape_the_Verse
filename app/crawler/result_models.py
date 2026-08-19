"""Result models and block classification types for web crawling."""

from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    """Categorized types of access denials, rate limits, and challenge blocks."""
    NONE = "NONE"
    RATE_LIMITED = "RATE_LIMITED"
    ACCESS_DENIED = "ACCESS_DENIED"
    CAPTCHA = "CAPTCHA"
    SECURITY_CHALLENGE = "SECURITY_CHALLENGE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    ROBOTS_RESTRICTED = "ROBOTS_RESTRICTED"
    UNKNOWN = "UNKNOWN"


class CrawlResult(BaseModel):
    """Structured crawl result produced by browser execution."""
    url: str
    final_url: Optional[str] = None
    status_code: int = 200
    html: str = ""
    markdown: Optional[str] = None
    blocked: bool = False
    block_type: BlockType = BlockType.NONE
    error: Optional[str] = None
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    timing_ms: float = 0.0
    extracted_data: Optional[Dict[str, Any]] = None

    @property
    def success(self) -> bool:
        """True if crawl completed with 2xx status, content present, and no block detected."""
        return not self.blocked and 200 <= self.status_code < 400 and bool(self.html.strip())
