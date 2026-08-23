"""Mailbox synchronizer managing incremental ingestion and event emission."""
import asyncio
import logging
from typing import List, Optional
from app.config import get_settings
from app.events.bus import EventBus, event_bus as default_bus
from app.events.models import CommunicationEvent, EventTypes
from app.imap.client import GmailIMAPClient
from app.parser.mime import MIMEParser
from app.persistence.models import EmailMessage, ClassificationRecord
from app.persistence.repository import Repository, repository as default_repo
from app.threads.correlator import ThreadCorrelator, thread_correlator as default_correlator
from app.classification.llm import LLMClassifier, llm_classifier as default_classifier

logger = logging.getLogger(__name__)


class MailboxSynchronizer:
    def __init__(
        self,
        client: GmailIMAPClient,
        repo: Optional[Repository] = None,
        correlator: Optional[ThreadCorrelator] = None,
        classifier: Optional[LLMClassifier] = None,
        bus: Optional[EventBus] = None,
    ):
        self.client = client
        self.repo = repo or default_repo
        self.correlator = correlator or default_correlator
        self.classifier = classifier or default_classifier
        self.bus = bus or default_bus
        self.settings = get_settings()

    async def sync_mailbox(self, mailbox: str = "INBOX") -> List[EmailMessage]:
        """Performs incremental synchronization for the given mailbox."""
        state = await self.repo.get_mailbox_state(mailbox)
        last_uid = state.last_uid

        # Determine which UIDs to fetch
        if last_uid == 0:
            # Initial synchronization: get latest N messages
            uids_to_fetch = await asyncio.to_thread(
                self.client.get_latest_uids, self.settings.INITIAL_SYNC_MESSAGES
            )
            logger.info(f"Initial sync for {mailbox}: found {len(uids_to_fetch)} initial messages.")
        else:
            # Incremental sync: search UIDs > last_uid
            uids_to_fetch = await asyncio.to_thread(
                self.client.search_uids_greater_than, last_uid
            )
            logger.info(f"Incremental sync for {mailbox}: found {len(uids_to_fetch)} new messages.")

        if not uids_to_fetch:
            return []

        processed_messages: List[EmailMessage] = []
        max_seen_uid = last_uid

        for uid in uids_to_fetch:
            try:
                # 1. Fetch raw RFC822 bytes
                raw_bytes = await asyncio.to_thread(self.client.fetch_rfc822, uid)
                if not raw_bytes:
                    continue

                # 2. Parse MIME structure
                message = MIMEParser.parse_rfc822(raw_bytes, uid=uid, mailbox=mailbox)

                # 3. Save message idempotently
                is_new = await self.repo.save_message(message)
                if not is_new:
                    max_seen_uid = max(max_seen_uid, uid)
                    continue

                # 4. Correlate with thread
                thread = await self.correlator.correlate(message)
                message.thread_id = thread.thread_id
                # Update saved message with thread_id
                await self.repo.db.execute(
                    "UPDATE messages SET thread_id = ? WHERE message_id = ?",
                    (thread.thread_id, message.id),
                )

                # 5. Classify intent
                classification: ClassificationRecord = await self.classifier.classify_message(
                    message_id=message.id,
                    subject=message.subject,
                    body=message.text_body,
                )
                await self.repo.save_classification(classification)

                # 6. Emit events to the EventBus
                await self._emit_ingestion_events(message, thread, classification)

                processed_messages.append(message)
                max_seen_uid = max(max_seen_uid, uid)

            except Exception as e:
                logger.error(f"Error synchronizing message UID {uid}: {e}", exc_info=True)

        # 7. Update cursor in database
        if max_seen_uid > last_uid:
            await self.repo.update_mailbox_state(mailbox, last_uid=max_seen_uid, status="IDLE")
            logger.info(f"Updated mailbox {mailbox} last_uid cursor to {max_seen_uid}.")

        return processed_messages

    async def _emit_ingestion_events(
        self, message: EmailMessage, thread, classification: ClassificationRecord
    ) -> None:
        # Event 1: email.received
        received_event = CommunicationEvent(
            event_type=EventTypes.EMAIL_RECEIVED.value,
            aggregate_type="message",
            aggregate_id=message.id,
            payload={
                "message_id": message.id,
                "thread_id": thread.thread_id,
                "sender_email": message.sender_email,
                "sender_name": message.sender_name,
                "subject": message.subject,
                "received_at": message.received_at.isoformat(),
                "snippet": (message.text_body or "")[:200],
            },
        )
        await self.bus.publish(received_event)

        # Event 2: email.classified
        classified_event = CommunicationEvent(
            event_type=EventTypes.EMAIL_CLASSIFIED.value,
            aggregate_type="message",
            aggregate_id=message.id,
            payload={
                "message_id": message.id,
                "thread_id": thread.thread_id,
                "intent": classification.intent,
                "confidence": classification.confidence,
                "reason": classification.reason,
                "suggested_action": classification.suggested_action,
                "model": classification.model,
            },
        )
        await self.bus.publish(classified_event)

        # Event 3: thread.updated
        thread_event = CommunicationEvent(
            event_type=EventTypes.THREAD_UPDATED.value,
            aggregate_type="thread",
            aggregate_id=thread.thread_id,
            payload={
                "thread_id": thread.thread_id,
                "lead_id": thread.lead_id,
                "subject": thread.subject,
                "participants": thread.participants,
                "last_message_at": thread.last_message_at.isoformat(),
                "status": thread.status,
            },
        )
        await self.bus.publish(thread_event)
