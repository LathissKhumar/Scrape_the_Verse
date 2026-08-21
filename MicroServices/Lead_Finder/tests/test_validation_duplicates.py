from leadfinder.validation.duplicates import DuplicateValidator


def test_duplicate_validator_clean():
    validator = DuplicateValidator()
    records = [
        {"url": "https://example.com/1", "name": "A"},
        {"url": "https://example.com/2", "name": "B"},
        {"url": "https://example.com/3", "name": "C"},
    ]
    metrics = validator.evaluate_duplicates(records)
    assert metrics.total_records == 3
    assert metrics.unique_records == 3
    assert metrics.duplicate_records == 0
    assert metrics.duplicate_rate == 0.0


def test_duplicate_validator_with_duplicates():
    validator = DuplicateValidator()
    records = [
        {"url": "https://example.com/1", "name": "A"},
        {"url": "https://example.com/1", "name": "A"},
        {"url": "https://example.com/2", "name": "B"},
        {"url": "https://example.com/2", "name": "B"},
    ]
    metrics = validator.evaluate_duplicates(records)
    assert metrics.total_records == 4
    assert metrics.unique_records == 2
    assert metrics.duplicate_records == 2
    assert metrics.duplicate_rate == 0.5
