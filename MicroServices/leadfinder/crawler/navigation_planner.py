"""Navigation planner sub-agent determining navigation actions and search strategies."""

import logging
from typing import Any

from leadfinder.models.schemas import ScrapingTask

logger = logging.getLogger("NAVIGATION_PLANNER")


class NavigationPlanner:
    """Plans on-site search interactions, filter applications, and link harvest limits."""

    def plan_navigation(self, task: ScrapingTask) -> dict[str, Any]:
        """Formulate a concrete navigation execution plan from a ScrapingTask."""
        root_url = task.target_urls[0] if task.target_urls else "https://www.google.com"

        return {
            "root_url": root_url,
            "is_search": task.is_search,
            "search_keyword": task.search_keyword or "",
            "deep_crawl": task.deep_crawl,
            "max_links": task.max_detail_pages or 20,
            "filters": task.filters or {},
            "max_pagination_pages": min(5, ((task.max_detail_pages or 20) // 10) + 1),
        }
