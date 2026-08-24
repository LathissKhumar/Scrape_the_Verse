"""MIME message parser converting raw RFC822 bytes to EmailMessage."""

import email
import email.policy
import email.utils
import hashlib
from datetime import datetime, timezone

from app.parser.body import extract_body_parts
from app.parser.headers import (
    clean_message_id,
    decode_rfc2047,
    parse_address_list,
    parse_references,
    parse_sender,
)
from app.persistence.models import EmailMessage


class MIMEParser:
    @staticmethod
    def parse_rfc822(
        raw_bytes: bytes, uid: int = 0, mailbox: str = "INBOX"
    ) -> EmailMessage:
        """Parses raw email bytes into the canonical EmailMessage model."""
        raw_hash = hashlib.sha256(raw_bytes).hexdigest()
        msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)

        # Subject
        raw_subject = msg.get("Subject")
        subject = decode_rfc2047(raw_subject) if raw_subject else None

        # Sender
        sender_raw = msg.get("From", "")
        sender_email, sender_name = parse_sender(sender_raw)

        # Recipients
        to_recipients = parse_address_list(msg.get("To", ""))
        cc_recipients = parse_address_list(msg.get("Cc", ""))
        bcc_recipients = parse_address_list(msg.get("Bcc", ""))

        # Message Headers
        message_id_header = clean_message_id(msg.get("Message-ID"))
        in_reply_to = clean_message_id(msg.get("In-Reply-To"))
        references = parse_references(msg.get("References"))

        # Date
        date_str = msg.get("Date")
        received_at = datetime.now(timezone.utc)
        if date_str:
            try:
                dt_tuple = email.utils.parsedate_to_datetime(date_str)
                if dt_tuple:
                    received_at = dt_tuple.astimezone(timezone.utc)
            except Exception:
                pass

        # Bodies
        plain_text, html = extract_body_parts(msg)

        # Generate a unique deterministic ID if message_id_header is absent
        msg_id = message_id_header or f"msg_{raw_hash[:16]}"

        return EmailMessage(
            id=msg_id,
            thread_id=None,  # ThreadCorrelator will correlate and populate this
            mailbox=mailbox,
            uid=uid,
            sender_email=sender_email,
            sender_name=sender_name,
            to=to_recipients,
            cc=cc_recipients,
            bcc=bcc_recipients,
            subject=subject,
            text_body=plain_text,
            html_body=html,
            received_at=received_at,
            message_id_header=message_id_header,
            in_reply_to=in_reply_to,
            references=references,
            labels=[],
            raw_hash=raw_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
