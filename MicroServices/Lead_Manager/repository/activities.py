"""
Activity Repository for Async SQLite.
"""

import json
from typing import Any, Dict, List, Optional
from ..domain.activity import LeadActivity
from .database import DatabaseManager


class ActivityRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_activity(self, row: Any) -> LeadActivity:
        return LeadActivity(
            id=row["id"],
            lead_id=row["lead_id"],
            type=row["type"],
            actor=row["actor"],
            summary=row["summary"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
        )

    async def create(self, activity: LeadActivity) -> LeadActivity:
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO activities (
                    id, lead_id, type, actor, summary, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    activity.id,
                    activity.lead_id,
                    activity.type,
                    activity.actor,
                    activity.summary,
                    json.dumps(activity.metadata),
                    activity.created_at,
                ),
            )
            await conn.commit()
        return activity

    async def get_by_lead_id(
        self, lead_id: str, limit: int = 100, offset: int = 0
    ) -> List[LeadActivity]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM activities
                WHERE lead_id = ?
                ORDER BY created_at ASC
                LIMIT ? OFFSET ?
                """,
                (lead_id, limit, offset),
            )
            rows = await cursor.fetchall()
            return [self._row_to_activity(row) for row in rows]

    async def list_recent(self, limit: int = 50) -> List[LeadActivity]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM activities
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_activity(row) for row in rows]
