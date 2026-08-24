import pytest
from leadfinder.models.schemas import (
    ScrapingRequest,
    ScrapingResult,
    ScrapingTask,
    validate_http_url,
)
from pydantic import ValidationError


def test_validate_http_url_valid():
    assert validate_http_url("https://example.com") == "https://example.com"
    assert (
        validate_http_url("http://sub.domain.org/path?q=1")
        == "http://sub.domain.org/path?q=1"
    )


def test_validate_http_url_invalid():
    with pytest.raises(ValueError):
        validate_http_url("ftp://example.com")

    with pytest.raises(ValueError):
        validate_http_url("not_a_url")

    with pytest.raises(ValueError):
        validate_http_url("")


def test_scraping_request_valid():
    req = ScrapingRequest(
        query="Scrape products from https://example.com/items",
        max_records=100,
        target_urls=["https://example.com/items"],
    )
    assert req.query == "Scrape products from https://example.com/items"
    assert req.max_records == 100
    assert req.target_urls == ["https://example.com/items"]


def test_scraping_request_defaults():
    req = ScrapingRequest(query="Extract data from provided text")
    assert req.max_records is None
    assert req.target_urls == []


def test_scraping_request_invalid_urls():
    with pytest.raises(ValidationError):
        ScrapingRequest(
            query="Extract data",
            target_urls=["invalid-url-without-scheme"],
        )


def test_scraping_request_invalid_empty_query():
    with pytest.raises(ValidationError):
        ScrapingRequest(query="")


def test_scraping_request_invalid_max_records():
    with pytest.raises(ValidationError):
        ScrapingRequest(query="Extract data", max_records=0)

    with pytest.raises(ValidationError):
        ScrapingRequest(query="Extract data", max_records=-5)


def test_scraping_task_valid():
    task = ScrapingTask(
        task_id="uuid-123",
        objective="Scrape product titles and prices",
        target_urls=["https://example.com/shop"],
        fields=["title", "price"],
        output_schema={"title": "string", "price": "string"},
        max_records=50,
        constraints=["Only in-stock"],
        source_requirements=["JS required"],
    )
    assert task.task_id == "uuid-123"
    assert task.objective == "Scrape product titles and prices"
    assert len(task.target_urls) == 1
    assert task.fields == ["title", "price"]
    assert task.output_schema == {"title": "string", "price": "string"}
    assert task.max_records == 50


def test_scraping_result_valid():
    res = ScrapingResult(
        status="success",
        records=[{"title": "Product A", "price": "$10"}],
        metadata={"duration_ms": 1200},
    )
    assert res.status == "success"
    assert len(res.records) == 1
    assert res.records[0]["title"] == "Product A"
    assert res.error is None


def test_scraping_result_failed_status():
    res = ScrapingResult(
        status="failed",
        records=[],
        error="Blocked by Cloudflare",
    )
    assert res.status == "failed"
    assert res.records == []
    assert res.error == "Blocked by Cloudflare"


def test_scraping_result_invalid_status():
    with pytest.raises(ValidationError):
        ScrapingResult(status="invalid_status", records=[])
