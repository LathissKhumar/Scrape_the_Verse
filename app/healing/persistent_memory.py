import json
import sqlite3
from typing import Optional

from app.config.logging import get_logger
from app.healing.schemas import RepairMemoryRecord, RepairType

logger = get_logger("PERSISTENT_REPAIR_MEMORY")


class PersistentRepairMemory:
    """SQLite-backed persistent repair memory for instant repeat self-healing."""

    def __init__(self, db_path: str = ".repair_memory.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite table for persistent repair records with automatic column migration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                ]:
                    if col not in existing_cols:
                        conn.execute(f"ALTER TABLE repair_memory ADD COLUMN {col} {col_type}")
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not initialize SQLite persistent repair memory: {e}")

    def record_success(self, record: RepairMemoryRecord) -> None:
        """Persist a successful repair record into SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO repair_memory
                    (memory_id, domain, signature, root_cause, repair_type, successful_patch, health_before, health_after, strategy, provider)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    ),
                )
                conn.commit()
                logger.info(
                    f"Persistent repair stored in SQLite for domain={record.domain} sig={record.signature}"
                )
        except Exception as e:
            logger.error(f"Failed to persist repair memory to SQLite: {e}")

    def lookup(
        self, domain: str, signature: str
    ) -> Optional[RepairMemoryRecord]:
        """Query SQLite database for a previously verified working repair record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT memory_id, domain, signature, root_cause, repair_type, successful_patch, health_before, health_after, strategy, provider
                    FROM repair_memory WHERE domain = ? AND signature = ?
                    """,
                    (domain, signature),
                )
                row = cursor.fetchone()
                if row:
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
                    )
        except Exception as e:
            logger.error(f"Failed to lookup repair memory in SQLite: {e}")
        return None
