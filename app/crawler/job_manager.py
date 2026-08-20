"""Lightweight crash-safe progress checkpointing and background job execution manager."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4
from pydantic import BaseModel, Field

from app.config.logging import get_logger
from app.crawler.db import get_sqlite_connection, safe_sqlite_transaction
from app.export.exporter import DataExporter

logger = get_logger("JOB_MANAGER")


class JobProgress(BaseModel):
    job_id: str
    status: str = "queued"  # queued, running, completed, failed
    query: str = ""
    total_urls: int = 0
    scraped_urls: int = 0
    failed_urls: int = 0
    total_records: int = 0
    error: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class JobManager:
    """Manages asynchronous scraping jobs, progress tracking, atomic checkpoints, and output export."""

    def __init__(self, db_path: str = ".job_progress.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite tables for jobs and atomic URL checkpoints."""
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scraping_jobs (
                    job_id TEXT PRIMARY KEY,
                    query TEXT,
                    total_urls INTEGER,
                    scraped_urls INTEGER DEFAULT 0,
                    failed_urls INTEGER DEFAULT 0,
                    total_records INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'queued',
                    error TEXT,
                    created_at REAL,
                    updated_at REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT,
                    records_count INTEGER DEFAULT 0,
                    retries INTEGER DEFAULT 0,
                    created_at REAL,
                    UNIQUE(job_id, url)
                )
                """
            )

    def create_job(self, job_id: str, query: str, total_urls: int) -> JobProgress:
        """Register a new job in SQLite."""
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO scraping_jobs
                (job_id, query, total_urls, scraped_urls, failed_urls, total_records, status, error, created_at, updated_at)
                VALUES (?, ?, ?, 0, 0, 0, 'queued', NULL, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET updated_at = excluded.updated_at
                """,
                (job_id, query, total_urls, now, now),
            )
        return JobProgress(job_id=job_id, query=query, total_urls=total_urls, created_at=now, updated_at=now)

    def record_checkpoint(
        self,
        job_id: str,
        url: str,
        status: str,
        records: list[dict[str, Any]],
        retries: int = 0,
    ) -> None:
        """Atomically record a crawled URL checkpoint with its extracted records."""
        now = time.time()
        rec_json = json.dumps(records)
        rec_count = len(records)
        is_success = status == "completed"

        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO job_checkpoints
                (job_id, url, status, result_json, records_count, retries, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id, url) DO UPDATE SET
                    status = excluded.status,
                    result_json = excluded.result_json,
                    records_count = excluded.records_count,
                    retries = excluded.retries,
                    created_at = excluded.created_at
                """,
                (job_id, url, status, rec_json, rec_count, retries, now),
            )

            # Update job progress counter
            if is_success:
                conn.execute(
                    """
                    UPDATE scraping_jobs
                    SET scraped_urls = scraped_urls + 1,
                        total_records = total_records + ?,
                        status = 'running',
                        updated_at = ?
                    WHERE job_id = ?
                    """,
                    (rec_count, now, job_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE scraping_jobs
                    SET failed_urls = failed_urls + 1,
                        status = 'running',
                        updated_at = ?
                    WHERE job_id = ?
                    """,
                    (now, job_id),
                )

    def get_completed_urls(self, job_id: str) -> Set[str]:
        """Return the set of URLs already completed for a job to support resumption."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url FROM job_checkpoints WHERE job_id = ? AND status = 'completed'",
                (job_id,),
            )
            return {row[0] for row in cursor.fetchall()}
        finally:
            conn.close()

    def update_job_status(
        self, job_id: str, status: str, error: Optional[str] = None
    ) -> None:
        """Update overall job status (completed, failed, etc.)."""
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                UPDATE scraping_jobs
                SET status = ?, error = ?, updated_at = ?
                WHERE job_id = ?
                """,
                (status, error, now, job_id),
            )

    def get_job(self, job_id: str) -> Optional[JobProgress]:
        """Get live job progress details."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT job_id, query, total_urls, scraped_urls, failed_urls, total_records, status, error, created_at, updated_at
                FROM scraping_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return JobProgress(
                job_id=row[0],
                query=row[1] or "",
                total_urls=row[2] or 0,
                scraped_urls=row[3] or 0,
                failed_urls=row[4] or 0,
                total_records=row[5] or 0,
                status=row[6] or "queued",
                error=row[7],
                created_at=row[8] or 0.0,
                updated_at=row[9] or 0.0,
            )
        finally:
            conn.close()

    def get_job_records(self, job_id: str) -> List[dict[str, Any]]:
        """Retrieve all extracted records across completed checkpoints for a job."""
        conn = get_sqlite_connection(self.db_path)
        records: List[dict[str, Any]] = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT result_json FROM job_checkpoints WHERE job_id = ? AND status = 'completed'",
                (job_id,),
            )
            for row in cursor.fetchall():
                if row[0]:
                    try:
                        recs = json.loads(row[0])
                        if isinstance(recs, list):
                            records.extend(recs)
                    except Exception:
                        pass
            return records
        finally:
            conn.close()


# Shared singleton instance
default_job_manager = JobManager()
