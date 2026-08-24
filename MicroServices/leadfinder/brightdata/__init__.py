"""Bright Data Scraper Studio integration package."""

from leadfinder.brightdata.adapter import build_collector_inputs
from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.exceptions import (
    BrightDataAuthError,
    BrightDataConfigError,
    BrightDataEmptyResultError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from leadfinder.brightdata.jobs import ScraperJobManager, default_job_manager
from leadfinder.brightdata.pipeline import BrightDataLeadPipeline
from leadfinder.brightdata.registry import (
    ScraperRegistry,
    compute_schema_hash,
    default_scraper_registry,
    normalize_url,
)
from leadfinder.brightdata.schemas import (
    CollectorJobRecord,
    CollectorRecord,
    CollectorStatus,
    FieldDefinition,
    ResolveAction,
    ScraperHealRequest,
    ScraperHealResponse,
    ScraperResolveResponse,
    ScraperRunRequest,
    ScraperRunResponse,
    ScrapeTargetRequest,
)
from leadfinder.brightdata.service import BrightDataService

__all__ = [
    "BrightDataAuthError",
    "BrightDataClient",
    "BrightDataConfigError",
    "BrightDataEmptyResultError",
    "BrightDataError",
    "BrightDataJobError",
    "BrightDataLeadPipeline",
    "BrightDataService",
    "BrightDataTimeoutError",
    "CollectorJobRecord",
    "CollectorRecord",
    "CollectorStatus",
    "FieldDefinition",
    "ResolveAction",
    "ScrapeTargetRequest",
    "ScraperHealRequest",
    "ScraperHealResponse",
    "ScraperJobManager",
    "ScraperRegistry",
    "ScraperResolveResponse",
    "ScraperRunRequest",
    "ScraperRunResponse",
    "build_collector_inputs",
    "compute_schema_hash",
    "default_job_manager",
    "default_scraper_registry",
    "normalize_url",
]
