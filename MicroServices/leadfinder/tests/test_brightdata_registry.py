"""Unit tests for ScraperRegistry, URL normalization, and schema hashing."""

import os
import tempfile

import pytest

from leadfinder.brightdata.registry import (
    ScraperRegistry,
    compute_schema_hash,
    normalize_url,
)
from leadfinder.brightdata.schemas import CollectorStatus, FieldDefinition


@pytest.fixture
def temp_registry():
    """Create a fresh ScraperRegistry with a temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name

    registry = ScraperRegistry(db_path=db_path)
    yield registry

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass


def test_normalize_url():
    # Lowercase scheme and domain
    assert normalize_url("HTTP://EXAMPLE.COM/path") == "http://example.com/path"
    # Auto-prepend https
    assert normalize_url("example.com/products") == "https://example.com/products"
    # Remove trailing slash
    assert (
        normalize_url("https://example.com/products/") == "https://example.com/products"
    )
    # Strip tracking parameters
    raw = "https://example.com/products?utm_source=google&category=shoes&utm_medium=cpc&ref=123"
    assert normalize_url(raw) == "https://example.com/products?category=shoes"
    # Sort query parameters
    raw2 = "https://example.com/search?z=1&a=2"
    assert normalize_url(raw2) == "https://example.com/search?a=2&z=1"


def test_compute_schema_hash_deterministic():
    url = "https://example.com/products"
    fields_1 = [
        FieldDefinition(name="price", description="Product price"),
        FieldDefinition(name="title", description="Product title"),
    ]
    fields_2 = [
        FieldDefinition(name="title", description="Product title"),
        FieldDefinition(name="price", description="Product price"),
    ]

    hash_1 = compute_schema_hash(url, fields_1)
    hash_2 = compute_schema_hash(url, fields_2)

    # Order of fields should not change hash
    assert hash_1 == hash_2
    assert len(hash_1) == 64


def test_registry_create_and_find_compatible(temp_registry):
    url = "https://example.com/items"
    fields = [FieldDefinition(name="name", description="Item name")]
    norm_url = normalize_url(url)
    s_hash = compute_schema_hash(norm_url, fields)

    # Initially empty
    assert temp_registry.find_compatible(norm_url, s_hash) is None

    # Create record
    record = temp_registry.create_record(
        target_url=url, fields=fields, description="Extract items"
    )
    assert record.status == CollectorStatus.CREATING
    assert record.collector_id is None
    assert record.schema_hash == s_hash

    # Find compatible returns in-flight record
    found_in_flight = temp_registry.find_compatible(norm_url, s_hash)
    assert found_in_flight is not None
    assert found_in_flight.id == record.id
    assert found_in_flight.status == CollectorStatus.CREATING

    # Transition to READY with collector_id
    updated = temp_registry.update_status(
        record_id=record.id,
        status=CollectorStatus.READY,
        collector_id="c_test123456",
    )
    assert updated.status == CollectorStatus.READY
    assert updated.collector_id == "c_test123456"

    # Find compatible returns ready record
    found_ready = temp_registry.find_compatible(norm_url, s_hash)
    assert found_ready is not None
    assert found_ready.collector_id == "c_test123456"
    assert found_ready.status == CollectorStatus.READY


def test_registry_update_run_metadata(temp_registry):
    record = temp_registry.create_record(
        target_url="https://example.com/test",
        fields=[FieldDefinition(name="f1", description="d1")],
    )
    temp_registry.update_status(
        record_id=record.id,
        status=CollectorStatus.READY,
        collector_id="c_run_test",
    )

    temp_registry.update_run_metadata(
        collector_id="c_run_test",
        last_run_status="success",
    )

    by_col = temp_registry.get_record_by_collector_id("c_run_test")
    assert by_col is not None
    assert by_col.last_run_status == "success"
    assert by_col.last_used_at is not None


def test_registry_list_records(temp_registry):
    temp_registry.create_record("https://site1.com", [FieldDefinition(name="a")])
    r2 = temp_registry.create_record("https://site2.com", [FieldDefinition(name="b")])
    temp_registry.update_status(r2.id, CollectorStatus.READY, collector_id="c_site2")

    all_records = temp_registry.list_records()
    assert len(all_records) == 2

    ready_records = temp_registry.list_records(status=CollectorStatus.READY)
    assert len(ready_records) == 1
    assert ready_records[0].collector_id == "c_site2"
