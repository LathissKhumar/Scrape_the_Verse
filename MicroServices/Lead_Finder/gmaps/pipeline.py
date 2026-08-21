"""Pipeline for Google Maps business discovery and scraping via Bright Data."""

import re
import urllib.parse
from typing import Any, Optional

from leadfinder.brightdata.client import BrightDataClient
from leadfinder.config.logging import get_logger
from leadfinder.config.settings import Settings, get_settings

logger = get_logger("GMAPS_PIPELINE")

DEFAULT_GMAPS_COLLECTOR_ID = "c_mt1qfvqx1051f3m8r9"

_FLOAT_PATTERN = re.compile(r"(\d+(?:[\.,]\d+)?)")
_DIGIT_PATTERN = re.compile(r"(\d+)")
_NUMERIC_ONLY_PATTERN = re.compile(r"^\d+[\.,]\d+$")
_INVALID_STRING_VALUES = {"None", "null", "#", ""}


class GoogleMapsPipeline:
    """Standalone pipeline for scraping local businesses and leads from Google Maps.

    Uses Bright Data Scraper Studio Collector to extract business name,
    phone number, address, website, rating, reviews, and category.
    """

    def __init__(
        self,
        client: Optional[BrightDataClient] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self.client = client or BrightDataClient(settings=self._settings)

    @property
    def collector_id(self) -> str:
        return (
            self._settings.BRIGHTDATA_GMAPS_COLLECTOR_ID
            or DEFAULT_GMAPS_COLLECTOR_ID
        )

    def format_maps_search_url(self, query: str, location: Optional[str] = None) -> str:
        """Format a search term and optional location into a Google Maps search URL."""
        trimmed_query = query.strip()
        if trimmed_query.startswith("http://") or trimmed_query.startswith("https://"):
            return trimmed_query

        search_phrase = trimmed_query
        if location and location.lower() not in trimmed_query.lower():
            search_phrase = f"{trimmed_query} in {location.strip()}"

        encoded_query = urllib.parse.quote_plus(search_phrase)
        return f"https://www.google.com/maps/search/{encoded_query}"

    def normalize_lead(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize and clean raw Google Maps scraped records."""
        return {
            "business_name": self._extract_business_name(record),
            "phone_number": self._extract_phone_number(record),
            "website": self._extract_website(record),
            "address": self._extract_address(record),
            "rating": self._extract_rating(record),
            "reviews_count": self._extract_reviews_count(record),
            "category": self._extract_category(record),
            "maps_url": self._extract_maps_url(record),
        }

    @staticmethod
    def _extract_business_name(record: dict[str, Any]) -> str:
        raw_name = (
            record.get("business_name")
            or record.get("title")
            or record.get("name")
            or record.get("company_name")
            or ""
        )
        return str(raw_name).strip()

    @staticmethod
    def _extract_phone_number(record: dict[str, Any]) -> str:
        raw_phone = str(
            record.get("phone_number")
            or record.get("phone")
            or record.get("contact_number")
            or record.get("tel")
            or ""
        ).strip()
        if raw_phone in ("None", "null"):
            return ""
        return raw_phone

    @staticmethod
    def _extract_website(record: dict[str, Any]) -> str:
        raw_website = str(
            record.get("website")
            or record.get("website_url")
            or record.get("domain")
            or ""
        ).strip()
        if raw_website in _INVALID_STRING_VALUES:
            return ""
        return raw_website

    @staticmethod
    def _extract_address(record: dict[str, Any]) -> str:
        raw_address = str(
            record.get("address")
            or record.get("location")
            or record.get("full_address")
            or ""
        ).strip()
        if raw_address in ("None", "null", "") or _NUMERIC_ONLY_PATTERN.match(raw_address):
            return ""
        return raw_address

    @staticmethod
    def _extract_rating(record: dict[str, Any]) -> Optional[float]:
        rating_raw = record.get("rating") or record.get("stars")
        if not rating_raw:
            return None
        try:
            if isinstance(rating_raw, (int, float)):
                return float(rating_raw)
            match = _FLOAT_PATTERN.search(str(rating_raw))
            if match:
                return float(match.group(1).replace(",", "."))
        except Exception:
            return None
        return None

    @staticmethod
    def _extract_reviews_count(record: dict[str, Any]) -> Optional[int]:
        reviews_raw = (
            record.get("reviews_count")
            or record.get("reviews")
            or record.get("total_reviews")
        )
        if not reviews_raw:
            return None
        try:
            if isinstance(reviews_raw, int):
                return reviews_raw
            cleaned_str = str(reviews_raw).replace(",", "").replace("(", "").replace(")", "")
            match = _DIGIT_PATTERN.search(cleaned_str)
            if match:
                return int(match.group(1))
        except Exception:
            return None
        return None

    @staticmethod
    def _extract_category(record: dict[str, Any]) -> str:
        category_raw = str(
            record.get("category")
            or record.get("type")
            or record.get("service_type")
            or ""
        ).strip()
        if category_raw in ("None", "null", "") or _NUMERIC_ONLY_PATTERN.match(category_raw):
            return ""
        return category_raw

    @staticmethod
    def _extract_maps_url(record: dict[str, Any]) -> str:
        return str(
            record.get("maps_url")
            or record.get("url")
            or record.get("link")
            or ""
        ).strip()

    async def search_leads(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Run Google Maps collector for the given query and location."""
        target_url = self.format_maps_search_url(query=query, location=location)
        collector_id = self.collector_id
        logger.info(f"Executing Google Maps lead search on '{target_url}' via collector '{collector_id}'")

        raw_results: list[dict[str, Any]] = []

        try:
            inputs = [{"url": target_url}]
            results = await self.client.scrape_and_collect(collector_id=collector_id, inputs=inputs)
            if results:
                raw_results = results
        except Exception as error:
            logger.warning(f"REST trigger failed or timed out ({error}). Trying CLI runner...")

        if not raw_results:
            try:
                raw_results = await self.client.scrape_via_cli(collector_id=collector_id, url=target_url)
            except Exception as error:
                logger.error(f"Google Maps CLI execution failed: {error}")

        # Normalize and filter results
        normalized_leads: list[dict[str, Any]] = []
        for raw_record in raw_results:
            cleaned_lead = self.normalize_lead(raw_record)
            if cleaned_lead.get("business_name") or cleaned_lead.get("phone_number"):
                normalized_leads.append(cleaned_lead)

        logger.info(f"Google Maps search completed with {len(normalized_leads)} normalized lead(s)")
        return normalized_leads

