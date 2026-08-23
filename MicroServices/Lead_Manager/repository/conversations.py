"""
Conversation Repository for Async SQLite.
"""

import json
from typing import Any, Dict, List, Optional
from ..domain.conversation import Conversation, utc_now_iso
from .database import DatabaseManager


class ConversationRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_conv(self, row: Any) -> Conversation:
        return Conversation(
            id=row["id"],
            lead_id=row["lead_id"],
            thread_id=row["thread_id"],
            channel=row["channel"],
            status=row["status"],
            last_intent=row["last_intent"],
            last_message_at=row["last_message_at"],
            message_count=row["message_count"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create_or_update(
        self,
        lead_id: str,
        thread_id: str,
        channel: str = "email",
        last_intent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        now_str = utc_now_iso()
        existing = await self.get_by_thread_id(thread_id)

        async with self.db.get_connection() as conn:
            if existing:
                count = existing.message_count + 1
                intent = last_intent or existing.last_intent
                meta = {**existing.metadata, **(metadata or {})}
                await conn.execute(
                    """
                    UPDATE conversations
                    SET message_count = ?, last_intent = ?, last_message_at = ?,
                        metadata = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (count, intent, now_str, json.dumps(meta), now_str, existing.id),
                )
                await conn.commit()
                return (await self.get_by_id(existing.id)) or existing
            else:
                conv = Conversation(
                    lead_id=lead_id,
                    thread_id=thread_id,
                    channel=channel,
                    status="ACTIVE",
                    last_intent=last_intent,
                    last_message_at=now_str,
                    message_count=1,
                    metadata=metadata or {},
                    created_at=now_str,
                    updated_at=now_str,
                )
                await conn.execute(
                    """
                    INSERT INTO conversations (
                        id, lead_id, thread_id, channel, status,
                        last_intent, last_message_at, message_count,
                        metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conv.id,
                        conv.lead_id,
                        conv.thread_id,
                        conv.channel,
                        conv.status,
                        conv.last_intent,
                        conv.last_message_at,
                        conv.message_count,
                        json.dumps(conv.metadata),
                        conv.created_at,
                        conv.updated_at,
                    ),
                )
                await conn.commit()
                return conv

    async def get_by_id(self, conv_id: str) -> Optional[Conversation]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_conv(row)
            return None

    async def get_by_thread_id(self, thread_id: str) -> Optional[Conversation]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM conversations WHERE thread_id = ? LIMIT 1", (thread_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_conv(row)
            return None

    async def get_by_lead_id(self, lead_id: str) -> List[Conversation]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM conversations WHERE lead_id = ? ORDER BY last_message_at DESC",
                (lead_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_conv(row) for row in rows]
