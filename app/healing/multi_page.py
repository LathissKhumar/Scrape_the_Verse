"""Multi-page canary validation engine for verifying repair candidates across multiple representative pages."""

from typing import Any, Optional
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionSchema, RawPage
from app.models.schemas import ScrapingTask
from app.validation.engine import ValidationEngine
from app.validation.schemas import ValidationResult

logger = get_logger("MULTI_PAGE_VALIDATOR")


class MultiPageRepairValidator:
    """Validates candidate extraction repairs across multiple representative sample pages."""

    def __init__(
        self,
        extraction_engine: Optional[ExtractionEngine] = None,
        validation_engine: Optional[ValidationEngine] = None,
    ) -> None:
        self.settings = get_settings()
        self.extraction_engine = extraction_engine or ExtractionEngine()
        self.validation_engine = validation_engine or ValidationEngine()

    async def validate_candidate_across_pages(
        self,
        task: ScrapingTask,
        schema: ExtractionSchema,
        raw_pages: list[RawPage],
    ) -> tuple[bool, float, list[dict[str, Any]], Optional[str]]:
        """Validate candidate schema across available representative pages.

        Returns:
            (passed, aggregate_health, per_page_metrics, rejection_reason)
        """
        if not self.settings.MULTI_PAGE_VALIDATION_ENABLED or len(raw_pages) <= 1:
            return True, 1.0, [], None

        max_pages = min(len(raw_pages), self.settings.MAX_VALIDATION_PAGES)
        eval_pages = raw_pages[:max_pages]
        logger.debug(f"Executing multi-page validation across {len(eval_pages)} representative pages...")

        per_page_metrics: list[dict[str, Any]] = []
        health_scores: list[float] = []

        for idx, page in enumerate(eval_pages, start=1):
            # Extract on this specific page
            ext_res = await self.extraction_engine.extract_async(
                raw_content=[page],
                task=task,
                schema=schema,
            )

            # Validate extraction on this page
            val_res: ValidationResult = self.validation_engine.validate(
                records=ext_res.records,
                task=task,
                raw_results=[page.model_dump()],
            )

            health_scores.append(val_res.health_score)
            per_page_metrics.append({
                "page_index": idx,
                "url": page.url,
                "records": len(ext_res.records),
                "health_score": val_res.health_score,
                "status": val_res.status,
            })

            # If any individual page completely fails (< 0.40), reject multi-page validation
            if val_res.health_score < 0.40 and len(eval_pages) > 1:
                reason = f"Multi-page inconsistency: Page #{idx} ({page.url}) failed with health={val_res.health_score:.2f}"
                logger.warning(reason)
                return False, sum(health_scores) / len(health_scores), per_page_metrics, reason

        avg_health = sum(health_scores) / len(health_scores)
        passed = avg_health >= 0.70
        reason = None if passed else f"Aggregate multi-page health ({avg_health:.2f}) below threshold 0.70"

        logger.debug(f"Multi-page validation completed: avg_health={avg_health:.2f}, passed={passed}")
        return passed, avg_health, per_page_metrics, reason

