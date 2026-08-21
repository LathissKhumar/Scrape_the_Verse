"""Unit tests for BrightDataClient CLI subprocess wrapper and error handling."""

import pytest
from unittest.mock import AsyncMock, patch

from app.brightdata.client import BrightDataClient
from app.brightdata.exceptions import (
    BrightDataConfigError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from app.config.settings import Settings


@pytest.fixture
def configured_client():
    settings = Settings(
        BRIGHTDATA=True,
        BRIGHTDATA_API_KEY="test_api_key",
        BRIGHTDATA_CLI_COMMAND="brightdata",
    )
    return BrightDataClient(settings=settings)


@pytest.mark.asyncio
async def test_create_scraper_success(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (
            0,
            "Creating collector...\nCollector ID: c_m123456789 ready for use\nDone",
            "",
        )

        col_id = await configured_client.create_scraper(
            url="https://example.com/products",
            extraction_description="Extract product name and price",
        )
        assert col_id == "c_m123456789"


@pytest.mark.asyncio
async def test_create_scraper_cli_failure(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (
            1,
            "",
            "Error: Invalid authentication token or quota exceeded",
        )

        with pytest.raises(BrightDataJobError) as exc:
            await configured_client.create_scraper(
                url="https://example.com",
                extraction_description="Extract all",
            )
        assert "Failed to create Bright Data scraper" in str(exc.value)


@pytest.mark.asyncio
async def test_create_scraper_missing_collector_id_in_output(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (
            0,
            "Scraper creation succeeded without identifier output",
            "",
        )

        with pytest.raises(BrightDataJobError) as exc:
            await configured_client.create_scraper(
                url="https://example.com",
                extraction_description="Extract all",
            )
        assert "collector ID was not parsed" in str(exc.value)


@pytest.mark.asyncio
async def test_run_scraper_success(configured_client):
    with patch.object(configured_client, "scrape_via_cli", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = [
            {"product_name": "Laptop", "price": "$999"},
            {"product_name": "Mouse", "price": "$29"},
        ]

        results = await configured_client.run_scraper(
            collector_id="c_m123456789",
            url="https://example.com/tech",
        )
        assert len(results) == 2
        assert results[0]["product_name"] == "Laptop"


@pytest.mark.asyncio
async def test_run_scraper_invalid_collector_id(configured_client):
    with pytest.raises(BrightDataConfigError):
        await configured_client.run_scraper(
            collector_id="invalid_collector",
            url="https://example.com",
        )


@pytest.mark.asyncio
async def test_heal_scraper_success(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (
            0,
            "Collector c_m123456789 healed successfully.",
            "",
        )

        result = await configured_client.heal_scraper(
            collector_id="c_m123456789",
            failure_description="Price selector broke on new layout",
        )
        assert result["status"] == "ready"
        assert result["collector_id"] == "c_m123456789"


@pytest.mark.asyncio
async def test_heal_scraper_failure(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (
            1,
            "",
            "Healing failed: Target domain unreachable",
        )

        with pytest.raises(BrightDataJobError):
            await configured_client.heal_scraper(
                collector_id="c_m123456789",
                failure_description="Broken selectors",
            )


def test_cli_base_command_resolution():
    # 1. Custom multi-token npx prefix
    settings_npx = Settings(BRIGHTDATA_CLI_COMMAND="npx -p @brightdata/cli bdata")
    client_npx = BrightDataClient(settings=settings_npx)
    cmd = client_npx._get_cli_base_command()
    assert cmd[1:4] == ["-p", "@brightdata/cli", "bdata"]

    # 2. Direct binary name
    settings_bdata = Settings(BRIGHTDATA_CLI_COMMAND="bdata")
    client_bdata = BrightDataClient(settings=settings_bdata)
    cmd_bdata = client_bdata._get_cli_base_command()
    assert len(cmd_bdata) >= 1


@pytest.mark.asyncio
async def test_exact_cli_argument_lists(configured_client):
    with patch.object(configured_client, "_execute_cli_subprocess", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = (0, '{"collector_id": "c_exact123", "status": "ready"}', "")

        # 1. Create Scraper
        col_id = await configured_client.create_scraper("https://example.com", "extract titles")
        assert col_id == "c_exact123"
        args_create = mock_exec.call_args_list[0][0][0]
        assert args_create == ["scraper", "create", "https://example.com", "extract titles", "--json"]

        # 2. Heal Scraper
        await configured_client.heal_scraper("c_exact123", "fix price selector")
        args_heal = mock_exec.call_args_list[1][0][0]
        assert args_heal == ["scraper", "heal", "c_exact123", "fix price selector", "--json"]

        # 3. Scrape Via CLI (Run)
        mock_exec.return_value = (0, '[{"title": "Item 1"}]', "")
        await configured_client.scrape_via_cli("c_exact123", "https://example.com")
        args_run = mock_exec.call_args_list[2][0][0]
        assert args_run == ["scraper", "run", "c_exact123", "https://example.com", "--json"]
