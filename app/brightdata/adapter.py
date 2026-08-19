from typing import Any
from app.models.schemas import ScrapingTask


def build_collector_inputs(task: ScrapingTask) -> list[dict[str, Any]]:
    """Convert a ScrapingTask into the input format expected by Bright Data Scraper Studio.

    Preserves target URLs verbatim and propagates relevant task requirements without
    inventing unrequested fields.
    """
    if not task.target_urls:
        raise ValueError("Cannot build collector inputs: ScrapingTask has no target URLs.")

    inputs: list[dict[str, Any]] = []
    for url in task.target_urls:
        item: dict[str, Any] = {"url": url}
        inputs.append(item)

    return inputs
