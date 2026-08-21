from app.graph.state import ScrapingGraphState
from app.models.schemas import ScrapingTask


def test_scraping_task_navigation_fields():
    task = ScrapingTask(
        task_id="t_nav_1",
        objective="Search redmi phones on flipkart",
        target_urls=["https://www.flipkart.com"],
        fields=["name", "price", "specs"],
        is_search=True,
        search_keyword="redmi",
        deep_crawl=True,
        max_detail_pages=15,
        filters={"brand": "Redmi"},
    )
    assert task.is_search is True
    assert task.search_keyword == "redmi"
    assert task.deep_crawl is True
    assert task.max_detail_pages == 15
    assert task.filters == {"brand": "Redmi"}
