"""SQLite database manager with asynchronous execution."""
import asyncio
import os
import sqlite3
from typing import Any, List, Optional, Tuple
from app.config import get_settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS gmail_accounts (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mailbox_state (
    mailbox TEXT PRIMARY KEY,
    last_uid INTEGER NOT NULL DEFAULT 0,
    last_sync_at TEXT,
    status TEXT DEFAULT 'IDLE'
);

CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    thread_id TEXT,
    mailbox TEXT NOT NULL DEFAULT 'INBOX',
    uid INTEGER NOT NULL DEFAULT 0,
    sender_email TEXT NOT NULL,
    sender_name TEXT,
    to_recipients TEXT NOT NULL DEFAULT '[]',
    cc_recipients TEXT NOT NULL DEFAULT '[]',
    bcc_recipients TEXT NOT NULL DEFAULT '[]',
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    received_at TEXT NOT NULL,
    message_id_header TEXT,
    in_reply_to TEXT,
    references_list TEXT NOT NULL DEFAULT '[]',
    labels TEXT NOT NULL DEFAULT '[]',
    raw_hash TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS threads (
    thread_id TEXT PRIMARY KEY,
    lead_id TEXT,
    subject TEXT,
    participants TEXT NOT NULL DEFAULT '[]',
    message_ids TEXT NOT NULL DEFAULT '[]',
    last_message_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS classifications (
    message_id TEXT PRIMARY KEY,
    intent TEXT NOT NULL,
    confidence REAL NOT NULL,
    reason TEXT NOT NULL,
    suggested_action TEXT,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(message_id) REFERENCES messages(message_id)
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    aggregate_type TEXT,
    aggregate_id TEXT,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TEXT NOT NULL,
    processed_at TEXT
);

CREATE TABLE IF NOT EXISTS outbound_messages (
    id TEXT PRIMARY KEY,
    lead_id TEXT,
    thread_id TEXT,
    to_address TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_text TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    provider_message_id TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_email ON messages(sender_email);
CREATE INDEX IF NOT EXISTS idx_messages_uid ON messages(uid);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
"""


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_settings().DATABASE_PATH
        self._lock = asyncio.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db_sync(self) -> None:
        """Initializes database schema synchronously."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    async def init_db(self) -> None:
        """Initializes database schema asynchronously."""
        await asyncio.to_thread(self.init_db_sync)

    async def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """Executes INSERT/UPDATE/DELETE query and returns affected rows."""
        async with self._lock:
            def _run():
                with self._get_connection() as conn:
                    cursor = conn.execute(query, params)
                    conn.commit()
                    return cursor.rowcount
            return await asyncio.to_thread(_run)

    async def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[dict]:
        """Fetches a single row as a dictionary."""
        def _run():
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
        return await asyncio.to_thread(_run)

    async def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[dict]:
        """Fetches all rows as a list of dictionaries."""
        def _run():
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        return await asyncio.to_thread(_run)


db = Database()
