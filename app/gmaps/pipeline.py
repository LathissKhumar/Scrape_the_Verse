import re
import urllib.parse
from typing import Any, Optional

from app.brightdata.client import BrightDataClient
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings

logger = get_logger("GMAPS_PIPELINE")

DEFAULT_GMAPS_COLLECTOR_ID = "c_mt1qfvqx1051f3m8r9"


class GoogleMapsPipeline:
    """Standalone pipeline for scraping local businesses and leads from Google Maps.

    Uses Bright Data Scraper Studio Collector (c_mt1q7dib7sifinjkq) to extract
    business name, phone number, address, website, rating, reviews, and category.
    """

    def __init__(
        self,
        client: Optional[BrightDataClient] = None,
        settings: Optional[Settings] = None,
    ):
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
        trimmed = query.strip()
        if trimmed.startswith("http://") or trimmed.startswith("https://"):
            return trimmed

        search_phrase = trimmed
        if location and location.lower() not in trimmed.lower():
            search_phrase = f"{trimmed} in {location.strip()}"

        encoded = urllib.parse.quote_plus(search_phrase)
        return f"https://www.google.com/maps/search/{encoded}"

    def normalize_lead(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize and clean raw Google Maps scraped records."""
        # Clean business name
        name = (
            record.get("business_name")
            or record.get("title")
            or record.get("name")
            or record.get("company_name")
            or ""
        ).strip()

        # Clean phone number
        phone = str(
            record.get("phone_number")
            or record.get("phone")
            or record.get("contact_number")
            or record.get("tel")
            or ""
        ).strip()
        if phone == "None" or phone == "null":
            phone = ""

        # Clean website
        website = str(
            record.get("website")
            or record.get("website_url")
            or record.get("domain")
            or ""
        ).strip()
        if website in ("None", "null", "#"):
            website = ""

        # Clean address
        address = str(
            record.get("address")
            or record.get("location")
            or record.get("full_address")
            or ""
        ).strip()
        if address in ("None", "null", "") or re.match(r"^\d+[\.,]\d+$", address):
            address = ""

        # Clean rating
        rating_raw = record.get("rating") or record.get("stars")
        rating_val: Optional[float] = None
        if rating_raw:
            try:
                if isinstance(rating_raw, (int, float)):
                    rating_val = float(rating_raw)
                else:
                    match = re.search(r"(\d+(?:[\.,]\d+)?)", str(rating_raw))
                    if match:
                        rating_val = float(match.group(1).replace(",", "."))
            except Exception:
                pass

        # Clean review count
        reviews_raw = record.get("reviews_count") or record.get("reviews") or record.get("total_reviews")
        reviews_val: Optional[int] = None
        if reviews_raw:
            try:
                if isinstance(reviews_raw, int):
                    reviews_val = reviews_raw
                else:
                    cleaned_str = str(reviews_raw).replace(",", "").replace("(", "").replace(")", "")
                    match = re.search(r"(\d+)", cleaned_str)
                    if match:
                        reviews_val = int(match.group(1))
            except Exception:
                pass

        # Clean category
        category = str(
            record.get("category")
            or record.get("type")
            or record.get("service_type")
            or ""
        ).strip()
        if category in ("None", "null", "") or re.match(r"^\d+[\.,]\d+$", category):
            category = ""

        # Clean Google Maps URL
        maps_url = str(
            record.get("maps_url")
            or record.get("url")
            or record.get("link")
            or ""
        ).strip()

        return {
            "business_name": name,
            "phone_number": phone,
            "website": website,
            "address": address,
            "rating": rating_val,
            "reviews_count": reviews_val,
            "category": category,
            "maps_url": maps_url,
        }

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
        except Exception as e:
            logger.warning(f"REST trigger failed or timed out ({e}). Trying CLI runner...")

        if not raw_results:
            try:
                raw_results = await self.client.scrape_via_cli(collector_id=collector_id, url=target_url)
            except Exception as e:
                logger.error(f"Google Maps CLI execution failed: {e}")

        # Normalize and filter results
        normalized = []
        for r in raw_results:
            cleaned = self.normalize_lead(r)
            if cleaned.get("business_name") or cleaned.get("phone_number"):
                normalized.append(cleaned)

        logger.info(f"Google Maps search completed with {len(normalized)} normalized lead(s)")
        return normalized
