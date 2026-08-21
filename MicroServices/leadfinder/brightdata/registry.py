"""Registry managing persistence, URL normalization, and schema fingerprinting for Bright Data Collectors."""

import hashlib
import json
import os
import time
from typing import Any, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from uuid import uuid4

from app.brightdata.schemas import CollectorRecord, CollectorStatus, FieldDefinition
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.crawler.db import get_sqlite_connection, safe_sqlite_transaction

logger = get_logger("BRIGHTDATA_REGISTRY")

_IGNORED_QUERY_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "ref",
    "source",
    "ss",
    "q",
    "query",
    "search",
    "keyword",
    "k",
    "term",
}


def normalize_url(raw_url: str) -> str:
    """Normalize a target URL by lowercasing host, removing tracking/search params, and sorting query keys."""
    url_str = raw_url.strip()
    if not url_str:
        return ""

    lower_raw = url_str.lower()
    if not lower_raw.startswith("http://") and not lower_raw.startswith("https://"):
        url_str = f"https://{url_str}"

    parsed = urlparse(url_str)
    scheme = (parsed.scheme or "https").lower()
    netloc = (parsed.netloc or "").lower()

    # Strip default ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Normalize path
    path = parsed.path or "/"
    if path.startswith("/maps/search"):
        path = "/maps/search"
    elif len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    # Normalize query parameters
    filtered_query: list[tuple[str, str]] = []
    if parsed.query:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        for k, v in sorted(query_pairs):
            if k.lower() not in _IGNORED_QUERY_PARAMS:
                filtered_query.append((k, v))

    clean_query = urlencode(filtered_query)
    return urlunparse((scheme, netloc, path, "", clean_query, ""))


