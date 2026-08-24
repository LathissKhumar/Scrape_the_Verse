import asyncio
import os
import tempfile
import threading
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from leadfinder.agents.scraper import ScraperAgent
from leadfinder.crawler.browser_manager import BrowserManager
from leadfinder.crawler.config import CrawlerConfig
from leadfinder.crawler.job_manager import JobManager
from leadfinder.crawler.rate_limiter import DomainRateLimiter
from leadfinder.crawler.result_models import BlockType, CrawlResult
from leadfinder.export.exporter import DataExporter
from leadfinder.healing.persistent_memory import PersistentRepairMemory
from leadfinder.healing.schemas import (
    RepairMemoryRecord,
    RepairType,
)


@pytest.mark.asyncio
async def test_bounded_browser_concurrency_semaphore():
    """Verify that ScraperAgent strictly limits concurrent crawls to max_concurrency."""
    mock_executor = MagicMock()
    mock_executor.config = CrawlerConfig(max_concurrency=3)

    active_concurrent = 0
    max_observed_concurrent = 0
    lock = asyncio.Lock()

    async def mock_crawl(url: str):
        nonlocal active_concurrent, max_observed_concurrent
        async with lock:
            active_concurrent += 1
            max_observed_concurrent = max(max_observed_concurrent, active_concurrent)

        # Simulate network delay
        await asyncio.sleep(0.05)

        async with lock:
            active_concurrent -= 1

        return CrawlResult(
            url=url,
            html="<html><body>Mock</body></html>",
            status_code=200,
            blocked=False,
            block_type=BlockType.NONE,
        )

    mock_executor.crawl = AsyncMock(side_effect=mock_crawl)
    scraper = ScraperAgent(browser_executor=mock_executor)

    urls = [f"https://example.com/item/{i}" for i in range(20)]
    results = await scraper._execute_browser_scrape(urls, max_concurrency=3)

    assert len(results) == 20
    # Concurrency must never have exceeded the semaphore bound of 3
    assert max_observed_concurrent <= 3
    # Result ordering must be preserved
    assert results[0]["url"] == "https://example.com/item/0"
    assert results[19]["url"] == "https://example.com/item/19"


def test_sqlite_wal_and_concurrent_writes():
    """Verify multi-threaded concurrent write resilience without database locked errors."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        db_path = tmp.name

    try:
        mem = PersistentRepairMemory(db_path=db_path)
        errors = []

        def worker_write(idx: int):
            try:
                rec = RepairMemoryRecord(
                    domain=f"domain{idx % 5}.com",
                    signature=f"sig_{idx}",
                    root_cause="SELECTOR_DRIFT",
                    repair_type=RepairType.REPAIR_CSS_SELECTORS,
                    strategy="css",
                    successful_patch={"field": f".selector_{idx}"},
                    health_before=0.2,
                    health_after=0.9,
                )
                mem.record_success(rec)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker_write, args=(i,)) for i in range(25)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Zero database is locked exceptions allowed
        assert len(errors) == 0

        # Verify items were persisted
        record = mem.lookup("domain0.com", "sig_0")
        assert record is not None
        assert record.repair_type == RepairType.REPAIR_CSS_SELECTORS
    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass


def test_job_checkpointing_and_resumption():
    """Verify atomic progress checkpointing, progress inspection, and resumption."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        db_path = tmp.name

    try:
        jm = JobManager(db_path=db_path)
        job_id = "test_job_123"
        jm.create_job(job_id=job_id, query="scrape products", total_urls=10)

        # Checkpoint URL 1 and 2
        jm.record_checkpoint(
            job_id=job_id,
            url="https://example.com/1",
            status="completed",
            records=[{"title": "Item 1"}],
        )
        jm.record_checkpoint(
            job_id=job_id,
            url="https://example.com/2",
            status="completed",
            records=[{"title": "Item 2"}],
        )
        jm.record_checkpoint(
            job_id=job_id,
            url="https://example.com/3",
            status="failed",
            records=[],
            retries=1,
        )

        completed = jm.get_completed_urls(job_id)
        assert "https://example.com/1" in completed
        assert "https://example.com/2" in completed
        assert "https://example.com/3" not in completed

        progress = jm.get_job(job_id)
        assert progress is not None
        assert progress.scraped_urls == 2
        assert progress.failed_urls == 1
        assert progress.total_records == 2

        records = jm.get_job_records(job_id)
        assert len(records) == 2
        assert records[0]["title"] == "Item 1"

        # Verify export formats
        csv_out = DataExporter.to_csv(records)
        assert "Item 1" in csv_out
        ndjson_out = DataExporter.to_ndjson(records)
        assert "Item 2" in ndjson_out
    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass


@pytest.mark.asyncio
async def test_rate_limiter_jitter_and_slots():
    """Verify rate limiter enforces backoff with jitter and per-domain slot context manager."""
    limiter = DomainRateLimiter(requests_per_second=100.0, default_backoff_seconds=0.1)
    url = "https://ratelimited.com/api"

    limiter.record_429(url, retry_after_seconds=0.05)
    assert limiter.is_rate_limited(url) is True

    # Wait for jittered backoff to expire
    await asyncio.sleep(0.1)
    assert limiter.is_rate_limited(url) is False

    # Verify slot context manager
    async with limiter.slot(url):
        pass


@pytest.mark.asyncio
async def test_browser_manager_crash_detection():
    """Verify BrowserManager detects disconnected browser and transparently relaunches."""
    mgr = BrowserManager()
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = False
    mgr._browser = mock_browser

    with patch("leadfinder.crawler.browser_manager.async_playwright") as mock_pw:
        mock_pw_inst = AsyncMock()
        mock_new_browser = MagicMock()
        mock_new_browser.is_connected.return_value = True
        mock_pw_inst.chromium.launch = AsyncMock(return_value=mock_new_browser)
        mock_pw.return_value.start = AsyncMock(return_value=mock_pw_inst)

        browser = await mgr.get_browser()
        assert browser == mock_new_browser
        assert mgr._browser == mock_new_browser


def test_observability_tail_loader():
    """Verify RepairObservability loads only tail lines without loading full file."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as tmp:
        tmp_path = tmp.name

    try:
        from leadfinder.healing.observability import (
            RepairObservability,
            RepairSessionTelemetry,
        )

        obs = RepairObservability(log_path=tmp_path)
        for i in range(20):
            obs.record_session(
                RepairSessionTelemetry(
                    task_id=f"t_{i}",
                    domain=f"domain_{i}.com",
                    root_cause="SELECTOR_DRIFT",
                    initial_health=0.2,
                    final_health=0.9,
                    improvement=0.7,
                    accepted=True,
                )
            )

        # Test tail reading of only last 5 sessions
        tail = obs.load_all_persisted_sessions(limit=5)
        assert len(tail) == 5
        assert tail[-1].domain == "domain_19.com"
        assert tail[0].domain == "domain_15.com"
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
