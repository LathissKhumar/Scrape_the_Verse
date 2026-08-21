"""High-Level Service and Scraper Orchestrator for Bright Data Scraper Studio execution."""

import time
from typing import Any, Optional
from uuid import uuid4

from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.jobs import ScraperJobManager, default_job_manager
from leadfinder.brightdata.pipeline import BrightDataLeadPipeline
from leadfinder.brightdata.registry import (
    ScraperRegistry,
    compute_schema_hash,
    default_scraper_registry,
    normalize_url,
)
from leadfinder.brightdata.schemas import (
    CollectorRecord,
    CollectorStatus,
    FieldDefinition,
    ResolveAction,
    ScrapeTargetRequest,
    ScraperHealResponse,
    ScraperResolveResponse,
    ScraperRunResponse,
)
from leadfinder.config.logging import get_logger
from leadfinder.config.settings import Settings, get_settings
from leadfinder.models.schemas import ScrapingResult, ScrapingTask

logger = get_logger("BRIGHTDATA_SERVICE")


class BrightDataService:
    """High-Level Service and Orchestrator for Bright Data Scraper Studio.

    Orchestrates collector resolution (reuse vs dynamic creation), background job tracking,
    fast-path execution, chained lead generation, and self-healing.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        client: Optional[BrightDataClient] = None,
        pipeline: Optional[BrightDataLeadPipeline] = None,
        registry: Optional[ScraperRegistry] = None,
        jobs: Optional[ScraperJobManager] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self.client = client or BrightDataClient(settings=self._settings)
        self.pipeline = pipeline or BrightDataLeadPipeline(client=self.client, settings=self._settings)
        self.registry = registry or default_scraper_registry
        self.jobs = jobs or default_job_manager

    @property
    def is_enabled(self) -> bool:
        """Return True if Bright Data mode is active and properly configured."""
        return bool(self._settings.BRIGHTDATA and self.client.is_configured)

    @staticmethod
    def _build_extraction_description(
        description: str,
        fields: list[FieldDefinition],
    ) -> str:
        """Construct a structured extraction prompt for Bright Data Scraper Studio CLI."""
        parts: list[str] = []
        if description.strip():
            parts.append(description.strip())

        if fields:
            field_lines = [f"- {f.name}: {f.description}" if f.description else f"- {f.name}" for f in fields]
            parts.append("Extract the following fields:\n" + "\n".join(field_lines))

        return "\n\n".join(parts) if parts else "Extract structured records from this page."

    async def resolve_scraper(self, request: ScrapeTargetRequest) -> ScraperResolveResponse:
        """Determine whether to reuse an existing collector or initiate asynchronous creation.

        Idempotent: Identical requests with in-flight creation jobs reuse the existing job.
        """
        norm_url = normalize_url(request.url)
        s_hash = compute_schema_hash(norm_url, request.fields)

        logger.info(f"SCRAPER_LOOKUP target_url='{norm_url}' schema_hash='{s_hash}'")
        existing: Optional[CollectorRecord] = self.registry.find_compatible(norm_url, s_hash)

        # 1. Fast Path: Compatible ready collector exists
        if existing and existing.status == CollectorStatus.READY and existing.collector_id:
            logger.info(
                f"SCRAPER_REUSED scraper_id={existing.id} collector_id={existing.collector_id} target='{norm_url}'"
            )
            return ScraperResolveResponse(
                action=ResolveAction.REUSE.value,
                status="ready",
                collector_id=existing.collector_id,
                scraper_id=existing.id,
            )

        # 2. In-Flight: Creation is already underway for this schema
        if existing and existing.status in (CollectorStatus.CREATING, CollectorStatus.RUNNING, CollectorStatus.HEALING):
            active_job = self.jobs.find_active_job_for_scraper(existing.id)
            job_id = active_job.job_id if active_job else f"job_{existing.id}"
            logger.info(
                f"SCRAPER_CREATION_IN_PROGRESS scraper_id={existing.id} job_id={job_id} target='{norm_url}'"
            )
            return ScraperResolveResponse(
                action=ResolveAction.CREATE.value,
                status="creating",
                job_id=job_id,
                scraper_id=existing.id,
            )

        # 3. Creation Path: No compatible collector exists; initiate new creation
        record = self.registry.create_record(
            target_url=request.url,
            fields=request.fields,
            description=request.description,
        )
        job = self.jobs.create_job(scraper_id=record.id)
        extraction_desc = self._build_extraction_description(request.description, request.fields)

        self.jobs.start_creation_worker(
            job_id=job.job_id,
            scraper_id=record.id,
            create_coro_factory=lambda: self.client.create_scraper(
                url=request.url,
                extraction_description=extraction_desc,
            ),
        )

        logger.info(
            f"SCRAPER_CREATION_STARTED scraper_id={record.id} job_id={job.job_id} target='{norm_url}'"
        )
        return ScraperResolveResponse(
            action=ResolveAction.CREATE.value,
            status="creating",
            job_id=job.job_id,
            scraper_id=record.id,
        )

    async def run_collector(
        self,
        collector_id: str,
        url: str,
        timeout_seconds: float = 120.0,
    ) -> ScraperRunResponse:
        """Run a ready Bright Data Collector against the specified target URL."""
        start_time = time.time()
        logger.info(f"COLLECTOR_RUN_STARTED collector_id={collector_id} url='{url}'")

        try:
            records = await self.client.run_scraper(
                collector_id=collector_id,
                url=url,
                timeout_seconds=timeout_seconds,
            )
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            self.registry.update_run_metadata(
                collector_id=collector_id,
                last_run_status="success",
            )
            logger.info(
                f"COLLECTOR_RUN_COMPLETED collector_id={collector_id} records={len(records)} elapsed_ms={elapsed_ms}"
            )
            return ScraperRunResponse(
                collector_id=collector_id,
                status="success",
                data=records,
                elapsed_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            err_msg = str(exc)
            self.registry.update_run_metadata(
                collector_id=collector_id,
                last_run_status="failed",
                error=err_msg,
            )
            logger.error(
                f"COLLECTOR_RUN_FAILED collector_id={collector_id} error={err_msg} elapsed_ms={elapsed_ms}"
            )
            return ScraperRunResponse(
                collector_id=collector_id,
                status="failed",
                data=[],
                error=err_msg,
                elapsed_ms=elapsed_ms,
            )

    async def heal_collector(
        self,
        collector_id: str,
        failure_description: str,
    ) -> ScraperHealResponse:
        """Trigger self-healing for an unhealthy or broken collector."""
        logger.info(f"COLLECTOR_HEAL_STARTED collector_id={collector_id} issue='{failure_description}'")

        rec = self.registry.get_record_by_collector_id(collector_id)
        if rec:
            self.registry.update_status(record_id=rec.id, status=CollectorStatus.HEALING)

        try:
            res = await self.client.heal_scraper(
                collector_id=collector_id,
                failure_description=failure_description,
            )
            if rec:
                self.registry.update_status(record_id=rec.id, status=CollectorStatus.READY)

            logger.info(f"COLLECTOR_HEAL_COMPLETED collector_id={collector_id}")
            return ScraperHealResponse(
                collector_id=collector_id,
                status="ready",
                message=res.get("message", "Collector healed successfully."),
            )
        except Exception as exc:
            err_msg = str(exc)
            if rec:
                self.registry.update_status(
                    record_id=rec.id,
                    status=CollectorStatus.UNHEALTHY,
                    error=err_msg,
                )
            logger.error(f"COLLECTOR_HEAL_FAILED collector_id={collector_id} error={err_msg}")
            return ScraperHealResponse(
                collector_id=collector_id,
                status="failed",
                message="Collector healing failed.",
                error=err_msg,
            )

    async def execute_task(self, task: ScrapingTask) -> ScrapingResult:
        """Fast-path execution of a ScrapingTask using Bright Data Scraper Studio."""
        task_id = task.task_id or str(uuid4())
        start_time = time.time()
        logger.info(f"task_id={task_id} Executing fast-path Bright Data scraping for {len(task.target_urls)} URL(s)")

        if not task.target_urls:
            return ScrapingResult(
                task_id=task_id,
                status="failed",
                records=[],
                metadata={"task_id": task_id, "record_count": 0, "scraper_provider": "brightdata"},
                error="No target URLs provided in ScrapingTask.",
            )

        all_records: list[dict[str, Any]] = []
        errors: list[str] = []

        for url in task.target_urls:
            try:
                if "search" in url.lower() or "ss=" in url.lower() or "/impcat/" in url.lower():
                    records = await self.pipeline.run_discovery(url)
                elif "profile" in url.lower() or "aboutus" in url.lower():
                    record = await self.pipeline.enrich_company(url)
                    records = [record] if record else []
                else:
                    records = await self.pipeline.run_discovery(url)

                all_records.extend(records)
            except Exception as error:
                logger.error(f"task_id={task_id} Error scraping '{url}' via Bright Data: {error}")
                errors.append(f"{url}: {str(error)}")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        status_str = "success" if all_records else ("failed" if errors else "empty")

        logger.info(
            f"task_id={task_id} Bright Data fast-path completed in {elapsed_ms}ms | records={len(all_records)} | status={status_str}"
        )

        return ScrapingResult(
            task_id=task_id,
            status=status_str,
            records=all_records,
            metadata={
                "task_id": task_id,
                "record_count": len(all_records),
                "scraper_provider": "brightdata",
                "elapsed_ms": elapsed_ms,
                "discovery_collector_id": self.pipeline.discovery_collector_id,
                "company_collector_id": self.pipeline.company_collector_id,
            },
            error="; ".join(errors) if errors and not all_records else None,
        )

    async def generate_leads(
        self,
        query: str,
        enrich_profiles: bool = True,
        max_concurrency: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate complete B2B leads by searching and enriching company profiles."""
        return await self.pipeline.generate_leads(
            query_or_url=query,
            enrich_profiles=enrich_profiles,
            max_concurrency=max_concurrency,
        )

    async def get_company_profile(self, company_url: str) -> dict[str, Any]:
        """Perform a direct lookup for a single company profile/catalog URL."""
        return await self.pipeline.enrich_company(company_url)

