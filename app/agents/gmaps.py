import re
from typing import Any, Optional
from uuid import uuid4

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.gmaps.service import GoogleMapsService
from app.llm.base import LLMClient
from app.models.schemas import ScrapingResult, ScrapingTask

logger = get_logger("GMAPS_AGENT")


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
    ):
        self._settings = settings or get_settings()
        self.service = service or GoogleMapsService(settings=self._settings)
        self.llm_client = llm_client

    def is_gmaps_query(self, query_or_url: str) -> bool:
        """Heuristic to detect if a query or URL is intended for Google Maps."""
        lower = query_or_url.lower()
        if "google.com/maps" in lower or "maps.google" in lower or "g.page" in lower:
            return True
        if any(keyword in lower for keyword in ["google maps", "near me", "in chennai", "in bangalore", "in mumbai", "in delhi"]):
            return True
        return False

    def parse_query_and_location(self, query: str) -> tuple[str, Optional[str]]:
        """Extract search category and geographic location from query string."""
        clean = query.strip()
        # Strip common instruction prefixes: find, search, scrape, get, list, extract
        clean = re.sub(r"^(?:find|search|scrape|get|list|extract)\s+", "", clean, flags=re.IGNORECASE).strip()

        # Look for "in <Location>" or "near <Location>"
        match = re.search(r"^(.*?)\s+(?:in|near|around|at)\s+(.*)$", clean, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return clean, None

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
