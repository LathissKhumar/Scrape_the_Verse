"""Chained multi-tier lead generation pipeline using Bright Data collectors."""

import asyncio
import urllib.parse
from typing import Any, Optional

from leadfinder.brightdata.client import BrightDataClient
from leadfinder.config.logging import get_logger
from leadfinder.config.settings import Settings, get_settings

logger = get_logger("BRIGHTDATA_PIPELINE")

DEFAULT_DISCOVERY_COLLECTOR_ID = "c_mt1klz941e6wjo8o6y"
DEFAULT_COMPANY_COLLECTOR_ID = "c_mt1n1d372h5qpcxcvh"


class BrightDataLeadPipeline:
    """Chained 2-Tier B2B Lead Generation Pipeline using Bright Data Scraper Studio collectors.

    Tier 1 (Discovery): Searches products/services to find suppliers, pricing, and catalog URLs.
    Tier 2 (Company Details): Concurrently queries company profile endpoints to enrich leads with
                              CEO/MD names, GSTIN, year established, and business nature.
    """

    def __init__(
        self,
        client: Optional[BrightDataClient] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self.client = client or BrightDataClient(settings=self._settings)

    @property
    def discovery_collector_id(self) -> str:
        return (
            self._settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID
            or self._settings.BRIGHTDATA_COLLECTOR_ID
            or DEFAULT_DISCOVERY_COLLECTOR_ID
        )

    @property
    def company_collector_id(self) -> str:
        return (
            self._settings.BRIGHTDATA_COMPANY_COLLECTOR_ID
            or DEFAULT_COMPANY_COLLECTOR_ID
        )

    def format_search_url(self, query_or_url: str) -> str:
        """Format a search query or URL into an IndiaMART catalog search URL."""
        if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
            return query_or_url

        encoded_query = urllib.parse.quote_plus(query_or_url.strip())
        return f"https://dir.indiamart.com/search.mp?ss={encoded_query}"

    def format_company_profile_url(self, catalog_url: str) -> str:
        """Derive the profile URL from a company catalog URL."""
        normalized_url = catalog_url.strip().rstrip("/")
        if not normalized_url.startswith("http://") and not normalized_url.startswith("https://"):
            normalized_url = f"https://{normalized_url}"

        # If it's already a profile/aboutus URL, preserve it
        if "profile.html" in normalized_url or "aboutus.html" in normalized_url:
            return normalized_url

        # If it's an IndiaMART company subdomain, append profile.html
        if "indiamart.com" in normalized_url:
            return f"{normalized_url}/profile.html"

        return normalized_url

    async def run_discovery(self, query_or_url: str) -> list[dict[str, Any]]:
        """Run Discovery Collector (Collector 1) to find supplier leads and catalog URLs."""
        target_url = self.format_search_url(query_or_url)
        collector_id = self.discovery_collector_id
        logger.info(f"Running Tier 1 Discovery on '{target_url}' with collector '{collector_id}'")

        try:
            # First attempt REST trigger
            inputs = [{"url": target_url}]
            results = await self.client.scrape_and_collect(collector_id=collector_id, inputs=inputs)
            if results:
                return results
        except Exception as error:
            logger.warning(f"REST trigger failed or returned empty ({error}). Falling back to CLI runner...")

        # Fallback to direct CLI runner
        return await self.client.scrape_via_cli(collector_id=collector_id, url=target_url)

    async def enrich_company(self, company_url: str) -> dict[str, Any]:
        """Run Company Profile Collector (Collector 2) on a single company catalog/profile URL."""
        profile_url = self.format_company_profile_url(company_url)
        collector_id = self.company_collector_id
        logger.debug(f"Enriching company profile for '{profile_url}' with collector '{collector_id}'")

        try:
            inputs = [{"url": profile_url}]
            results = await self.client.scrape_and_collect(collector_id=collector_id, inputs=inputs)
            if results and isinstance(results, list):
                return results[0]
        except Exception as error:
            logger.debug(f"REST enrichment failed for '{profile_url}' ({error}). Trying CLI runner...")

        try:
            results = await self.client.scrape_via_cli(collector_id=collector_id, url=profile_url)
            if results and isinstance(results, list):
                return results[0]
        except Exception as error:
            logger.warning(f"Failed to enrich company '{profile_url}': {error}")

        return {}

    async def enrich_companies_batch(
        self,
        discovery_leads: list[dict[str, Any]],
        max_concurrency: int = 5,
    ) -> list[dict[str, Any]]:
        """Enrich a batch of discovery leads concurrently using Collector 2."""
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _enrich_single_lead(lead: dict[str, Any]) -> dict[str, Any]:
            catalog_url = lead.get("company_catalog_url")
            if not catalog_url:
                return lead

            async with semaphore:
                company_details = await self.enrich_company(catalog_url)
                if company_details:
                    # Merge deep company facts while preserving discovery fields
                    merged = dict(lead)
                    for key, value in company_details.items():
                        if key not in merged or not merged[key]:
                            merged[key] = value
                    return merged
                return lead

        tasks = [_enrich_single_lead(lead) for lead in discovery_leads]
        enriched_results = await asyncio.gather(*tasks)
        return list(enriched_results)

    async def generate_leads(
        self,
        query_or_url: str,
        enrich_profiles: bool = True,
        max_concurrency: int = 5,
    ) -> list[dict[str, Any]]:
        """Execute the end-to-end B2B Lead Generation pipeline."""
        # Tier 1: Discovery
        discovery_leads = await self.run_discovery(query_or_url)
        logger.info(f"Tier 1 Discovery completed with {len(discovery_leads)} lead(s)")

        if not discovery_leads or not enrich_profiles:
            return discovery_leads

        # Tier 2: Concurrent Profile Enrichment
        logger.info(f"Starting Tier 2 Profile Enrichment for {len(discovery_leads)} lead(s)...")
        enriched_leads = await self.enrich_companies_batch(
            discovery_leads=discovery_leads,
            max_concurrency=max_concurrency,
        )
        logger.info(f"Lead Generation pipeline completed successfully with {len(enriched_leads)} enriched lead(s)")
        return enriched_leads

