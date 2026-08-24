"""
Meeting Repository for Async SQLite.
"""

import json
from typing import Any

from ..domain.meeting import Meeting, utc_now_iso
from ..domain.stage import MeetingStatus
from .database import DatabaseManager


class MeetingRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_meeting(self, row: Any) -> Meeting:
        return Meeting(
            id=row["id"],
            lead_id=row["lead_id"],
            conversation_id=row["conversation_id"],
            title=row["title"],
            scheduled_at=row["scheduled_at"],
            duration_minutes=row["duration_minutes"],
            timezone=row["timezone"],
            status=MeetingStatus(row["status"]),
            meeting_url=row["meeting_url"],
            ics_content=row["ics_content"],
            organizer_email=row["organizer_email"],
            attendee_email=row["attendee_email"],
            notes=row["notes"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create(self, meeting: Meeting) -> Meeting:
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO meetings (
                    id, lead_id, conversation_id, title, scheduled_at,
                    duration_minutes, timezone, status, meeting_url,
                    ics_content, organizer_email, attendee_email, notes,
                    metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meeting.id,
                    meeting.lead_id,
                    meeting.conversation_id,
                    meeting.title,
                    meeting.scheduled_at,
                    meeting.duration_minutes,
                    meeting.timezone,
                    meeting.status.value
                    if hasattr(meeting.status, "value")
                    else str(meeting.status),
                    meeting.meeting_url,
                    meeting.ics_content,
                    meeting.organizer_email,
                    meeting.attendee_email,
                    meeting.notes,
                    json.dumps(meeting.metadata),
                    meeting.created_at,
                    meeting.updated_at,
                ),
            )
            await conn.commit()
        return meeting

    async def get_by_id(self, meeting_id: str) -> Meeting | None:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_meeting(row)
            return None

    async def get_by_lead_id(self, lead_id: str) -> list[Meeting]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM meetings WHERE lead_id = ? ORDER BY created_at DESC",
                (lead_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_meeting(row) for row in rows]

    async def update_status(
        self,
        meeting_id: str,
        status: MeetingStatus,
        scheduled_at: str | None = None,
        ics_content: str | None = None,
    ) -> Meeting | None:
        status_str = status.value if hasattr(status, "value") else str(status)
        now_str = utc_now_iso()

        async with self.db.get_connection() as conn:
            if scheduled_at and ics_content:
                await conn.execute(
                    """
                    UPDATE meetings
                    SET status = ?, scheduled_at = ?, ics_content = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, scheduled_at, ics_content, now_str, meeting_id),
                )
            elif scheduled_at:
                await conn.execute(
                    """
                    UPDATE meetings
                    SET status = ?, scheduled_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, scheduled_at, now_str, meeting_id),
                )
            elif ics_content:
                await conn.execute(
                    """
                    UPDATE meetings
                    SET status = ?, ics_content = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, ics_content, now_str, meeting_id),
                )
            else:
                await conn.execute(
                    """
                    UPDATE meetings
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, now_str, meeting_id),
                )
            await conn.commit()

        return await self.get_by_id(meeting_id)
