"""Background job coordinator for asynchronous Bright Data Collector creation."""

import asyncio
import os
import time
from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

from leadfinder.brightdata.registry import ScraperRegistry, default_scraper_registry
from leadfinder.brightdata.schemas import CollectorJobRecord, CollectorStatus
from leadfinder.config.logging import get_logger
from leadfinder.config.settings import get_settings
from leadfinder.crawler.db import get_sqlite_connection, safe_sqlite_transaction

logger = get_logger("BRIGHTDATA_JOBS")


class ScraperJobManager:
    """Manages asynchronous background scraper creation jobs with SQLite persistence."""

    def __init__(
        self,
        db_path: str | None = None,
        registry: ScraperRegistry | None = None,
    ) -> None:
        settings = get_settings()
        path = db_path or getattr(
            settings, "BRIGHTDATA_REGISTRY_DB_PATH", ".brightdata_registry.sqlite"
        )
        if not os.path.exists(path) and os.path.exists(os.path.join("app", path)):
            path = os.path.join("app", path)
        self.db_path = path
        self.registry = registry or default_scraper_registry
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite table for creation jobs."""
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS brightdata_creation_jobs (
                    job_id TEXT PRIMARY KEY,
                    scraper_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    collector_id TEXT,
                    error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_scraper_status
                ON brightdata_creation_jobs (scraper_id, status)
                """
            )

    @staticmethod
    def _row_to_job(row: tuple[Any, ...]) -> CollectorJobRecord:
        return CollectorJobRecord(
            job_id=row[0],
            scraper_id=row[1],
            status=CollectorStatus(row[2]),
            collector_id=row[3],
            error=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def create_job(
        self, scraper_id: str, job_id: str | None = None
    ) -> CollectorJobRecord:
        """Create a new job record in CREATING state."""
        jid = job_id or f"job_{uuid4().hex[:12]}"
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO brightdata_creation_jobs
                (job_id, scraper_id, status, collector_id, error, created_at, updated_at)
                VALUES (?, ?, 'CREATING', NULL, NULL, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET updated_at = excluded.updated_at
                """,
                (jid, scraper_id, now, now),
            )
        return CollectorJobRecord(
            job_id=jid,
            scraper_id=scraper_id,
            status=CollectorStatus.CREATING,
            created_at=now,
            updated_at=now,
        )

    def update_job(
        self,
        job_id: str,
        status: CollectorStatus,
        collector_id: str | None = None,
        error: str | None = None,
    ) -> CollectorJobRecord | None:
        """Update job status, collector ID, or error message."""
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            if collector_id is not None:
                conn.execute(
                    """
                    UPDATE brightdata_creation_jobs
                    SET status = ?, collector_id = ?, error = ?, updated_at = ?
                    WHERE job_id = ?
                    """,
                    (status.value, collector_id, error, now, job_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE brightdata_creation_jobs
                    SET status = ?, error = ?, updated_at = ?
                    WHERE job_id = ?
                    """,
                    (status.value, error, now, job_id),
                )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> CollectorJobRecord | None:
        """Fetch job progress record by job ID."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT job_id, scraper_id, status, collector_id, error, created_at, updated_at
                FROM brightdata_creation_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            )
            row = cursor.fetchone()
            return self._row_to_job(row) if row else None
        finally:
            conn.close()

    def find_active_job_for_scraper(self, scraper_id: str) -> CollectorJobRecord | None:
        """Find any currently running or in-progress creation job for a given scraper ID."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT job_id, scraper_id, status, collector_id, error, created_at, updated_at
                FROM brightdata_creation_jobs
                WHERE scraper_id = ? AND status IN ('CREATING', 'RUNNING')
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (scraper_id,),
            )
            row = cursor.fetchone()
            return self._row_to_job(row) if row else None
        finally:
            conn.close()

    def start_creation_worker(
        self,
        job_id: str,
        scraper_id: str,
        create_coro_factory: Callable[[], Coroutine[Any, Any, str]],
    ) -> asyncio.Task:
        """Launch background asyncio task executing scraper creation and persisting result."""

        async def _worker() -> None:
            logger.info(
                f"SCRAPER_CREATION_STARTED job_id={job_id} scraper_id={scraper_id}"
            )
            try:
                collector_id = await create_coro_factory()
                if not collector_id or not collector_id.startswith("c_"):
                    raise ValueError(
                        f"Invalid Bright Data Collector ID returned: '{collector_id}'"
                    )

                # Update registry & job record to READY
                self.registry.update_status(
                    record_id=scraper_id,
                    status=CollectorStatus.READY,
                    collector_id=collector_id,
                )
                self.update_job(
                    job_id=job_id,
                    status=CollectorStatus.READY,
                    collector_id=collector_id,
                )
                logger.info(
                    f"SCRAPER_CREATION_COMPLETED job_id={job_id} scraper_id={scraper_id} collector_id={collector_id}"
                )
            except Exception as exc:
                err_msg = str(exc)
                logger.error(
                    f"SCRAPER_CREATION_FAILED job_id={job_id} scraper_id={scraper_id} error={err_msg}"
                )
                self.registry.update_status(
                    record_id=scraper_id,
                    status=CollectorStatus.FAILED,
                    error=err_msg,
                )
                self.update_job(
                    job_id=job_id,
                    status=CollectorStatus.FAILED,
                    error=err_msg,
                )

        task = asyncio.create_task(_worker())
        return task


# Default singleton instance
default_job_manager = ScraperJobManager()
