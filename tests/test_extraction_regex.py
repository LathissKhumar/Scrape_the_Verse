from app.extraction.regex import RegexExtractor
from app.extraction.schema import ExtractionSchema, FieldRule, RawPage


def test_regex_extraction_common_patterns():
    text = """
    Contact us at support@example.com or sales@example.org.
    Phone lines: 123-456-7890 or 987-654-3210.
    Standard price is $49.99, discounted to $29.99 today.
    """
    schema = ExtractionSchema(
        fields=[
            FieldRule(name="email"),
            FieldRule(name="phone"),
            FieldRule(name="price"),
        ]
    )

    extractor = RegexExtractor()
    records = extractor.extract(text, schema)

    assert len(records) >= 2
    emails = [r["email"] for r in records if r.get("email")]
    assert "support@example.com" in emails
    assert "sales@example.org" in emails


def test_regex_extraction_custom_pattern():
    text = "Order IDs are ORD-1001, ORD-1002, and ORD-1003."
    schema = ExtractionSchema(
        fields=[
            FieldRule(name="order_id", regex_pattern=r"ORD-\d{4}"),
        ]
    )

    extractor = RegexExtractor()
    records = extractor.extract(text, schema)

    assert len(records) == 3
    assert records[0]["order_id"] == "ORD-1001"
    assert records[1]["order_id"] == "ORD-1002"
    assert records[2]["order_id"] == "ORD-1003"
