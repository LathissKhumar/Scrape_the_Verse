from typing import Any, Optional, TypedDict
from app.models.schemas import ScrapingResult, ScrapingTask


class ScrapingGraphState(TypedDict, total=False):
    """Shared state structure for LangGraph workflow execution across agent nodes."""

    task_id: str
    original_user_query: str
    scraping_task: Optional[ScrapingTask]
    target_urls: list[str]
    scraper_id: Optional[str]
    scraper_version: Optional[str]
    scraper_code: Optional[str]
    raw_results: Optional[list[dict[str, Any]]]
    extracted_results: Optional[list[dict[str, Any]]]
    validation_result: Optional[dict[str, Any]]
    failure: Optional[dict[str, Any]]
    repair_attempt: int
    final_output: Optional[ScrapingResult]
