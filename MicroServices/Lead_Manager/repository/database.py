"""
Async SQLite Database Manager for Lead Manager.
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite

from ..config.logging import get_logger
from ..config.settings import Settings, get_settings

logger = get_logger("Database")

SCHEMA_DDL = """
-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    company_name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    website_url TEXT,
    primary_contact_name TEXT,
    primary_contact_email TEXT,
    primary_contact_phone TEXT,
    stage TEXT NOT NULL,
    fit_score REAL,
    opportunity_score REAL,
    recommended_services TEXT, -- JSON array
    metadata TEXT,             -- JSON object
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_stage ON leads (stage);
CREATE INDEX IF NOT EXISTS idx_leads_campaign ON leads (campaign_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads (primary_contact_email);

-- Opportunities table
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    type TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    problem_summary TEXT,
    evidence TEXT,            -- JSON array
    recommended INTEGER DEFAULT 1,
    status TEXT NOT NULL,     -- IDENTIFIED, PROPOSED, ACCEPTED, REJECTED
    metadata TEXT,            -- JSON object
    created_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_opps_lead ON opportunities (lead_id);

-- Activities (Audit Timeline) table
CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    type TEXT NOT NULL,
    actor TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata TEXT,            -- JSON object
    created_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_activities_lead ON activities (lead_id, created_at);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    due_at TEXT,
    assigned_to TEXT NOT NULL,
    title TEXT,
    description TEXT,
    metadata TEXT,            -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_lead ON tasks (lead_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL,
    last_intent TEXT,
    last_message_at TEXT,
    message_count INTEGER DEFAULT 0,
    metadata TEXT,            -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conv_lead ON conversations (lead_id);
CREATE INDEX IF NOT EXISTS idx_conv_thread ON conversations (thread_id);

-- Meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    conversation_id TEXT,
    title TEXT NOT NULL,
    scheduled_at TEXT,
    duration_minutes INTEGER DEFAULT 30,
    timezone TEXT DEFAULT 'UTC',
    status TEXT NOT NULL,
    meeting_url TEXT,
    ics_content TEXT,
    organizer_email TEXT,
    attendee_email TEXT,
    notes TEXT,
    metadata TEXT,            -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_meetings_lead ON meetings (lead_id);
"""


class DatabaseManager:
    def __init__(self, settings: Settings | None = None, db_path: str | None = None):
        self.settings = settings or get_settings()
        self.db_path = db_path or self.settings.LEAD_MANAGER_DB_PATH

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA foreign_keys = ON;")
            await conn.execute("PRAGMA journal_mode = WAL;")
            yield conn

    async def init_db(self) -> None:
        dir_path = os.path.dirname(self.db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        async with self.get_connection() as conn:
            await conn.executescript(SCHEMA_DDL)
            await conn.commit()
        logger.info(f"Database initialized at {self.db_path}")


_db_manager: DatabaseManager | None = None


def get_db_manager(
    settings: Settings | None = None, db_path: str | None = None
) -> DatabaseManager:
    global _db_manager
    if _db_manager is None or db_path is not None:
        _db_manager = DatabaseManager(settings=settings, db_path=db_path)
    return _db_manager
