"""Pydantic schemas and enums for Bright Data dynamic collector management."""

import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CollectorStatus(str, Enum):
    """Lifecycle status of a Bright Data Scraper Studio collector."""

    CREATING = "CREATING"
    READY = "READY"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    UNHEALTHY = "UNHEALTHY"
    HEALING = "HEALING"


class ResolveAction(str, Enum):
    """Action returned by the Scraper Orchestrator."""

    REUSE = "reuse"
    CREATE = "create"


class FieldDefinition(BaseModel):
    """Schema definition for a requested extraction field."""

    name: str = Field(..., description="Target field name")
    description: str | None = Field(
        default="", description="Description of the field to extract"
    )


class ScrapeTargetRequest(BaseModel):
    """User request specifying target URL, extraction description, and requested fields."""

    url: str = Field(..., description="Target website or page URL to scrape")
    description: str = Field(
        default="", description="High-level extraction instructions or objective"
    )
    fields: list[FieldDefinition] = Field(
        default_factory=list,
        description="Structured list of field names and descriptions to extract",
    )


class CollectorRecord(BaseModel):
    """Registry record tracking a Bright Data Scraper Studio Collector."""

    id: str = Field(
        ..., description="Internal unique registry identifier for the scraper"
    )
    collector_id: str | None = Field(
        default=None,
        description="Bright Data Collector ID (e.g. c_xxxxxx)",
    )
    target_url: str = Field(..., description="Original requested target URL")
    normalized_url: str = Field(
        ..., description="Normalized target URL used for matching"
    )
    extraction_schema: list[dict[str, str]] = Field(
        default_factory=list,
        description="Canonical list of field definitions",
    )
    schema_hash: str = Field(
        ..., description="Deterministic SHA-256 fingerprint of target URL + fields"
    )
    description: str = Field(
        default="", description="Extraction description provided during creation"
    )
    status: CollectorStatus = Field(
        default=CollectorStatus.CREATING,
        description="Current lifecycle status of the collector",
    )
    created_at: float = Field(
        default_factory=time.time, description="Creation timestamp in epoch seconds"
    )
    updated_at: float = Field(
        default_factory=time.time, description="Last update timestamp in epoch seconds"
    )
    last_used_at: float | None = Field(
        default=None, description="Timestamp when collector was last executed"
    )
    last_run_status: str | None = Field(
        default=None, description="Status of last execution (e.g. success, failed)"
    )
    last_error: str | None = Field(
        default=None, description="Error message from last failure if any"
    )


class CollectorJobRecord(BaseModel):
    """Record tracking an asynchronous background scraper creation job."""

    job_id: str = Field(..., description="Unique background job identifier")
    scraper_id: str = Field(
        ..., description="Internal registry ID of the associated scraper"
    )
    status: CollectorStatus = Field(
        default=CollectorStatus.CREATING,
        description="Current execution status of the creation job",
    )
    collector_id: str | None = Field(
        default=None,
        description="Generated Bright Data collector ID once ready",
    )
    error: str | None = Field(
        default=None, description="Error message if creation failed"
    )
    created_at: float = Field(
        default_factory=time.time, description="Job submission timestamp"
    )
    updated_at: float = Field(
        default_factory=time.time, description="Job update timestamp"
    )


class ScraperResolveResponse(BaseModel):
    """Response returned when resolving a scraping target against the registry."""

    action: str = Field(..., description="'reuse' or 'create'")
    status: str = Field(..., description="Current status: 'ready', 'creating', etc.")
    collector_id: str | None = Field(
        default=None, description="Bright Data Collector ID if ready"
    )
    job_id: str | None = Field(
        default=None, description="Background job ID if creation in progress"
    )
    scraper_id: str | None = Field(
        default=None, description="Internal scraper registry ID"
    )


class ScraperRunRequest(BaseModel):
    """Request payload to execute a ready Bright Data Collector."""

    collector_id: str = Field(..., description="Bright Data collector ID (c_xxxxxx)")
    url: str = Field(..., description="Target URL to run collector against")
    timeout_seconds: float | None = Field(
        default=120.0, description="Max execution timeout in seconds"
    )


class ScraperRunResponse(BaseModel):
    """Result payload from running a Bright Data Collector."""

    collector_id: str = Field(..., description="Bright Data collector ID")
    status: str = Field(..., description="Execution status: 'success' or 'failed'")
    data: list[dict[str, Any]] = Field(
        default_factory=list, description="Extracted records"
    )
    error: str | None = Field(
        default=None, description="Error details if execution failed"
    )
    elapsed_ms: float | None = Field(
        default=None, description="Execution elapsed time in milliseconds"
    )


class ScraperHealRequest(BaseModel):
    """Request payload to heal a broken Bright Data Collector."""

    collector_id: str = Field(..., description="Bright Data collector ID")
    failure_description: str = Field(
        ..., description="Explanation of what broke or needs repair"
    )
    url: str | None = Field(default=None, description="Optional target URL context")


class ScraperHealResponse(BaseModel):
    """Result payload from collector healing."""

    collector_id: str = Field(..., description="Bright Data collector ID")
    status: str = Field(..., description="Healing status: 'ready', 'healing', 'failed'")
    message: str = Field(..., description="Outcome message")
    error: str | None = Field(
        default=None, description="Error message if healing failed"
    )
