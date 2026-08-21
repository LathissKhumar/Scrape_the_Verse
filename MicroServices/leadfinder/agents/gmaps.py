"""Google Maps scraping agent supporting autonomous delegation and geo-queries."""

import re
from typing import Optional
from uuid import uuid4

from leadfinder.config.logging import get_logger
from leadfinder.config.settings import Settings, get_settings
from leadfinder.gmaps.service import GoogleMapsService
from leadfinder.llm.base import LLMClient
from leadfinder.models.schemas import ScrapingResult, ScrapingTask

logger = get_logger("GMAPS_AGENT")

_PREFIX_CLEAN_PATTERN = re.compile(
    r"^(?:find|search|scrape|get|list|extract)\s+",
    re.IGNORECASE,
)
_LOCATION_SPLIT_PATTERN = re.compile(
    r"^(.*?)\s+(?:in|near|around|at)\s+(.*)$",
    re.IGNORECASE,
)
_GMAPS_DOMAINS = ("google.com/maps", "maps.google", "g.page")
_GMAPS_KEYWORDS = (
    "google maps",
    "near me",
    "in chennai",
    "in bangalore",
    "in mumbai",
    "in delhi",
)


class GoogleMapsAgent:
    """Specialized Agent for local geographic business discovery and Google Maps scraping.

    Enables Agent-to-Agent delegation: When a supervisor or Planner agent identifies
    a local business directory request, it delegates the discovery to GoogleMapsAgent.
    """

    def __init__(
        self,
        service: Optional[GoogleMapsService] = None,
        llm_client: Optional[LLMClient] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self.service = service or GoogleMapsService(settings=self._settings)
        self.llm_client = llm_client

    def is_gmaps_query(self, query_or_url: str) -> bool:
        """Heuristic to detect if a query or URL is intended for Google Maps."""
        lower_query = query_or_url.lower()
        if any(domain in lower_query for domain in _GMAPS_DOMAINS):
            return True
        if any(keyword in lower_query for keyword in _GMAPS_KEYWORDS):
            return True
        return False

    def parse_query_and_location(self, query: str) -> tuple[str, Optional[str]]:
        """Extract search category and geographic location from query string."""
        clean_query = query.strip()
        clean_query = _PREFIX_CLEAN_PATTERN.sub("", clean_query).strip()

        match = _LOCATION_SPLIT_PATTERN.search(clean_query)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return clean_query, None

    async def execute_agent_delegation(
        self,
        task: ScrapingTask,
        source_agent: str = "ScrapingPlannerAgent",
    ) -> ScrapingResult:
        """Invoked via Agent-to-Agent communication to fulfill a local geo-scraping task."""
        task_id = task.task_id or str(uuid4())
        logger.info(
            f"task_id={task_id} GoogleMapsAgent received delegation from '{source_agent}' for objective: '{task.objective}'"
        )

        category, location = self.parse_query_and_location(task.objective)
        leads = await self.service.get_local_leads(query=category, location=location)

        logger.info(f"task_id={task_id} GoogleMapsAgent harvested {len(leads)} local business leads")

        return ScrapingResult(
            task_id=task_id,
            status="success" if leads else "empty",
            records=leads,
            metadata={
                "task_id": task_id,
                "record_count": len(leads),
                "agent": "GoogleMapsAgent",
                "delegated_by": source_agent,
                "category": category,
                "location": location,
                "scraper_provider": "brightdata_gmaps",
            },
        )

