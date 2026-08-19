from app.graph.state import ScrapingGraphState
from app.models.schemas import ScrapingResult, ScrapingTask


def test_scraping_graph_state_instantiation():
    task = ScrapingTask(
        task_id="task-uuid-1",
        objective="Scrape product listings",
        target_urls=["https://example.com/products"],
        fields=["name", "price"],
    )

    state: ScrapingGraphState = {
        "task_id": "task-uuid-1",
        "original_user_query": "Scrape products from https://example.com/products",
        "scraping_task": task,
        "target_urls": ["https://example.com/products"],
        "scraper_id": "collector_123",
        "scraper_version": "v1.0",
        "scraper_code": "function extract() {}",
        "raw_results": [{"html": "<div>Product</div>"}],
        "extracted_results": [{"name": "Item 1", "price": "$10"}],
        "validation_result": {"is_valid": True, "score": 1.0},
        "failure": None,
        "repair_attempt": 0,
        "final_output": ScrapingResult(
            status="success",
            records=[{"name": "Item 1", "price": "$10"}],
        ),
    }

    assert state["task_id"] == "task-uuid-1"
    assert state["scraping_task"] is not None
    assert state["scraping_task"].task_id == "task-uuid-1"
    assert state["repair_attempt"] == 0
    assert state["final_output"] is not None
    assert state["final_output"].status == "success"


def test_scraping_graph_state_partial():
    # TypedDict total=False allows initial partial state
    state: ScrapingGraphState = {
        "task_id": "task-uuid-2",
        "original_user_query": "Scrape catalog",
        "target_urls": ["https://example.com"],
    }
    assert state["task_id"] == "task-uuid-2"
    assert state["target_urls"] == ["https://example.com"]
