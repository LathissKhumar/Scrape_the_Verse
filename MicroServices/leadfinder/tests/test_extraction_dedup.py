from leadfinder.extraction.dedup import RecordDeduplicator


def test_deduplication_by_primary_key():
    records = [
        {"url": "https://example.com/p/1", "name": "Item 1", "price": "$10"},
        {"url": "https://example.com/p/1", "name": "Item 1 Duplicate", "price": "$10"},
        {"url": "https://example.com/p/2", "name": "Item 2", "price": "$20"},
    ]
    deduper = RecordDeduplicator()
    result = deduper.deduplicate(records)

    assert len(result) == 2
    assert result[0]["name"] == "Item 1"
    assert result[1]["name"] == "Item 2"


def test_deduplication_by_composite_fields():
    records = [
        {"title": "Book A", "author": "John"},
        {"title": "Book A", "author": "John"},
        {"title": "Book B", "author": "Alice"},
    ]
    deduper = RecordDeduplicator()
    result = deduper.deduplicate(records)

    assert len(result) == 2