def compute_schema_hash(normalized_url: str, fields: list[Union[FieldDefinition, dict[str, Any]]]) -> str:
    """Compute a deterministic SHA-256 hash representing the target URL and requested extraction schema."""
    canonical_fields: list[dict[str, str]] = []
    for f in fields:
        if isinstance(f, FieldDefinition):
            name = f.name.strip().lower()
            desc = (f.description or "").strip().lower()
        elif isinstance(f, dict):
            name = str(f.get("name", "")).strip().lower()
            desc = str(f.get("description", "")).strip().lower()
        else:
            continue

        if name:
            canonical_fields.append({"name": name, "description": desc})

    canonical_fields.sort(key=lambda item: item["name"])
    serialized = json.dumps(canonical_fields, sort_keys=True, separators=(",", ":"))
    payload = f"{normalized_url}|{serialized}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ScraperRegistry:
    """Thread-safe SQLite repository tracking created Bright Data Collectors."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        settings = get_settings()
        path = db_path or getattr(settings, "BRIGHTDATA_REGISTRY_DB_PATH", ".brightdata_registry.sqlite")
        if not os.path.exists(path) and os.path.exists(os.path.join("app", path)):
            path = os.path.join("app", path)
        self.db_path = path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database table and indexes."""
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS brightdata_scrapers (
                    id TEXT PRIMARY KEY,
                    collector_id TEXT,
                    target_url TEXT NOT NULL,
                    normalized_url TEXT NOT NULL,
                    extraction_schema TEXT NOT NULL,
                    schema_hash TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_used_at REAL,
                    last_run_status TEXT,
                    last_error TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_scrapers_lookup
                ON brightdata_scrapers (normalized_url, schema_hash, status)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_scrapers_collector_id
                ON brightdata_scrapers (collector_id)
                """
            )

    @staticmethod
    def _row_to_record(row: tuple[Any, ...]) -> CollectorRecord:
        schema_json = row[4]
        try:
            extraction_schema = json.loads(schema_json) if schema_json else []
        except Exception:
            extraction_schema = []

        return CollectorRecord(
            id=row[0],
            collector_id=row[1],
            target_url=row[2],
            normalized_url=row[3],
            extraction_schema=extraction_schema,
            schema_hash=row[5],
            description=row[6] or "",
            status=CollectorStatus(row[7]),
            created_at=row[8],
            updated_at=row[9],
            last_used_at=row[10],
            last_run_status=row[11],
            last_error=row[12],
        )

    def find_compatible(self, normalized_url: str, schema_hash: str) -> Optional[CollectorRecord]:
        """Find an existing compatible collector matching target URL and schema hash.

        Returns READY collectors first; if none, returns in-flight CREATING/RUNNING/HEALING collectors
        to prevent duplicate concurrent generation.
        """
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            # 1. Check for READY collectors first
            cursor.execute(
                """
                SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                       schema_hash, description, status, created_at, updated_at,
                       last_used_at, last_run_status, last_error
                FROM brightdata_scrapers
                WHERE normalized_url = ? AND schema_hash = ? AND status = 'READY' AND collector_id IS NOT NULL
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (normalized_url, schema_hash),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)

            # 2. Check for in-progress creations to prevent duplicate generation
            cursor.execute(
                """
                SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                       schema_hash, description, status, created_at, updated_at,
                       last_used_at, last_run_status, last_error
                FROM brightdata_scrapers
                WHERE normalized_url = ? AND schema_hash = ? AND status IN ('CREATING', 'RUNNING', 'HEALING')
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (normalized_url, schema_hash),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)

            return None
        finally:
            conn.close()

    def create_record(
        self,
        target_url: str,
        fields: list[Union[FieldDefinition, dict[str, Any]]],
        description: str = "",
    ) -> CollectorRecord:
        """Create and persist a new scraper record with CREATING status."""
        norm_url = normalize_url(target_url)
        s_hash = compute_schema_hash(norm_url, fields)
        rec_id = f"scraper_{uuid4().hex[:12]}"
        now = time.time()

        canonical_fields = []
        for f in fields:
            if isinstance(f, FieldDefinition):
                canonical_fields.append(f.model_dump())
            elif isinstance(f, dict):
                canonical_fields.append(f)

        schema_json = json.dumps(canonical_fields)

        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO brightdata_scrapers
                (id, collector_id, target_url, normalized_url, extraction_schema,
                 schema_hash, description, status, created_at, updated_at)
                VALUES (?, NULL, ?, ?, ?, ?, ?, 'CREATING', ?, ?)
                """,
                (rec_id, target_url, norm_url, schema_json, s_hash, description, now, now),
            )

        logger.info(f"Created scraper registry record id={rec_id} for target='{norm_url}'")
        return CollectorRecord(
            id=rec_id,
            collector_id=None,
            target_url=target_url,
            normalized_url=norm_url,
            extraction_schema=canonical_fields,
            schema_hash=s_hash,
            description=description,
            status=CollectorStatus.CREATING,
            created_at=now,
            updated_at=now,
        )

    def update_status(
        self,
        record_id: str,
        status: CollectorStatus,
        collector_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[CollectorRecord]:
        """Update collector status and optional collector_id or error message."""
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            if collector_id is not None:
                conn.execute(
                    """
                    UPDATE brightdata_scrapers
                    SET status = ?, collector_id = ?, last_error = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status.value, collector_id, error, now, record_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE brightdata_scrapers
                    SET status = ?, last_error = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status.value, error, now, record_id),
                )

        return self.get_record_by_id(record_id)

    def update_run_metadata(
        self,
        collector_id: str,
        last_run_status: str,
        error: Optional[str] = None,
    ) -> None:
        """Update execution metadata upon collector run."""
        now = time.time()
        with safe_sqlite_transaction(self.db_path) as conn:
            conn.execute(
                """
                UPDATE brightdata_scrapers
                SET last_used_at = ?, last_run_status = ?, last_error = ?, updated_at = ?
                WHERE collector_id = ?
                """,
                (now, last_run_status, error, now, collector_id),
            )

    def get_record_by_id(self, record_id: str) -> Optional[CollectorRecord]:
        """Fetch collector record by internal ID."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                       schema_hash, description, status, created_at, updated_at,
                       last_used_at, last_run_status, last_error
                FROM brightdata_scrapers
                WHERE id = ?
                """,
                (record_id,),
            )
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()

    def get_record_by_collector_id(self, collector_id: str) -> Optional[CollectorRecord]:
        """Fetch collector record by Bright Data Collector ID."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                       schema_hash, description, status, created_at, updated_at,
                       last_used_at, last_run_status, last_error
                FROM brightdata_scrapers
                WHERE collector_id = ?
                LIMIT 1
                """,
                (collector_id,),
            )
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()

    def list_records(
        self,
        limit: int = 50,
        status: Optional[CollectorStatus] = None,
    ) -> list[CollectorRecord]:
        """List tracked collector records with optional status filter."""
        conn = get_sqlite_connection(self.db_path)
        try:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    """
                    SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                           schema_hash, description, status, created_at, updated_at,
                           last_used_at, last_run_status, last_error
                    FROM brightdata_scrapers
                    WHERE status = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (status.value, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, collector_id, target_url, normalized_url, extraction_schema,
                           schema_hash, description, status, created_at, updated_at,
                           last_used_at, last_run_status, last_error
                    FROM brightdata_scrapers
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [self._row_to_record(r) for r in rows]
        finally:
            conn.close()


# Default singleton instance
default_scraper_registry = ScraperRegistry()
