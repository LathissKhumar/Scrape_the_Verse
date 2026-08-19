from app.validation.completeness import CompletenessValidator


def test_completeness_perfect_coverage():
    validator = CompletenessValidator()
    records = [
        {"title": "Item 1", "price": "$10"},
        {"title": "Item 2", "price": "$20"},
    ]
    metrics = validator.evaluate_all(records, ["title", "price"])

    assert metrics["title"].coverage == 1.0
    assert metrics["title"].valid_count == 2
    assert metrics["title"].empty_count == 0
    assert metrics["price"].coverage == 1.0


def test_completeness_placeholders_and_empty():
    validator = CompletenessValidator()
    records = [
        {"name": "Alice", "phone": "123-456", "email": "alice@example.com"},
        {"name": "Bob", "phone": "N/A", "email": ""},
        {"name": "Charlie", "phone": "unknown", "email": None},
        {"name": "David", "phone": "456-789", "email": "-"},
    ]
    metrics = validator.evaluate_all(records, ["name", "phone", "email"])

    # Phone: 2 valid, 2 placeholders
    assert metrics["phone"].coverage == 0.5
    assert metrics["phone"].valid_count == 2
    assert metrics["phone"].placeholder_count == 2

    # Email: 1 valid, 2 empty, 1 placeholder
    assert metrics["email"].coverage == 0.25
    assert metrics["email"].valid_count == 1
    assert metrics["email"].empty_count == 2
    assert metrics["email"].placeholder_count == 1
