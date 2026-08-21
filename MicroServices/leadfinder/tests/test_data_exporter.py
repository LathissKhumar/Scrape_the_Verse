import json
import pytest
from leadfinder.export.exporter import DataExporter


def test_data_exporter_to_csv():
    records = [
        {"title": "Book 1", "price": "$10"},
        {"title": "Book 2", "price": "$20"},
    ]
    csv_str = DataExporter.to_csv(records)
    assert "title,price" in csv_str
    assert "Book 1,$10" in csv_str
    assert "Book 2,$20" in csv_str


def test_data_exporter_to_json():
    records = [{"title": "Book 1", "price": "$10"}]
    json_str = DataExporter.to_json(records)
    parsed = json.loads(json_str)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "Book 1"


def test_data_exporter_to_ndjson():
    records = [
        {"title": "Book 1", "price": "$10"},
        {"title": "Book 2", "price": "$20"},
    ]
    ndjson_str = DataExporter.to_ndjson(records)
    lines = [line for line in ndjson_str.split("\n") if line.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["title"] == "Book 1"


def test_data_exporter_empty():
    assert DataExporter.to_csv([]) == ""
    assert DataExporter.to_json([]) == "[]"
    assert DataExporter.to_ndjson([]) == ""
