"""Thread Correlator correlating messages into unified conversations."""
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from app.persistence.models import EmailMessage, EmailThread
from app.persistence.repository import Repository, repository as default_repo


def normalize_subject(subject: Optional[str]) -> str:
    """Removes Re:, Fwd:, Aw:, etc. prefixes from subject."""
    if not subject:
        return ""
    cleaned = subject.strip()
    pattern = r"^(re|fwd|fw|aw|vs|antwort):\s*"
    while re.match(pattern, cleaned, re.IGNORECASE):
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


class ThreadCorrelator:
    def __init__(self, repo: Optional[Repository] = None):
        self.repo = repo or default_repo

    async def correlate(self, message: EmailMessage) -> EmailThread:
        """
        Correlates an incoming EmailMessage with an existing EmailThread or creates a new one.
        Algorithm:
        1. Check In-Reply-To against existing message_id_header / thread.
        2. Check References list against existing threads.
        3. Check Message-ID against known threads.
        4. If not found, create a new thread.
        """
        matched_thread: Optional[EmailThread] = None

        # 1. Check In-Reply-To
        if message.in_reply_to:
            matched_thread = await self.repo.find_thread_by_header(message.in_reply_to)

        # 2. Check References if not matched yet
        if not matched_thread and message.references:
            for ref in message.references:
                matched_thread = await self.repo.find_thread_by_header(ref)
                if matched_thread:
                    break

        # 3. Create new thread if no match found
        if not matched_thread:
            thread_id = f"thread_{uuid.uuid4().hex[:12]}"
            participants = list(set([message.sender_email] + message.to))
            matched_thread = EmailThread(
                thread_id=thread_id,
                lead_id=None,
                subject=message.subject,
                participants=participants,
                message_ids=[message.id],
                last_message_at=message.received_at,
                status="ACTIVE",
            )
        else:
            # Update existing thread
            if message.id not in matched_thread.message_ids:
                matched_thread.message_ids.append(message.id)
            for p in [message.sender_email] + message.to:
                if p and p not in matched_thread.participants:
                    matched_thread.participants.append(p)
            if message.received_at > matched_thread.last_message_at:
                matched_thread.last_message_at = message.received_at
            # Update subject if thread didn't have one
            if not matched_thread.subject and message.subject:
                matched_thread.subject = message.subject

        # Update message's thread_id
        message.thread_id = matched_thread.thread_id

        # Persist thread state
        await self.repo.save_thread(matched_thread)
        await self.repo.db.execute(
            "UPDATE messages SET thread_id = ? WHERE message_id = ?",
            (matched_thread.thread_id, message.id),
        )
        return matched_thread


thread_correlator = ThreadCorrelator()
