from app.validation.urls import URLValidator


def test_url_validator_all_valid():
    validator = URLValidator()
    records = [
        {"product_url": "https://example.com/p1"},
        {"product_url": "https://example.com/p2"},
    ]
    metrics = validator.evaluate_urls(records, ["product_url"])
    assert metrics.total_urls == 2
    assert metrics.valid_urls == 2
    assert metrics.invalid_urls == 0
    assert metrics.valid_rate == 1.0


def test_url_validator_mixed():
    validator = URLValidator()
    records = [
        {"product_url": "https://example.com/valid"},
        {"product_url": "ftp://not-http.com"},
        {"product_url": "not a url"},
        {"product_url": "http://sub.domain.org/path?q=1"},
    ]
    metrics = validator.evaluate_urls(records, ["product_url"])
    assert metrics.total_urls == 4
    assert metrics.valid_urls == 2
    assert metrics.invalid_urls == 2
    assert metrics.valid_rate == 0.5
