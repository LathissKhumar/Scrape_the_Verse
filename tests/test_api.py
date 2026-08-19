import pytest
from unittest.mock import AsyncMock, patch

from app.llm.exceptions import LLMConnectionError
from app.models.schemas import ScrapingResult, ScrapingTask


def test_get_root(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "self-healing-scraper"
    assert data["status"] == "running"
    assert data["phase"] == 2


def test_get_health(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ollama_model" in data
    assert "brightdata_configured" in data


def test_get_health_llm_available(api_client):
    with patch(
        "app.main.llm_client.check_health",
        new_callable=AsyncMock,
        return_value={"available": True, "model_installed": True, "model_name": "qwen3:8b"},
    ):
        response = api_client.get("/health/llm")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert data["model_installed"] is True


def test_get_health_llm_unavailable(api_client):
    with patch(
        "app.main.llm_client.check_health",
        new_callable=AsyncMock,
        return_value={"available": False, "model_installed": False, "error": "Cannot connect"},
    ):
        response = api_client.get("/health/llm")
        assert response.status_code == 503
        data = response.json()
        assert data["available"] is False


def test_post_parse_task_success(api_client):
    mock_task = ScrapingTask(
        task_id="injected-uuid",
        objective="Scrape product listings",
        target_urls=["https://example.com/products"],
        fields=["name", "price"],
        output_schema={"name": "string", "price": "string"},
        max_records=100,
    )

    with patch("app.main.planner_agent.plan_async", new_callable=AsyncMock, return_value=mock_task):
        payload = {
            "query": "Scrape https://example.com/products and collect name and price",
            "target_urls": ["https://example.com/products"],
            "max_records": 100,
        }
        response = api_client.post("/parse-task", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["scraping_task"]["objective"] == "Scrape product listings"
        assert data["scraping_task"]["target_urls"] == ["https://example.com/products"]
        assert data["scraping_task"]["fields"] == ["name", "price"]


def test_post_parse_task_llm_connection_error(api_client):
    with patch(
        "app.main.planner_agent.plan_async",
        side_effect=LLMConnectionError("Ollama service unreachable"),
    ):
        payload = {"query": "Scrape items"}
        response = api_client.post("/parse-task", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert data["error_type"] == "LLMConnectionError"


def test_post_parse_task_invalid_input(api_client):
    # Empty query
    response = api_client.post("/parse-task", json={"query": ""})
    assert response.status_code == 422

    # Invalid URL scheme
    response = api_client.post(
        "/parse-task",
        json={"query": "Scrape", "target_urls": ["ftp://invalid.com"]},
    )
    assert response.status_code == 422


def test_post_scrape_success(api_client):
    mock_result_state = {
        "final_output": ScrapingResult(
            status="success",
            records=[{"title": "Product 1", "price": "$50"}],
            metadata={"record_count": 1},
        )
    }

    with patch("app.main.workflow.ainvoke", new_callable=AsyncMock, return_value=mock_result_state):
        payload = {
            "query": "Scrape product names and prices from the provided website",
            "target_urls": ["https://example.com/products"],
            "max_records": 20,
        }
        response = api_client.post("/scrape", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["records"]) == 1
        assert data["records"][0]["title"] == "Product 1"
        assert "task_id" in data


def test_post_scrape_missing_target_url_returns_400(api_client):
    payload = {
        "query": "Scrape product names and prices without providing any URL",
        "target_urls": [],
    }
    response = api_client.post("/scrape", json=payload)
    assert response.status_code == 400
    assert "No target URL was supplied" in response.json()["detail"]


def test_post_scrape_url_in_query_accepted(api_client):
    mock_result_state = {
        "final_output": ScrapingResult(
            status="success",
            records=[{"title": "Headline", "points": "120"}],
            metadata={"record_count": 1},
        )
    }

    with patch("app.main.workflow.ainvoke", new_callable=AsyncMock, return_value=mock_result_state):
        payload = {
            "query": "Scrape from https://news.ycombinator.com the front page",
        }
        response = api_client.post("/scrape", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["records"]) == 1
