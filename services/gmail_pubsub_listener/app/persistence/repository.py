"""Repository for managing database operations."""
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional
from app.persistence.database import db
from app.persistence.models import (
    EmailMessage,
    EmailThread,
    MailboxStateRecord,
    ClassificationRecord,
    EventRecord,
    OutboundMessageRecord,
    GmailAccountRecord,
)

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, database=None):
        self.db = database or db

    # ---------------- Mailbox State ----------------
    async def get_mailbox_state(self, mailbox: str = "INBOX") -> MailboxStateRecord:
        row = await self.db.fetch_one(
            "SELECT mailbox, last_uid, last_sync_at, status FROM mailbox_state WHERE mailbox = ?",
            (mailbox,)
        )
        if row:
            return MailboxStateRecord(**row)
        # Create initial row if missing
        now_str = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "INSERT OR IGNORE INTO mailbox_state (mailbox, last_uid, last_sync_at, status) VALUES (?, 0, ?, 'IDLE')",
            (mailbox, now_str)
        )
        return MailboxStateRecord(mailbox=mailbox, last_uid=0, last_sync_at=now_str, status="IDLE")

    async def update_mailbox_state(self, mailbox: str, last_uid: int, status: str = "IDLE") -> None:
        now_str = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            """
            INSERT INTO mailbox_state (mailbox, last_uid, last_sync_at, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(mailbox) DO UPDATE SET
                last_uid = CASE WHEN excluded.last_uid > mailbox_state.last_uid THEN excluded.last_uid ELSE mailbox_state.last_uid END,
                last_sync_at = excluded.last_sync_at,
                status = excluded.status
            """,
            (mailbox, last_uid, now_str, status)
        )

    # ---------------- Messages ----------------
    async def save_message(self, msg: EmailMessage) -> bool:
        """Saves an incoming or synced message. Returns True if inserted, False if already existed."""
        existing = await self.db.fetch_one(
            "SELECT message_id FROM messages WHERE message_id = ?",
            (msg.id,)
        )
        if existing:
            return False

        await self.db.execute(
            """
            INSERT INTO messages (
                message_id, thread_id, mailbox, uid, sender_email, sender_name,
                to_recipients, cc_recipients, bcc_recipients, subject,
                body_text, body_html, received_at, message_id_header,
                in_reply_to, references_list, labels, raw_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                msg.id,
                msg.thread_id,
                msg.mailbox,
                msg.uid,
                msg.sender_email,
                msg.sender_name,
                json.dumps(msg.to),
                json.dumps(msg.cc),
                json.dumps(msg.bcc),
                msg.subject,
                msg.text_body,
                msg.html_body,
                msg.received_at.isoformat() if isinstance(msg.received_at, datetime) else str(msg.received_at),
                msg.message_id_header,
                msg.in_reply_to,
                json.dumps(msg.references),
                json.dumps(msg.labels),
                msg.raw_hash,
                msg.created_at,
            )
        )
        return True

    async def get_message(self, message_id: str) -> Optional[EmailMessage]:
        row = await self.db.fetch_one("SELECT * FROM messages WHERE message_id = ?", (message_id,))
        if not row:
            return None
        return self._row_to_email_message(row)

    async def get_messages_by_thread(self, thread_id: str) -> List[EmailMessage]:
        rows = await self.db.fetch_all(
            "SELECT * FROM messages WHERE thread_id = ? ORDER BY received_at ASC",
            (thread_id,)
        )
        return [self._row_to_email_message(r) for r in rows]

    async def get_all_messages(self, limit: int = 100, offset: int = 0) -> List[EmailMessage]:
        rows = await self.db.fetch_all(
            "SELECT * FROM messages ORDER BY received_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [self._row_to_email_message(r) for r in rows]

    def _row_to_email_message(self, row: dict) -> EmailMessage:
        return EmailMessage(
            id=row["message_id"],
            thread_id=row["thread_id"],
            mailbox=row["mailbox"],
            uid=row["uid"],
            sender_email=row["sender_email"],
            sender_name=row["sender_name"],
            to=json.loads(row["to_recipients"] or "[]"),
            cc=json.loads(row["cc_recipients"] or "[]"),
            bcc=json.loads(row["bcc_recipients"] or "[]"),
            subject=row["subject"],
            text_body=row["body_text"],
            html_body=row["body_html"],
            received_at=datetime.fromisoformat(row["received_at"]),
            message_id_header=row["message_id_header"],
            in_reply_to=row["in_reply_to"],
            references=json.loads(row["references_list"] or "[]"),
            labels=json.loads(row["labels"] or "[]"),
            raw_hash=row["raw_hash"],
            created_at=row["created_at"],
        )

    # ---------------- Threads ----------------
    async def get_thread(self, thread_id: str) -> Optional[EmailThread]:
        row = await self.db.fetch_one("SELECT * FROM threads WHERE thread_id = ?", (thread_id,))
        if not row:
            return None
        return EmailThread(
            thread_id=row["thread_id"],
            lead_id=row["lead_id"],
            subject=row["subject"],
            participants=json.loads(row["participants"] or "[]"),
            message_ids=json.loads(row["message_ids"] or "[]"),
            last_message_at=datetime.fromisoformat(row["last_message_at"]),
            status=row["status"],
        )

    async def get_all_threads(self, limit: int = 50, offset: int = 0) -> List[EmailThread]:
        rows = await self.db.fetch_all(
            "SELECT * FROM threads ORDER BY last_message_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [
            EmailThread(
                thread_id=r["thread_id"],
                lead_id=r["lead_id"],
                subject=r["subject"],
                participants=json.loads(r["participants"] or "[]"),
                message_ids=json.loads(r["message_ids"] or "[]"),
                last_message_at=datetime.fromisoformat(r["last_message_at"]),
                status=r["status"],
            )
            for r in rows
        ]

    async def save_thread(self, thread: EmailThread) -> None:
        await self.db.execute(
            """
            INSERT INTO threads (thread_id, lead_id, subject, participants, message_ids, last_message_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                lead_id = COALESCE(excluded.lead_id, threads.lead_id),
                subject = excluded.subject,
                participants = excluded.participants,
                message_ids = excluded.message_ids,
                last_message_at = excluded.last_message_at,
                status = excluded.status
            """,
            (
                thread.thread_id,
                thread.lead_id,
                thread.subject,
                json.dumps(thread.participants),
                json.dumps(thread.message_ids),
                thread.last_message_at.isoformat() if isinstance(thread.last_message_at, datetime) else str(thread.last_message_at),
                thread.status,
            )
        )

    async def find_thread_by_header(self, message_id_header: str) -> Optional[EmailThread]:
        """Finds thread containing a message matching a message_id_header."""
        if not message_id_header:
            return None
        clean_header = message_id_header.strip().strip("<>").strip()
        row = await self.db.fetch_one(
            """
            SELECT thread_id FROM messages 
            WHERE message_id_header = ? 
               OR in_reply_to = ? 
               OR message_id = ?
               OR message_id_header = ?
               OR in_reply_to = ?
               OR message_id = ?
            LIMIT 1
            """,
            (clean_header, clean_header, clean_header, f"<{clean_header}>", f"<{clean_header}>", f"<{clean_header}>")
        )
        if row and row["thread_id"]:
            return await self.get_thread(row["thread_id"])
        return None

    # ---------------- Classifications ----------------
    async def save_classification(self, cl: ClassificationRecord) -> None:
        await self.db.execute(
            """
            INSERT INTO classifications (message_id, intent, confidence, reason, suggested_action, model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(message_id) DO UPDATE SET
                intent = excluded.intent,
                confidence = excluded.confidence,
                reason = excluded.reason,
                suggested_action = excluded.suggested_action,
                model = excluded.model
            """,
            (cl.message_id, cl.intent, cl.confidence, cl.reason, cl.suggested_action, cl.model, cl.created_at)
        )

    async def get_classification(self, message_id: str) -> Optional[ClassificationRecord]:
        row = await self.db.fetch_one("SELECT * FROM classifications WHERE message_id = ?", (message_id,))
        return ClassificationRecord(**row) if row else None

    # ---------------- Events ----------------
    async def save_event(self, ev: EventRecord) -> None:
        await self.db.execute(
            """
            INSERT INTO events (id, event_type, aggregate_type, aggregate_id, payload, status, created_at, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                processed_at = excluded.processed_at
            """,
            (ev.id, ev.event_type, ev.aggregate_type, ev.aggregate_id, ev.payload, ev.status, ev.created_at, ev.processed_at)
        )

    async def get_events(self, status: Optional[str] = None, limit: int = 100) -> List[EventRecord]:
        if status:
            rows = await self.db.fetch_all(
                "SELECT * FROM events WHERE status = ? ORDER BY created_at ASC LIMIT ?",
                (status, limit)
            )
        else:
            rows = await self.db.fetch_all(
                "SELECT * FROM events ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        return [EventRecord(**r) for r in rows]

    async def update_event_status(self, event_id: str, status: str) -> None:
        now_str = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "UPDATE events SET status = ?, processed_at = ? WHERE id = ?",
            (status, now_str, event_id)
        )

    # ---------------- Outbound Messages ----------------
    async def save_outbound_message(self, out: OutboundMessageRecord) -> None:
        await self.db.execute(
            """
            INSERT INTO outbound_messages (id, lead_id, thread_id, to_address, subject, body_text, status, provider_message_id, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                provider_message_id = excluded.provider_message_id,
                error_message = excluded.error_message
            """,
            (out.id, out.lead_id, out.thread_id, out.to_address, out.subject, out.body_text, out.status, out.provider_message_id, out.error_message, out.created_at)
        )

    async def get_outbound_messages_by_thread(self, thread_id: str) -> List[OutboundMessageRecord]:
        rows = await self.db.fetch_all(
            "SELECT * FROM outbound_messages WHERE thread_id = ? ORDER BY created_at ASC",
            (thread_id,)
        )
        return [OutboundMessageRecord(**r) for r in rows]


repository = Repository()
