"""Thread-safe SQLite database connection manager with WAL mode and busy timeout handling."""

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator
from app.config.logging import get_logger

logger = get_logger("SQLITE_DB_POOL")

_db_locks: dict[str, threading.Lock] = {}
_global_lock = threading.Lock()


def get_db_lock(db_path: str) -> threading.Lock:
    """Get or create a dedicated threading mutex per database path."""
    with _global_lock:
        if db_path not in _db_locks:
            _db_locks[db_path] = threading.Lock()
        return _db_locks[db_path]


def get_sqlite_connection(db_path: str, timeout: float = 15.0) -> sqlite3.Connection:
    """Create and configure a crash-resilient SQLite connection in WAL mode."""
    conn = sqlite3.connect(db_path, timeout=timeout, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


@contextmanager
def safe_sqlite_transaction(db_path: str, timeout: float = 15.0) -> Generator[sqlite3.Connection, None, None]:
    """Context manager acquiring a thread mutex and executing within a clean SQLite transaction."""
    lock = get_db_lock(db_path)
    with lock:
        conn = get_sqlite_connection(db_path=db_path, timeout=timeout)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            raise e
        finally:
            try:
                conn.close()
            except Exception:
                pass
