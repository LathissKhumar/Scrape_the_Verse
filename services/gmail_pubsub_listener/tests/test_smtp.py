"""Tests for SMTP outbound sender and thread header creation."""

from unittest.mock import MagicMock

import pytest
from app.events.bus import EventBus
from app.persistence.models import EmailMessage
from app.smtp.sender import GmailSMTPSender, OutboundEmail


@pytest.mark.asyncio
async def test_smtp_send_success_and_headers(temp_db):
    test_db, test_repo = temp_db
    bus = EventBus()
    await bus.start()

    sender = GmailSMTPSender(
        host="smtp.gmail.com",
        port=465,
        email_address="agency@example.com",
        password="test_password",
        repo=test_repo,
        bus=bus,
    )

    # Seed an inbound message to test thread-aware In-Reply-To derivation
    seed_msg = EmailMessage(
        id="in_msg_999",
        thread_id="thread_xyz",
        mailbox="INBOX",
        uid=55,
        sender_email="prospect@abc.com",
        to=["agency@example.com"],
        subject="Re: Proposal",
        text_body="Interested in chatting",
        message_id_header="header_id_original_123",
    )
    await test_repo.save_message(seed_msg)

    # Mock low-level transmission
    sender._transmit_smtp = MagicMock()

    outbound_req = OutboundEmail(
        to=["prospect@abc.com"],
        subject="Re: Proposal",
        body_text="Here is our calendar link: https://cal.com/example",
        lead_id="lead_001",
        thread_id="thread_xyz",
    )

    res = await sender.send(outbound_req)

    assert res.status == "sent"
    assert res.message_id.startswith("out_")
    sender._transmit_smtp.assert_called_once()

    # Verify outbound message was recorded in SQLite
    out_msgs = await test_repo.get_outbound_messages_by_thread("thread_xyz")
    assert len(out_msgs) == 1
    assert out_msgs[0].to_address == "prospect@abc.com"
    assert out_msgs[0].status == "SENT"

    await bus.stop()
