from unittest.mock import AsyncMock, MagicMock
import pytest
from leadfinder.crawler.navigator import InteractiveNavigatorEngine


@pytest.mark.asyncio
async def test_navigator_finds_and_types_search():
    mock_page = MagicMock()
    mock_input = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=mock_input)
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    navigator = InteractiveNavigatorEngine()
    success = await navigator.search(mock_page, query="redmi 13c")
    assert success is True
    mock_input.fill.assert_called_once_with("redmi 13c")
    mock_input.press.assert_called_once_with("Enter")


@pytest.mark.asyncio
async def test_navigator_handles_no_search_input():
    mock_page = MagicMock()
    mock_page.query_selector = AsyncMock(return_value=None)
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    navigator = InteractiveNavigatorEngine()
    success = await navigator.search(mock_page, query="redmi 13c")
    assert success is False
