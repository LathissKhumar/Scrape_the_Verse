import pytest

from leadfinder.brightdata.adapter import build_collector_inputs
from leadfinder.models.schemas import ScrapingTask


def test_build_collector_inputs_success():
    task = ScrapingTask(
        task_id="t1",
        objective="Scrape shop items",
        target_urls=["https://example.com/item1", "https://example.com/item2"],
        fields=["name", "price"],
        max_records=10,
    )
    inputs = build_collector_inputs(task)
    assert len(inputs) == 2
    assert inputs[0] == {"url": "https://example.com/item1"}
    assert inputs[1] == {"url": "https://example.com/item2"}


def test_build_collector_inputs_empty_urls_raises():
    task = ScrapingTask(
        task_id="t2",
        objective="Scrape shop items",
        target_urls=[],
        fields=["name"],
    )
    with pytest.raises(ValueError) as exc:
        build_collector_inputs(task)
    assert "no target URLs" in str(exc.value)
