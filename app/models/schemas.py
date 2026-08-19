import re
from typing import Any, Literal, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator


def validate_http_url(url: str) -> str:
    """Validate that a URL has a valid http/https scheme and netloc."""
    trimmed = url.strip()
    if not trimmed:
        raise ValueError("URL cannot be empty")
    parsed = urlparse(trimmed)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Invalid HTTP/HTTPS URL: '{url}'")
    return trimmed


class ScrapingRequest(BaseModel):
    """User input representing a plain-language scraping request."""

    query: str = Field(
        ...,
        min_length=1,
        description="Plain-language description of the scraping objective, requirements, or target URLs.",
    )
    max_records: Optional[int] = Field(
        default=None,
        gt=0,
        description="Optional maximum number of records to scrape.",
    )
    target_urls: list[str] = Field(
        default_factory=list,
        description="Optional list of target HTTP/HTTPS URLs explicitly supplied.",
    )

    @field_validator("target_urls")
    @classmethod
    def validate_target_urls(cls, urls: list[str]) -> list[str]:
        validated = []
        for u in urls:
            validated.append(validate_http_url(u))
        return validated


class ScrapingTask(BaseModel):
    """Structured representation of a validated scraping task."""

    task_id: str = Field(
        ...,
        description="Unique identifier for the task, generated server-side.",
    )
    objective: str = Field(
        ...,
        description="Clear, summarized objective of the scraping job.",
    )
    target_urls: list[str] = Field(
        default_factory=list,
        description="Target URLs to scrape, strictly preserved from user input or query.",
    )
    fields: list[str] = Field(
        default_factory=list,
        description="Extracted field names requested by the user.",
    )
    output_schema: Optional[dict[str, Any]] = Field(
        default=None,
        description="Type mapping or structure for the requested fields (e.g. {'name': 'string'}).",
    )
    max_records: Optional[int] = Field(
        default=None,
        description="Limit on records to scrape if specified.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Explicit constraints mentioned by the user (e.g. pagination limits, exclusions).",
    )
    source_requirements: list[str] = Field(
        default_factory=list,
        description="Explicit source or data requirements (e.g. JavaScript rendering needed, headers).",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary task metadata and execution configuration.",
    )


class ScrapingResult(BaseModel):
    """Canonical result schema of a scraping workflow."""

    task_id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the scraping task.",
    )
    status: Literal["success", "partial", "failed"] = Field(
        ...,
        description="Execution status of the scraping task.",
    )
    records: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Canonical structured records produced by the workflow.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata (timing, attempts, collector info).",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error description if status is failed or partial.",
    )
