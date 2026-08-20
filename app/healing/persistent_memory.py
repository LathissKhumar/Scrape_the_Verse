"""SQLite-backed persistent repair memory for instant repeat self-healing with freshness lifecycle."""

import json
import time
from typing import Optional

from app.config.logging import get_logger
from app.crawler.db import get_sqlite_connection, safe_sqlite_transaction
from app.healing.schemas import (
    RepairConfidenceLevel,
    RepairFreshnessStatus,
    RepairMemoryRecord,
    RepairType,
)

logger = get_logger("PERSISTENT_REPAIR_MEMORY")


class PersistentRepairMemory:
    """SQLite-backed persistent repair memory for instant repeat self-healing with freshness lifecycle."""

    def __init__(self, db_path: str = ".repair_memory.sqlite") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite table for persistent repair records with automatic column migration."""
        try:
            with safe_sqlite_transaction(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS repair_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memory_id TEXT,
                        domain TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        root_cause TEXT NOT NULL,
                        repair_type TEXT NOT NULL,
                        successful_patch TEXT NOT NULL,
                        health_before REAL,
                        health_after REAL,
                        strategy TEXT NOT NULL,
                        provider TEXT DEFAULT 'local',
                        status TEXT DEFAULT 'active',
                        confidence_level TEXT DEFAULT 'high',
                        success_count INTEGER DEFAULT 1,
                        failure_count INTEGER DEFAULT 0,
                        last_used_at REAL,
                        structural_fingerprint TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(domain, signature)
                    )
                    """
                )
                # Auto-migrate missing columns if table existed previously with old schema
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(repair_memory)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                for col, col_type in [
                    ("memory_id", "TEXT"),
                    ("root_cause", "TEXT DEFAULT 'UNKNOWN'"),
                    ("strategy", "TEXT DEFAULT 'css'"),
                    ("provider", "TEXT DEFAULT 'local'"),
                    ("health_before", "REAL"),
                    ("health_after", "REAL"),
                    ("successful_patch", "TEXT DEFAULT '{}'"),
                    ("status", "TEXT DEFAULT 'active'"),
                    ("confidence_level", "TEXT DEFAULT 'high'"),
                    ("success_count", "INTEGER DEFAULT 1"),
                    ("failure_count", "INTEGER DEFAULT 0"),
                    ("last_used_at", "REAL"),
                    ("structural_fingerprint", "TEXT"),
                ]:
                    if col not in existing_cols:
                        conn.execute(f"ALTER TABLE repair_memory ADD COLUMN {col} {col_type}")
        except Exception as error:
            logger.warning(f"Could not initialize SQLite persistent repair memory: {error}")

    def record_success(self, record: RepairMemoryRecord) -> None:
        """Persist or update a verified working repair record into SQLite database."""
        try:
            now = time.time()
            with safe_sqlite_transaction(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO repair_memory
                    (memory_id, domain, signature, root_cause, repair_type, successful_patch, health_before, health_after, strategy, provider, status, confidence_level, success_count, failure_count, last_used_at, structural_fingerprint)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(domain, signature) DO UPDATE SET
                        successful_patch = excluded.successful_patch,
                        health_after = excluded.health_after,
                        status = 'active',
                        confidence_level = excluded.confidence_level,
                        success_count = repair_memory.success_count + 1,
                        failure_count = 0,
                        last_used_at = excluded.last_used_at,
                        structural_fingerprint = excluded.structural_fingerprint
                    """,
                    (
                        record.memory_id,
                        record.domain,
                        record.signature,
                        record.root_cause,
                        record.repair_type.value,
                        json.dumps(record.successful_patch),
                        record.health_before,
                        record.health_after,
                        record.strategy,
                        record.provider,
                        record.status.value,
                        record.confidence_level.value,
                        record.success_count,
                        record.failure_count,
                        now,
                        record.structural_fingerprint,
                    ),
                )
                logger.debug(
                    f"Persistent repair stored in SQLite for domain={record.domain} sig={record.signature} (status={record.status.value}, confidence={record.confidence_level.value})"
                )
        except Exception as error:
            logger.error(f"Failed to persist repair memory to SQLite: {error}")

    def record_failure(self, domain: str, signature: str) -> None:
        """Increment failure count for a stored repair and transition to STALE/DISABLED if needed."""
        try:
            with safe_sqlite_transaction(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE repair_memory
                    SET failure_count = failure_count + 1,
                        status = CASE
                            WHEN failure_count + 1 >= 4 THEN 'disabled'
                            WHEN failure_count + 1 >= 2 THEN 'stale'
                            ELSE status
                        END
                    WHERE domain = ? AND signature = ?
                    """,
                    (domain, signature),
                )
        except Exception as error:
            logger.debug(f"Failed to record repair failure in SQLite: {error}")

    def lookup(
        self, domain: str, signature: str
    ) -> Optional[RepairMemoryRecord]:
        """Query SQLite database for a previously verified working repair record (skipping disabled)."""
        try:
            conn = get_sqlite_connection(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT memory_id, domain, signature, root_cause, repair_type, successful_patch, health_before, health_after, strategy, provider, status, confidence_level, success_count, failure_count, structural_fingerprint
                    FROM repair_memory
                    WHERE domain = ? AND signature = ? AND status != 'disabled'
                    """,
                    (domain, signature),
                )
                row = cursor.fetchone()
                if row:
                    status_val = RepairFreshnessStatus(row[10]) if row[10] in RepairFreshnessStatus.__members__.values() else RepairFreshnessStatus.ACTIVE
                    conf_val = RepairConfidenceLevel(row[11]) if row[11] in RepairConfidenceLevel.__members__.values() else RepairConfidenceLevel.HIGH
                    return RepairMemoryRecord(
                        memory_id=row[0],
                        domain=row[1],
                        signature=row[2],
                        root_cause=row[3],
                        repair_type=RepairType(row[4]),
                        successful_patch=json.loads(row[5]),
                        health_before=row[6],
                        health_after=row[7],
                        strategy=row[8],
                        provider=row[9],
                        status=status_val,
                        confidence_level=conf_val,
                        success_count=row[12] or 1,
                        failure_count=row[13] or 0,
                        structural_fingerprint=row[14],
                    )
            finally:
                conn.close()
        except Exception as error:
            logger.error(f"Failed to lookup repair memory in SQLite: {error}")
        return None

