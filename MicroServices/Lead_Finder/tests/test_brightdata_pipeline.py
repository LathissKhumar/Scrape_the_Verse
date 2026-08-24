from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.pipeline import BrightDataLeadPipeline
from leadfinder.brightdata.service import BrightDataService
from leadfinder.config.settings import Settings
from leadfinder.models.schemas import ScrapingResult, ScrapingTask


def test_pipeline_url_formatting():
    """Verify that BrightDataLeadPipeline correctly formats queries and catalog URLs."""
    pipeline = BrightDataLeadPipeline()

    # Search URL generation
    search_url = pipeline.format_search_url("solar panels")
    assert search_url == "https://dir.indiamart.com/search.mp?ss=solar+panels"

    # Already valid URL preservation
    direct_url = "https://dir.indiamart.com/search.mp?ss=packaging"
    assert pipeline.format_search_url(direct_url) == direct_url

    # Company profile URL derivation
    company_subdomain = "https://www.indiamart.com/cosmic-tech-solutions/"
    assert (
        pipeline.format_company_profile_url(company_subdomain)
        == "https://www.indiamart.com/cosmic-tech-solutions/profile.html"
    )

    external_site = "https://www.bpackindustries.co.in"
    assert (
        pipeline.format_company_profile_url(external_site)
        == "https://www.bpackindustries.co.in"
    )


@pytest.mark.asyncio
async def test_lead_pipeline_discovery_and_enrichment():
    """Test full lead pipeline execution with mocked collector outputs."""
    mock_discovery_output = [
        {
            "company_name": "Cosmic Tech Solutions",
            "product_title": "Solar Panel 540W",
            "price": {"value": 14500, "currency": "INR", "symbol": "₹"},
            "city": "Chennai",
            "state": "Tamil Nadu",
            "company_catalog_url": "https://www.indiamart.com/cosmic-tech-solutions/",
        }
    ]

    mock_profile_output = {
        "company_name": "Cosmic Tech Solutions",
        "contact_person": "T Saktheeshwari (CEO)",
        "gstin": "33**********1Z3",
        "established_year": "2022",
        "nature_of_business": "Trader - Wholesaler/Distributor",
    }

    mock_client = MagicMock(spec=BrightDataClient)
    mock_client.scrape_and_collect = AsyncMock()
    mock_client.scrape_via_cli = AsyncMock()

    # Configure client mock to return discovery then profile
    mock_client.scrape_and_collect.side_effect = [
        mock_discovery_output,
        [mock_profile_output],
    ]

    pipeline = BrightDataLeadPipeline(client=mock_client)
    leads = await pipeline.generate_leads(
        query_or_url="solar panels", enrich_profiles=True
    )

    assert len(leads) == 1
    lead = leads[0]
    assert lead["company_name"] == "Cosmic Tech Solutions"
    assert lead["product_title"] == "Solar Panel 540W"
    assert lead["contact_person"] == "T Saktheeshwari (CEO)"
    assert lead["gstin"] == "33**********1Z3"
    assert lead["established_year"] == "2022"


@pytest.mark.asyncio
async def test_brightdata_service_execute_task():
    """Test BrightDataService fast-path execution of ScrapingTask."""
    mock_client = MagicMock(spec=BrightDataClient)
    mock_client.is_configured = True
    mock_client.scrape_and_collect = AsyncMock(
        return_value=[
            {
                "company_name": "Sparkbee Tech",
                "product_title": "Adani Solar Panel",
                "price": {"value": 9450, "currency": "INR", "symbol": "₹"},
                "city": "Chennai",
                "state": "Tamil Nadu",
            }
        ]
    )

    settings = Settings(
        BRIGHTDATA=True,
        BRIGHTDATA_API_KEY="test_key",
        BRIGHTDATA_COLLECTOR_ID="c_test_discovery",
    )

    service = BrightDataService(settings=settings, client=mock_client)
    assert service.is_enabled is True

    task = ScrapingTask(
        task_id="task-123",
        objective="Find solar panels",
        target_urls=["https://dir.indiamart.com/search.mp?ss=solar+panels"],
    )

    result = await service.execute_task(task)
    assert result.status == "success"
    assert result.task_id == "task-123"
    assert len(result.records) == 1
    assert result.records[0]["company_name"] == "Sparkbee Tech"
    assert result.metadata["scraper_provider"] == "brightdata"


def test_api_brightdata_routing_fast_path():
    """Test FastAPI /scrape endpoint fast-path routing when BRIGHTDATA=True."""
    from leadfinder.main import app

    # Mock brightdata_service to return immediate success
    mock_service = MagicMock(spec=BrightDataService)
    mock_service.is_enabled = True
    mock_service.execute_task = AsyncMock(
        return_value=ScrapingResult(
            task_id="fast-path-task",
            status="success",
            records=[{"company_name": "Fast Path Corp", "city": "Mumbai"}],
            metadata={"scraper_provider": "brightdata"},
        )
    )

    with patch("leadfinder.main.brightdata_service", mock_service):
        client = TestClient(app)
        response = client.post(
            "/scrape",
            json={
                "query": "Find machinery suppliers",
                "target_urls": ["https://dir.indiamart.com/search.mp?ss=machinery"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["records"][0]["company_name"] == "Fast Path Corp"


def test_api_brightdata_leads_endpoint():
    """Test dedicated /api/v1/brightdata/leads endpoint."""
    from leadfinder.main import app

    mock_service = MagicMock(spec=BrightDataService)
    mock_service.is_enabled = True
    mock_service.generate_leads = AsyncMock(
        return_value=[
            {
                "company_name": "Solar Tech India",
                "contact_person": "A Kumar (Director)",
                "city": "Delhi",
            }
        ]
    )

    with patch("leadfinder.main.brightdata_service", mock_service):
        client = TestClient(app)
        response = client.post(
            "/api/v1/brightdata/leads",
            json={"query": "solar panels in Delhi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "solar panels in Delhi"
        assert data["total_leads"] == 1
        assert data["leads"][0]["company_name"] == "Solar Tech India"
