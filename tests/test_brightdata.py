import pytest
from app.brightdata.client import BrightDataClient
from app.config.settings import Settings


def test_brightdata_is_configured_flag():
    unconfigured = BrightDataClient(Settings(BRIGHTDATA_API_KEY=None))
    assert unconfigured.is_configured is False

    configured = BrightDataClient(Settings(BRIGHTDATA_API_KEY="valid_key"))
    assert configured.is_configured is True


@pytest.mark.asyncio
async def test_brightdata_trigger_scraper_raises_not_implemented():
    client = BrightDataClient()
    with pytest.raises(NotImplementedError) as exc:
        await client.trigger_scraper(collector_id="c_123", inputs=[])
    assert "Phase 2" in str(exc.value)


@pytest.mark.asyncio
async def test_brightdata_get_job_status_raises_not_implemented():
    client = BrightDataClient()
    with pytest.raises(NotImplementedError) as exc:
        await client.get_job_status(job_id="j_123")
    assert "Phase 2" in str(exc.value)


@pytest.mark.asyncio
async def test_brightdata_fetch_results_raises_not_implemented():
    client = BrightDataClient()
    with pytest.raises(NotImplementedError) as exc:
        await client.fetch_results(job_id="j_123")
    assert "Phase 2" in str(exc.value)
