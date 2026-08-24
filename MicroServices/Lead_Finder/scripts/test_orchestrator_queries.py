"""Script to evaluate what the Orchestrator chooses for specific user queries."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.registry import default_scraper_registry
from leadfinder.brightdata.schemas import FieldDefinition, ScrapeTargetRequest
from leadfinder.brightdata.service import BrightDataService
from leadfinder.config.logging import get_logger, setup_logging
from leadfinder.config.settings import get_settings
from leadfinder.gmaps.service import GoogleMapsService

setup_logging()
logger = get_logger("ORCHESTRATOR_QUERY_TEST")


async def evaluate_queries():
    settings = get_settings()
    client = BrightDataClient(settings=settings)
    registry = default_scraper_registry
    service = BrightDataService(settings=settings, client=client, registry=registry)
    gmaps_service = GoogleMapsService(settings=settings, client=client)

    print("=" * 80)
    print("ORCHESTRATOR CLASSIFICATION AND ROUTING ANALYSIS")
    print("=" * 80)

    # -------------------------------------------------------------
    # Query 1: "plumbers"
    # -------------------------------------------------------------
    print("\n--- [QUERY 1]: 'plumbers' ---")
    # A. If evaluated as a target URL for Google Maps
    req_maps = ScrapeTargetRequest(
        url="https://www.google.com/maps/search/plumbers",
        description="Local plumber services search",
        fields=[
            FieldDefinition(name="business_name"),
            FieldDefinition(name="phone_number"),
            FieldDefinition(name="address"),
            FieldDefinition(name="rating"),
            FieldDefinition(name="category"),
        ],
    )
    res_maps = await service.resolve_scraper(req_maps)
    print(
        f"Maps Intent Resolution:      Action={res_maps.action} | Status={res_maps.status} | Collector={res_maps.collector_id}"
    )

    # B. If evaluated as a B2B supplier search on IndiaMART
    req_im = ScrapeTargetRequest(
        url="https://dir.indiamart.com/search.mp?ss=plumbers",
        description="IndiaMART B2B supplier search",
        fields=[
            FieldDefinition(name="company_name"),
            FieldDefinition(name="product_title"),
            FieldDefinition(name="price"),
            FieldDefinition(name="contact_number"),
            FieldDefinition(name="company_catalog_url"),
        ],
    )
    res_im = await service.resolve_scraper(req_im)
    print(
        f"IndiaMART Intent Resolution: Action={res_im.action} | Status={res_im.status} | Collector={res_im.collector_id}"
    )

    # -------------------------------------------------------------
    # Query 2: "restaurents in tambaram"
    # -------------------------------------------------------------
    print("\n--- [QUERY 2]: 'restaurents in tambaram' ---")
    req_rest = ScrapeTargetRequest(
        url="https://www.google.com/maps/search/restaurants+in+Tambaram",
        description="Google Maps local business lead discovery",
        fields=[
            FieldDefinition(name="business_name"),
            FieldDefinition(name="phone_number"),
            FieldDefinition(name="address"),
            FieldDefinition(name="rating"),
            FieldDefinition(name="category"),
        ],
    )
    res_rest = await service.resolve_scraper(req_rest)
    print(
        f"Resolution Result:           Action={res_rest.action} | Status={res_rest.status} | Collector={res_rest.collector_id}"
    )

    # -------------------------------------------------------------
    # Query 3: "details about amazon"
    # -------------------------------------------------------------
    print("\n--- [QUERY 3]: 'details about amazon' ---")
    # For a new target domain like amazon.com with custom schema:
    req_amazon = ScrapeTargetRequest(
        url="https://www.amazon.com/s?k=electronics",
        description="Extract Amazon products, ratings, price, and reviews",
        fields=[
            FieldDefinition(
                name="product_name", description="Name of the Amazon product"
            ),
            FieldDefinition(name="price", description="Current listing price"),
            FieldDefinition(name="rating", description="Customer review rating"),
            FieldDefinition(name="availability", description="Stock status"),
        ],
    )

    # We mock create_scraper so we can detect if it tries to spawn CLI creation without waiting for minutes
    with patch.object(
        service.client, "create_scraper", new_callable=AsyncMock
    ) as mock_cli:
        mock_cli.return_value = "c_mock_amazon_collector"
        res_amazon = await service.resolve_scraper(req_amazon)
        print(
            f"Resolution Result:           Action={res_amazon.action} | Status={res_amazon.status} | Job_ID={res_amazon.job_id} | Scraper_ID={res_amazon.scraper_id}"
        )
        if res_amazon.action == "create":
            print(
                ">>> ORCHESTRATOR DECISION: [CREATE NEW SCRAPER USING BRIGHT DATA CLI]"
            )
            print(f"    Target: {req_amazon.url}")
            print(
                "    Reason: No existing collector matches amazon.com schema. Initiating new collector creation job."
            )


if __name__ == "__main__":
    asyncio.run(evaluate_queries())
