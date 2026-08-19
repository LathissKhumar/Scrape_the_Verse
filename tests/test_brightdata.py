import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.brightdata.client import BrightDataClient
from app.brightdata.exceptions import (
    BrightDataAuthError,
    BrightDataConfigError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from app.config.settings import Settings


def test_brightdata_is_configured_flag():
    unconfigured = BrightDataClient(Settings(BRIGHTDATA_API_KEY=None, BRIGHTDATA_COLLECTOR_ID=None))
    assert unconfigured.is_configured is False

    partial_key = BrightDataClient(Settings(BRIGHTDATA_API_KEY="valid_key", BRIGHTDATA_COLLECTOR_ID=None))
    assert partial_key.is_configured is False

    configured = BrightDataClient(Settings(BRIGHTDATA_API_KEY="valid_key", BRIGHTDATA_COLLECTOR_ID="col_123"))
    assert configured.is_configured is True


@pytest.mark.asyncio
async def test_brightdata_unconfigured_raises():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY=None))
    with pytest.raises(BrightDataConfigError) as exc:
        await client.trigger_scraper(collector_id="col_123", inputs=[])
    assert "credentials are not configured" in str(exc.value)


@pytest.mark.asyncio
async def test_brightdata_trigger_scraper_success():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    mock_response = httpx.Response(
        status_code=200,
        json={"collection_id": "job_abc_123"},
        request=httpx.Request("POST", "https://api.brightdata.com/dca/trigger"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        job_id = await client.trigger_scraper(inputs=[{"url": "https://example.com"}])
        assert job_id == "job_abc_123"


@pytest.mark.asyncio
async def test_brightdata_trigger_auth_error():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="bad_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    mock_response = httpx.Response(
        status_code=401,
        text="Unauthorized",
        request=httpx.Request("POST", "https://api.brightdata.com/dca/trigger"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(BrightDataAuthError):
            await client.trigger_scraper(inputs=[])


@pytest.mark.asyncio
async def test_brightdata_trigger_timeout():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timed out")):
        with pytest.raises(BrightDataTimeoutError):
            await client.trigger_scraper(inputs=[])


@pytest.mark.asyncio
async def test_brightdata_get_job_status_running():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    mock_response = httpx.Response(
        status_code=200,
        json={"status": "building", "message": "Dataset not ready"},
        request=httpx.Request("GET", "https://api.brightdata.com/dca/dataset"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        status_info = await client.get_job_status("job_abc_123")
        assert status_info["status"] == "running"


@pytest.mark.asyncio
async def test_brightdata_get_job_status_completed_array():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    mock_response = httpx.Response(
        status_code=200,
        json=[{"name": "Item 1", "price": "$10"}],
        request=httpx.Request("GET", "https://api.brightdata.com/dca/dataset"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        status_info = await client.get_job_status("job_abc_123")
        assert status_info["status"] == "completed"
        assert len(status_info["data"]) == 1
        assert status_info["data"][0]["name"] == "Item 1"


@pytest.mark.asyncio
async def test_brightdata_get_job_status_failed():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    mock_response = httpx.Response(
        status_code=200,
        json={"status": "failed", "error": "Target website blocked request"},
        request=httpx.Request("GET", "https://api.brightdata.com/dca/dataset"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        status_info = await client.get_job_status("job_abc_123")
        assert status_info["status"] == "failed"
        assert "blocked" in status_info["error"]


@pytest.mark.asyncio
async def test_brightdata_scrape_and_collect_success():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    with patch.object(client, "trigger_scraper", new_callable=AsyncMock) as mock_trigger, \
         patch.object(client, "get_job_status", new_callable=AsyncMock) as mock_status:

        mock_trigger.return_value = "job_123"
        # First poll returns running, second poll returns completed
        mock_status.side_effect = [
            {"status": "running"},
            {"status": "completed", "data": [{"name": "Widget A", "price": "$25"}]},
        ]

        results = await client.scrape_and_collect(inputs=[{"url": "https://example.com"}], poll_interval=0.01)
        assert len(results) == 1
        assert results[0]["name"] == "Widget A"


@pytest.mark.asyncio
async def test_brightdata_scrape_and_collect_polling_timeout():
    client = BrightDataClient(Settings(BRIGHTDATA_API_KEY="test_key", BRIGHTDATA_COLLECTOR_ID="col_123"))

    with patch.object(client, "trigger_scraper", new_callable=AsyncMock) as mock_trigger, \
         patch.object(client, "get_job_status", new_callable=AsyncMock) as mock_status:

        mock_trigger.return_value = "job_123"
        mock_status.return_value = {"status": "running"}

        with pytest.raises(BrightDataTimeoutError):
            await client.scrape_and_collect(
                inputs=[{"url": "https://example.com"}],
                poll_interval=0.01,
                max_poll_seconds=0.03,
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_brightdata_integration():
    """Optional integration test against live Bright Data (skipped if unconfigured)."""
    settings = Settings()
    client = BrightDataClient(settings=settings)
    if not client.is_configured:
        pytest.skip("Bright Data credentials not configured in environment.")

    results = await client.scrape_and_collect(
        inputs=[{"url": "https://example.com"}],
        max_poll_seconds=60.0,
    )
    assert isinstance(results, list)
