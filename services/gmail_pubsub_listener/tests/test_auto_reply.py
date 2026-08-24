"""Tests for the Auto-Responder engine."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.events.models import CommunicationEvent, EventTypes
from app.persistence.models import ClassificationRecord, EmailMessage
from app.responder.engine import AutoResponder


@pytest.mark.asyncio
async def test_auto_responder_triggers_reply(temp_db):
    test_db, test_repo = temp_db

    # Seed message and classification in DB
    msg = EmailMessage(
        id="in_msg_test_01",
        thread_id="thread_test_01",
        mailbox="INBOX",
        sender_email="prospect@store.com",
        sender_name="John Doe",
        to=["aadhitkc@gmail.com"],
        subject="Meeting Inquiry",
        text_body="Can we schedule a call?",
        message_id_header="<hdr_123@store.com>",
    )
    await test_repo.save_message(msg)

    cl = ClassificationRecord(
        message_id="in_msg_test_01",
        intent="REQUEST_MEETING",
        confidence=0.95,
        reason="Clear meeting request",
    )
    await test_repo.save_classification(cl)

    # Mock SMTP sender
    mock_sender = MagicMock()
    mock_sender.send = AsyncMock(return_value=MagicMock(status="sent"))

    responder = AutoResponder(repo=test_repo, sender=mock_sender)

    # Trigger event
    event = CommunicationEvent(
        event_type=EventTypes.EMAIL_RECEIVED.value,
        aggregate_type="message",
        aggregate_id="in_msg_test_01",
        payload={
            "message_id": "in_msg_test_01",
            "thread_id": "thread_test_01",
            "sender_email": "prospect@store.com",
            "subject": "Meeting Inquiry",
        },
    )

    await responder.handle_new_inbound(event)

    # Verify send was called
    mock_sender.send.assert_called_once()
    call_args = mock_sender.send.call_args[0][0]
    assert call_args.to == ["prospect@store.com"]
    assert call_args.thread_id == "thread_test_01"
    assert (
        "https://cal.com/agencyos-demo" in call_args.body_text
        or "connecting" in call_args.body_text.lower()
    )
