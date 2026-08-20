"""Repair evidence collector acquiring fresh page snapshots and testing transient recovery."""

from typing import Any, Optional
from bs4 import BeautifulSoup
from app.config.logging import get_logger
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionSchema, RawPage
from app.models.schemas import ScrapingTask
from app.validation.engine import ValidationEngine
from app.validation.schemas import ValidationResult

logger = get_logger("REPAIR_EVIDENCE")


class RepairEvidenceCollector:
    """Acquires fresh current-page snapshots via the active scraper provider to discover layout changes and verify transient recovery."""

    def __init__(
        self,
        scraper_agent: Optional[Any] = None,
        extraction_engine: Optional[ExtractionEngine] = None,
        validation_engine: Optional[ValidationEngine] = None,
    ) -> None:
        self.scraper_agent = scraper_agent
        self.extraction_engine = extraction_engine
        self.validation_engine = validation_engine

    async def collect_fresh_pages(self, task: ScrapingTask) -> list[RawPage]:
        """Fetch fresh live/canary page records using the configured scraper provider."""
        if not self.scraper_agent:
            logger.warning("No scraper agent configured for RepairEvidenceCollector")
            return []

        logger.debug(f"Fetching fresh page evidence for task_id={task.task_id} from {task.target_urls}")
        try:
            raw_dicts = await self.scraper_agent.execute(task=task)
            raw_pages: list[RawPage] = []
            for item in raw_dicts:
                if isinstance(item, dict):
                    raw_pages.append(RawPage(**item))
                elif isinstance(item, RawPage):
                    raw_pages.append(item)
            return raw_pages
        except Exception as error:
            logger.warning(f"Failed to fetch fresh page evidence for task {task.task_id}: {error}")
            return []

    async def check_transient_recovery(
        self,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> tuple[list[RawPage], bool, Optional[ValidationResult]]:
        """Fetch a fresh scrape and verify if the original configuration unexpectedly produces a healthy result (transient glitch)."""
        raw_pages = await self.collect_fresh_pages(task=task)
        if not raw_pages:
            return [], False, None

        if not self.extraction_engine or not self.validation_engine or not schema:
            return raw_pages, False, None

        try:
            # Attempt extraction on fresh page with current schema
            raw_dicts = [p.model_dump() for p in raw_pages]
            ext_call = self.extraction_engine.extract(raw_results=raw_dicts, task=task, schema=schema)
            ext_result = await ext_call if hasattr(ext_call, "__await__") else ext_call
            records = ext_result.records

            # Validate extraction
            val_call = self.validation_engine.validate(
                extracted_results=records,
                task=task,
                raw_results=raw_dicts,
            )
            val_res = await val_call if hasattr(val_call, "__await__") else val_call

            if val_res.status == "healthy" and val_res.health_score >= 0.80:
                logger.info(
                    f"Transient recovery detected on fresh scrape: health_score={val_res.health_score:.2f}. "
                    f"No repair required."
                )
                return raw_pages, True, val_res

            return raw_pages, False, val_res

        except Exception as error:
            logger.warning(f"Error checking transient recovery on fresh scrape: {error}")
            return raw_pages, False, None

    def summarize_dom_evidence(self, raw_pages: list[RawPage], max_snippet_length: int = 4000) -> dict[str, Any]:
        """Extract structured DOM summary (tag counts, candidate class names, containers) from raw pages."""
        if not raw_pages:
            return {"sample_url": "", "candidate_classes": [], "tag_counts": {}, "html_snippet": ""}

        sample_page = raw_pages[0]
        html_content = sample_page.get_primary_content()

        candidate_classes: set[str] = set()
        tag_counts: dict[str, int] = {}

        if html_content:
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                for tag in soup.find_all(True):
                    tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
                    classes = tag.get("class", [])
                    if isinstance(classes, list):
                        for c in classes:
                            candidate_classes.add(str(c))
                    elif isinstance(classes, str):
                        candidate_classes.add(classes)
            except Exception as error:
                logger.warning(f"Failed to parse HTML for DOM summary: {error}")

        # Limit candidate classes to top/most descriptive
        sorted_classes = sorted(list(candidate_classes))[:50]

        return {
            "sample_url": sample_page.url or "",
            "candidate_classes": sorted_classes,
            "tag_counts": tag_counts,
            "html_snippet": html_content[:max_snippet_length] if html_content else "",
        }

