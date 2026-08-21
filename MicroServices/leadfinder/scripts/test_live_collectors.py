import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.brightdata.client import BrightDataClient
from app.brightdata.registry import (
    ScraperRegistry,
    compute_schema_hash,
    default_scraper_registry,
)
from app.brightdata.schemas import (
    CollectorStatus,
    FieldDefinition,
    ScrapeTargetRequest,
)
from app.brightdata.service import BrightDataService
from app.config.logging import get_logger, setup_logging
from app.config.settings import get_settings
from app.gmaps.service import GoogleMapsService

setup_logging()
logger = get_logger("TEST_LIVE_COLLECTORS")


async def main():
    settings = get_settings()
    print("=" * 70)
    print("BRIGHT DATA LIVE COLLECTOR TEST SUITE")
    print(f"API Key configured: {'YES' if settings.BRIGHTDATA_API_KEY else 'NO'}")
    print(f"Discovery Collector: {settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID}")
    print(f"Company Collector:   {settings.BRIGHTDATA_COMPANY_COLLECTOR_ID}")
    print(f"GMaps Collector:     {settings.BRIGHTDATA_GMAPS_COLLECTOR_ID}")
    print("=" * 70)

    client = BrightDataClient(settings=settings)
    registry = default_scraper_registry
    service = BrightDataService(settings=settings, client=client, registry=registry)
    gmaps_service = GoogleMapsService(settings=settings, client=client)

    # -------------------------------------------------------------
    # 1. Register Pre-configured Collectors in Registry if not present
    # -------------------------------------------------------------
    print("\n[STEP 1] Seeding Pre-configured Collectors in Scraper Registry...")

    # IndiaMART Discovery Collector
    indiamart_url = "https://dir.indiamart.com/search.mp"
    indiamart_fields = [
        FieldDefinition(name="company_name", description="Name of the supplier or business"),
        FieldDefinition(name="product_title", description="Title of the product"),
        FieldDefinition(name="price", description="Product price"),
        FieldDefinition(name="contact_number", description="Supplier contact phone number"),
        FieldDefinition(name="company_catalog_url", description="URL to company catalog"),
    ]
    im_norm = registry.find_compatible("https://dir.indiamart.com/search.mp", compute_schema_hash("https://dir.indiamart.com/search.mp", indiamart_fields))
    if not im_norm or not im_norm.collector_id:
        im_rec = registry.create_record(
            target_url=indiamart_url,
            fields=indiamart_fields,
            description="IndiaMART B2B supplier search",
        )
        registry.update_status(
            record_id=im_rec.id,
            status=CollectorStatus.READY,
            collector_id=settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID,
        )
        print(f"[OK] Registered IndiaMART Collector: ID={im_rec.id} -> {settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID}")
    else:
        print(f"[OK] Existing IndiaMART Collector found in registry: {im_norm.collector_id}")

    # Google Maps Collector
    gmaps_url = "https://www.google.com/maps/search/"
    gmaps_fields = [
        FieldDefinition(name="business_name", description="Name of the business"),
        FieldDefinition(name="phone_number", description="Business phone number"),
        FieldDefinition(name="address", description="Full address"),
        FieldDefinition(name="rating", description="Rating score"),
        FieldDefinition(name="category", description="Category or industry"),
    ]
    gm_norm = registry.find_compatible("https://www.google.com/maps/search", compute_schema_hash("https://www.google.com/maps/search", gmaps_fields))
    if not gm_norm or not gm_norm.collector_id:
        gm_rec = registry.create_record(
            target_url=gmaps_url,
            fields=gmaps_fields,
            description="Google Maps local business lead discovery",
        )
        registry.update_status(
            record_id=gm_rec.id,
            status=CollectorStatus.READY,
            collector_id=settings.BRIGHTDATA_GMAPS_COLLECTOR_ID,
        )
        print(f"[OK] Registered Google Maps Collector: ID={gm_rec.id} -> {settings.BRIGHTDATA_GMAPS_COLLECTOR_ID}")
    else:
        print(f"[OK] Existing Google Maps Collector found in registry: {gm_norm.collector_id}")

    # -------------------------------------------------------------
    # 2. Test Orchestrator Resolution (Verify Reuse)
    # -------------------------------------------------------------
    print("\n[STEP 2] Testing Scraper Orchestrator Resolution (Reuse Check)...")
    im_request = ScrapeTargetRequest(
        url="https://dir.indiamart.com/search.mp?ss=solar+panels",
        description="IndiaMART B2B supplier search",
        fields=indiamart_fields,
    )
    resolve_res = await service.resolve_scraper(im_request)
    print(f"Resolve IndiaMART Response: action={resolve_res.action}, status={resolve_res.status}, collector_id={resolve_res.collector_id}")
    assert resolve_res.action == "reuse", "Expected action to be 'reuse' for existing collector!"

    # -------------------------------------------------------------
    # 3. Test Running IndiaMART Collector
    # -------------------------------------------------------------
    print("\n[STEP 3] Running IndiaMART Discovery Collector...")
    target_im_search = "https://dir.indiamart.com/search.mp?ss=solar+panels"
    print(f"Target URL: {target_im_search}")
    print(f"Collector ID: {settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID}")

    try:
        im_start = time.time()
        im_records = await service.pipeline.run_discovery("solar panels")
        im_elapsed = round(time.time() - im_start, 2)
        print(f"\n[OUTPUT] IndiaMART Scrape Result ({im_elapsed}s, records={len(im_records)}):")
        print(json.dumps(im_records[:3], indent=2))
    except Exception as e:
        print(f"IndiaMART run error: {e}")

    # -------------------------------------------------------------
    # 4. Test Running Google Maps Collector
    # -------------------------------------------------------------
    print("\n[STEP 4] Running Google Maps Lead Discovery Collector...")
    print(f"Query: 'plumbers in Chennai'")
    print(f"Collector ID: {settings.BRIGHTDATA_GMAPS_COLLECTOR_ID}")

    try:
        gm_start = time.time()
        gm_leads = await gmaps_service.get_local_leads(query="plumbers", location="Chennai")
        gm_elapsed = round(time.time() - gm_start, 2)
        print(f"\n[OUTPUT] Google Maps Scrape Result ({gm_elapsed}s, leads={len(gm_leads)}):")
        print(json.dumps(gm_leads[:3], indent=2))
    except Exception as e:
        print(f"Google Maps run error: {e}")

    print("\n" + "=" * 70)
    print("LIVE COLLECTOR TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
