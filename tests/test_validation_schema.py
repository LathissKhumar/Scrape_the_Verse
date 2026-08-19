from app.validation.type_validator import TypeValidator


def test_type_validator_primitive_types():
    validator = TypeValidator()

    # Strings
    assert validator.validate_value("Hello", "string") is True
    assert validator.validate_value(123, "string") is True

    # Integers
    assert validator.validate_value(42, "integer") is True
    assert validator.validate_value("1,000", "integer") is True
    assert validator.validate_value("abc", "integer") is False
    assert validator.validate_value(True, "integer") is False

    # Floats / Numbers
    assert validator.validate_value(19.99, "number") is True
    assert validator.validate_value("$19.99", "number") is True
    assert validator.validate_value("invalid", "number") is False

    # Booleans
    assert validator.validate_value(True, "boolean") is True
    assert validator.validate_value("true", "boolean") is True
    assert validator.validate_value("no", "boolean") is True

    # Emails
    assert validator.validate_value("user@example.com", "email") is True
    assert validator.validate_value("not-an-email", "email") is False

    # URLs
    assert validator.validate_value("https://example.com", "url") is True
    assert validator.validate_value("ftp://example.com", "url") is False

    # Dates
    assert validator.validate_value("2026-08-19", "date") is True
    assert validator.validate_value("Aug 19, 2026", "date") is True
    assert validator.validate_value("not-a-date", "date") is False


def test_validate_records_schema():
    validator = TypeValidator()
    records = [
        {"name": "Alpha", "price": "$10", "in_stock": "true"},
        {"name": "Beta", "price": "invalid_num", "in_stock": "yes"},
    ]
    output_schema = {"name": "string", "price": "number", "in_stock": "boolean"}

    metric = validator.validate_records_schema(records, output_schema)
    assert metric.valid_records == 1
    assert metric.invalid_records == 1
    assert metric.valid_rate == 0.5
