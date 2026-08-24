from typing import Any, TypedDict

from leadfinder.models.schemas import ScrapingResult, ScrapingTask


class ScrapingGraphState(TypedDict, total=False):
    """Shared state structure for LangGraph workflow execution across agent nodes in Phase 5."""

    task_id: str
    original_user_query: str
    scraping_task: ScrapingTask | None
    target_urls: list[str]
    navigation_result: dict[str, Any] | None
    scraper_provider: str
    scraper_id: str | None
    scraper_version: str | None
    scraper_code: str | None
    raw_results: list[dict[str, Any]] | None
    extracted_results: list[dict[str, Any]] | None
    extraction_schema: dict[str, Any] | None
    validation_result: dict[str, Any] | None
    diagnosis_result: dict[str, Any] | None
    repair_plan: dict[str, Any] | None
    candidate_configuration: dict[str, Any] | None
    candidate_scraper_version: str | None
    repair_evaluation: dict[str, Any] | None
    repair_history: list[dict[str, Any]]
    repair_attempt: int
    failure: Any | None
    final_output: ScrapingResult | None
