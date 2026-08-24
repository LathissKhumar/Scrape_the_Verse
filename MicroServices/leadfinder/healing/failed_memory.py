"""Memory subsystem for recording and suppressing repeatedly failing repair candidates with TTL decay."""

import hashlib
import json
import os
import sqlite3
import time
from typing import Any

from leadfinder.config.logging import get_logger
from leadfinder.config.settings import get_settings

logger = get_logger("FAILED_REPAIR_MEMORY")

_DEFAULT_FAILED_REPAIR_TTL_SECONDS = 3600


class FailedRepairMemory:
    """Tracks failed repair candidates per domain/signature to prevent wasteful retries."""

    def __init__(self, db_path: str = "app/.repair_memory.sqlite") -> None:
        if not os.path.exists(db_path) and os.path.exists(os.path.join("app", db_path)):
            db_path = os.path.join("app", db_path)
        self.db_path = db_path
        self.settings = get_settings()
        self._memory_cache: dict[str, dict[str, Any]] = {}
        self._init_db()

    def _init_db(self) -> None:
        """Create failed_repairs table if not exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS failed_repairs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        fingerprint TEXT NOT NULL,
                        failure_reason TEXT,
                        failure_count INTEGER DEFAULT 1,
                        updated_at REAL,
                        UNIQUE(domain, signature, fingerprint)
                    )
                    """
                )
                conn.commit()
        except Exception as error:
            logger.warning(f"Could not initialize failed_repairs SQLite table: {error}")

    def generate_fingerprint(self, config: dict[str, Any]) -> str:
        """Create a deterministic SHA-256 fingerprint for a proposed configuration."""
        serialized = json.dumps(config, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    def record_failure(
        self,
        domain: str,
        signature: str,
        config: dict[str, Any],
        reason: str = "Validation rejection",
    ) -> None:
        """Record or increment a candidate repair failure."""
        fingerprint = self.generate_fingerprint(config)
        now = time.time()
        key = f"{domain}:{signature}:{fingerprint}"

        # Update in-memory
        if key in self._memory_cache:
            self._memory_cache[key]["failure_count"] += 1
            self._memory_cache[key]["updated_at"] = now
            self._memory_cache[key]["reason"] = reason
        else:
            self._memory_cache[key] = {
                "domain": domain,
                "signature": signature,
                "fingerprint": fingerprint,
                "failure_count": 1,
                "updated_at": now,
                "reason": reason,
            }

        # Persist to SQLite
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO failed_repairs (domain, signature, fingerprint, failure_reason, failure_count, updated_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                    ON CONFLICT(domain, signature, fingerprint) DO UPDATE SET
                        failure_count = failure_count + 1,
                        failure_reason = excluded.failure_reason,
                        updated_at = excluded.updated_at
                    """,
                    (domain, signature, fingerprint, reason, now),
                )
                conn.commit()
        except Exception as error:
            logger.debug(f"Failed to persist failure record to SQLite: {error}")

        logger.debug(
            f"Recorded failed repair candidate for {domain} (fp={fingerprint}, reason='{reason[:40]}')"
        )

    def is_suppressed(
        self,
        domain: str,
        signature: str,
        config: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> bool:
        """Check if this candidate has repeatedly failed within the active TTL window."""
        fingerprint = self.generate_fingerprint(config)
        ttl = (
            ttl_seconds
            if ttl_seconds is not None
            else getattr(
                self.settings,
                "FAILED_REPAIR_TTL_SECONDS",
                _DEFAULT_FAILED_REPAIR_TTL_SECONDS,
            )
        )
        now = time.time()
        key = f"{domain}:{signature}:{fingerprint}"

        # 1. Check in-memory
        if key in self._memory_cache:
            record = self._memory_cache[key]
            if (now - record["updated_at"]) < ttl and record["failure_count"] >= 2:
                logger.debug(
                    f"Candidate {fingerprint} suppressed via memory (failures={record['failure_count']})"
                )
                return True

        # 2. Check SQLite
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT failure_count, updated_at FROM failed_repairs
                    WHERE domain = ? AND signature = ? AND fingerprint = ?
                    """,
                    (domain, signature, fingerprint),
                )
                row = cur.fetchone()
                if row:
                    count, updated_at = row[0], row[1]
                    if (now - updated_at) < ttl and count >= 2:
                        logger.debug(
                            f"Candidate {fingerprint} suppressed via SQLite (failures={count})"
                        )
                        return True
        except Exception:
            pass

        return False

    def get_penalty(self, domain: str, signature: str, config: dict[str, Any]) -> float:
        """Return score penalty factor (0.0 to 0.5) if candidate has previous failures."""
        fingerprint = self.generate_fingerprint(config)
        key = f"{domain}:{signature}:{fingerprint}"
        if key in self._memory_cache:
            return min(0.5, self._memory_cache[key]["failure_count"] * 0.20)
        return 0.0
