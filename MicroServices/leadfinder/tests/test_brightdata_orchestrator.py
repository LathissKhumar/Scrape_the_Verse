"""Unit tests for Bright Data Scraper Orchestrator and background job handling."""

import asyncio
import os
import tempfile
import pytest
from unittest.mock import AsyncMock, patch

from app.brightdata.client import BrightDataClient
from app.brightdata.jobs import ScraperJobManager
from app.brightdata.registry import ScraperRegistry
from app.brightdata.schemas import (
    CollectorStatus,
    FieldDefinition,
    ScrapeTargetRequest,
)
from app.brightdata.service import BrightDataService
from app.config.settings import Settings


@pytest.fixture
def temp_service():
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name

    settings = Settings(
        BRIGHTDATA=True,
        BRIGHTDATA_API_KEY="test_api_key",
        BRIGHTDATA_REGISTRY_DB_PATH=db_path,
    )
    registry = ScraperRegistry(db_path=db_path)
    jobs = ScraperJobManager(db_path=db_path, registry=registry)
    client = BrightDataClient(settings=settings)
    service = BrightDataService(
        settings=settings,
        client=client,
        registry=registry,
        jobs=jobs,
    )

    yield service

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass


@pytest.mark.asyncio
async def test_resolve_new_request_triggers_creation(temp_service):
    request = ScrapeTargetRequest(
        url="https://example.com/books",
        description="Extract book titles and prices",
        fields=[
            FieldDefinition(name="title", description="Book title"),
            FieldDefinition(name="price", description="Book price"),
        ],
    )

    with patch.object(temp_service.client, "create_scraper", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = "c_book_scraper_99"

        # 1. First resolve request: initiates creation
        res = await temp_service.resolve_scraper(request)
        assert res.action == "create"
        assert res.status == "creating"
        assert res.job_id is not None
        assert res.scraper_id is not None

        # Give background asyncio task time to execute
        await asyncio.sleep(0.05)

        # 2. Check job progress: should now be ready
        job_record = temp_service.jobs.get_job(res.job_id)
        assert job_record is not None
        assert job_record.status == CollectorStatus.READY
        assert job_record.collector_id == "c_book_scraper_99"

        # 3. Second identical resolve request: should REUSE collector immediately
        res2 = await temp_service.resolve_scraper(request)
        assert res2.action == "reuse"
        assert res2.status == "ready"
        assert res2.collector_id == "c_book_scraper_99"


@pytest.mark.asyncio
async def test_resolve_concurrent_creation_reuses_job(temp_service):
    request = ScrapeTargetRequest(
        url="https://example.com/gadgets",
        description="Extract gadget names",
        fields=[FieldDefinition(name="gadget_name")],
    )

    # Mock create_scraper with artificial delay
    async def _slow_create(*args, **kwargs):
        await asyncio.sleep(0.1)
        return "c_gadget_col"

    with patch.object(temp_service.client, "create_scraper", side_effect=_slow_create):
        # First request starts creation
        res1 = await temp_service.resolve_scraper(request)
        assert res1.action == "create"
        assert res1.status == "creating"

        # Second request before worker finishes should return existing in-flight job
        res2 = await temp_service.resolve_scraper(request)
        assert res2.action == "create"
        assert res2.status == "creating"
        assert res2.job_id == res1.job_id
        assert res2.scraper_id == res1.scraper_id

        # Let background task complete
        await asyncio.sleep(0.15)

        # Third request after completion reuses ready collector
        res3 = await temp_service.resolve_scraper(request)
        assert res3.action == "reuse"
        assert res3.status == "ready"
        assert res3.collector_id == "c_gadget_col"


@pytest.mark.asyncio
async def test_resolve_creation_failure_handling(temp_service):
    request = ScrapeTargetRequest(
        url="https://example.com/broken",
        fields=[FieldDefinition(name="f1")],
    )

    with patch.object(temp_service.client, "create_scraper", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("Bright Data CLI network timeout")

        res = await temp_service.resolve_scraper(request)
        assert res.action == "create"
        assert res.status == "creating"

        # Let worker complete with failure
        await asyncio.sleep(0.05)

        job_record = temp_service.jobs.get_job(res.job_id)
        assert job_record is not None
        assert job_record.status == CollectorStatus.FAILED
        assert "network timeout" in (job_record.error or "")


@pytest.mark.asyncio
async def test_run_collector_execution(temp_service):
    with patch.object(temp_service.client, "run_scraper", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = [{"title": "Book A", "price": "$12.99"}]

        run_res = await temp_service.run_collector(
            collector_id="c_valid_123",
            url="https://example.com/books",
        )
        assert run_res.status == "success"
        assert len(run_res.data) == 1
        assert run_res.data[0]["title"] == "Book A"


@pytest.mark.asyncio
async def test_heal_collector_execution(temp_service):
    with patch.object(temp_service.client, "heal_scraper", new_callable=AsyncMock) as mock_heal:
        mock_heal.return_value = {"message": "Repaired layout"}

        heal_res = await temp_service.heal_collector(
            collector_id="c_broken_123",
            failure_description="Pagination missing",
        )
        assert heal_res.status == "ready"
        assert heal_res.collector_id == "c_broken_123"
