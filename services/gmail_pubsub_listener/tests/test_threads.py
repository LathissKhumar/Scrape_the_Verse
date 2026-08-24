"""Tests for conversation thread correlation."""

import pytest
from app.parser.mime import MIMEParser
from app.threads.correlator import ThreadCorrelator, normalize_subject


def test_normalize_subject():
    assert (
        normalize_subject("Re: Re: Fwd: Website Design Proposal")
        == "Website Design Proposal"
    )
    assert normalize_subject("Aw: Pricing quote") == "Pricing quote"


@pytest.mark.asyncio
async def test_thread_correlation_in_reply_to(temp_db):
    test_db, test_repo = temp_db
    correlator = ThreadCorrelator(repo=test_repo)

    # Initial incoming message
    email_1 = (
        b"From: client@co.com\r\n"
        b"To: agency@co.com\r\n"
        b"Subject: Initial Pitch\r\n"
        b"Message-ID: <msg_root_001@co.com>\r\n"
        b"\r\n"
        b"We want to build a website.\r\n"
    )
    msg1 = MIMEParser.parse_rfc822(email_1, uid=1)
    await test_repo.save_message(msg1)
    thread1 = await correlator.correlate(msg1)

    assert thread1.thread_id.startswith("thread_")
    assert "client@co.com" in thread1.participants

    # Second message referencing msg1
    email_2 = (
        b"From: agency@co.com\r\n"
        b"To: client@co.com\r\n"
        b"Subject: Re: Initial Pitch\r\n"
        b"Message-ID: <msg_reply_002@co.com>\r\n"
        b"In-Reply-To: <msg_root_001@co.com>\r\n"
        b"References: <msg_root_001@co.com>\r\n"
        b"\r\n"
        b"Great, let's schedule time.\r\n"
    )
    msg2 = MIMEParser.parse_rfc822(email_2, uid=2)
    await test_repo.save_message(msg2)
    thread2 = await correlator.correlate(msg2)

    # Should correlate to same thread
    assert thread2.thread_id == thread1.thread_id
    assert len(thread2.message_ids) == 2
    assert "msg_root_001@co.com" in thread2.message_ids
    assert "msg_reply_002@co.com" in thread2.message_ids
