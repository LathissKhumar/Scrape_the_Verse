from unittest.mock import AsyncMock, MagicMock
import pytest
from leadfinder.crawler.pagination_walker import PaginationWalkerEngine


@pytest.mark.asyncio
async def test_pagination_walker_clicks_next():
    mock_page = MagicMock()
    mock_btn = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=mock_btn)
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    walker = PaginationWalkerEngine()
    advanced = await walker.advance_page(mock_page)
    assert advanced is True
    mock_btn.click.assert_called_once()


@pytest.mark.asyncio
async def test_pagination_walker_handles_no_next_button():
    mock_page = MagicMock()
    mock_page.query_selector = AsyncMock(return_value=None)
    mock_page.evaluate = AsyncMock(return_value=1000)
    mock_page.wait_for_timeout = AsyncMock()

    walker = PaginationWalkerEngine()
    advanced = await walker.advance_page(mock_page)
    assert advanced is True
    mock_page.evaluate.assert_called_once()
