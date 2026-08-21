"""Bright Data Scraper Studio integration package."""

from app.brightdata.adapter import build_collector_inputs
from app.brightdata.client import BrightDataClient
from app.brightdata.exceptions import (
    BrightDataAuthError,
    BrightDataConfigError,
    BrightDataEmptyResultError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from app.brightdata.jobs import ScraperJobManager, default_job_manager
from app.brightdata.pipeline import BrightDataLeadPipeline
from app.brightdata.registry import (
    ScraperRegistry,
    compute_schema_hash,
    default_scraper_registry,
    normalize_url,
)
from app.brightdata.schemas import (
    CollectorJobRecord,
    CollectorRecord,
    CollectorStatus,
    FieldDefinition,
    ResolveAction,
    ScrapeTargetRequest,
    ScraperHealRequest,
    ScraperHealResponse,
    ScraperResolveResponse,
    ScraperRunRequest,
    ScraperRunResponse,
)
from app.brightdata.service import BrightDataService

__all__ = [
    "BrightDataClient",
    "BrightDataLeadPipeline",
    "BrightDataService",
    "ScraperRegistry",
    "default_scraper_registry",
    "ScraperJobManager",
    "default_job_manager",
    "normalize_url",
    "compute_schema_hash",
    "CollectorStatus",
    "ResolveAction",
    "FieldDefinition",
    "ScrapeTargetRequest",
    "CollectorRecord",
    "CollectorJobRecord",
    "ScraperResolveResponse",
    "ScraperRunRequest",
    "ScraperRunResponse",
    "ScraperHealRequest",
    "ScraperHealResponse",
    "build_collector_inputs",
    "BrightDataError",
    "BrightDataConfigError",
    "BrightDataAuthError",
    "BrightDataJobError",
    "BrightDataTimeoutError",
    "BrightDataEmptyResultError",
]

