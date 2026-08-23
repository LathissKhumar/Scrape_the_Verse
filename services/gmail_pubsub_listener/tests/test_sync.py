"""Tests for incremental mailbox synchronization and cursor state."""
import pytest
from unittest.mock import MagicMock
from app.events.bus import EventBus
from app.imap.synchronizer import MailboxSynchronizer
from app.threads.correlator import ThreadCorrelator
from app.classification.llm import LLMClassifier


@pytest.mark.asyncio
async def test_incremental_sync_and_cursor(temp_db):
    test_db, test_repo = temp_db
    bus = EventBus()
    received_events = []

    async def event_collector(event):
        received_events.append(event)

    bus.subscribe("*", event_collector)
    await bus.start()

    correlator = ThreadCorrelator(repo=test_repo)
    classifier = LLMClassifier()

    # Mock IMAP client
    mock_client = MagicMock()
    mock_client.get_latest_uids.return_value = [101, 102]
    mock_client.search_uids_greater_than.return_value = [103]

    raw_email_101 = (
        b"From: c1@test.com\r\nTo: us@test.com\r\nSubject: Hello\r\nMessage-ID: <m101@test.com>\r\n\r\nHello\r\n"
    )
    raw_email_102 = (
        b"From: c2@test.com\r\nTo: us@test.com\r\nSubject: Pricing?\r\nMessage-ID: <m102@test.com>\r\n\r\nHow much is it?\r\n"
    )
    raw_email_103 = (
        b"From: c3@test.com\r\nTo: us@test.com\r\nSubject: Meet\r\nMessage-ID: <m103@test.com>\r\n\r\nLet's meet tomorrow\r\n"
    )

    def fetch_side_effect(uid):
        return {101: raw_email_101, 102: raw_email_102, 103: raw_email_103}.get(uid)

    mock_client.fetch_rfc822.side_effect = fetch_side_effect

    synchronizer = MailboxSynchronizer(
        client=mock_client,
        repo=test_repo,
        correlator=correlator,
        classifier=classifier,
        bus=bus,
    )

    # Initial sync (last_uid = 0)
    synced_initial = await synchronizer.sync_mailbox("INBOX")
    assert len(synced_initial) == 2

    # Check cursor updated to 102
    state = await test_repo.get_mailbox_state("INBOX")
    assert state.last_uid == 102

    # Incremental sync (last_uid = 102) -> fetches 103
    synced_next = await synchronizer.sync_mailbox("INBOX")
    assert len(synced_next) == 1

    # Check cursor updated to 103
    state_after = await test_repo.get_mailbox_state("INBOX")
    assert state_after.last_uid == 103

    await bus.stop()
