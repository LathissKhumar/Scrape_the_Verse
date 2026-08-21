import pytest
from unittest.mock import AsyncMock, MagicMock

from app.crawler.link_discovery import LinkDiscoveryEngine
from app.crawler.result_models import CrawlResult
from app.extraction.engine import ExtractionEngine
from app.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_conditional_child_crawling_when_fields_missing():
    # Primary page has title & price, but is missing 'specifications'
    primary_html = """
    <html>
      <body>
        <h1 class="title">Awesome Laptop</h1>
        <span class="price">$999</span>
        <a href="/specs/laptop-details">View Full Tech Specifications</a>
      </body>
    </html>
    """

    child_html = """
    <html>
      <body>
        <div class="tech-specs">
          <p>Processor: M2 Max</p>
          <p>RAM: 32GB</p>
        </div>
      </body>
    </html>
    """

    task = ScrapingTask(
        task_id="test_task",
        target_urls=["https://example.com/laptop"],
        fields=["title", "price", "specifications"],
        objective="Extract laptop info and specs",
    )

    mock_browser_executor = MagicMock()
    mock_browser_executor.crawl = AsyncMock(return_value=CrawlResult(
        url="https://example.com/specs/laptop-details",
        final_url="https://example.com/specs/laptop-details",
        html=child_html,
        status_code=200,
    ))

    engine = ExtractionEngine(
        browser_executor=mock_browser_executor,
        link_discovery=LinkDiscoveryEngine(),
    )

    # Mock extract_async on LLM/Regex to simulate primary extraction missing 'specifications'
    result = await engine.extract_async(
        raw_content=[{"url": "https://example.com/laptop", "html": primary_html}],
        task=task,
    )

    # Verify that child link was discovered and crawled
    mock_browser_executor.crawl.assert_called_once_with(url="https://example.com/specs/laptop-details")


@pytest.mark.asyncio
async def test_no_child_crawling_when_all_fields_present():
    # Primary page already has all requested fields
    primary_html = """
    <html>
      <body>
        <h1>Awesome Laptop</h1>
        <p>Price: $999</p>
        <a href="/specs/laptop-details">View Details</a>
      </body>
    </html>
    """

    task = ScrapingTask(
        task_id="test_task_full",
        target_urls=["https://example.com/laptop"],
        fields=["price"],
        objective="Extract laptop price",
    )

    mock_browser_executor = MagicMock()
    mock_browser_executor.crawl = AsyncMock()

    engine = ExtractionEngine(
        browser_executor=mock_browser_executor,
        link_discovery=LinkDiscoveryEngine(),
    )

    result = await engine.extract_async(
        raw_content=[{"url": "https://example.com/laptop", "html": primary_html}],
        task=task,
    )

    # Verify child crawl was NOT triggered because all fields were already found!
    mock_browser_executor.crawl.assert_not_called()
    assert len(result.records) > 0
