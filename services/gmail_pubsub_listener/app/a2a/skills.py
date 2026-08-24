"""A2A skills implemented by the Communication Service."""

from typing import Any

from app.classification.llm import llm_classifier
from app.imap.listener import imap_listener
from app.persistence.repository import repository
from app.smtp.sender import OutboundEmail, smtp_sender


async def skill_send_email(params: dict[str, Any]) -> dict[str, Any]:
    """Skill to send an email or thread reply."""
    req = OutboundEmail(
        to=params.get("to", []),
        subject=params.get("subject", ""),
        body_text=params.get("body_text", ""),
        body_html=params.get("body_html"),
        lead_id=params.get("lead_id"),
        thread_id=params.get("thread_id"),
    )
    res = await smtp_sender.send(req)
    return res.model_dump()


async def skill_get_thread(params: dict[str, Any]) -> dict[str, Any] | None:
    """Skill to retrieve complete conversation thread with all inbound and outbound messages."""
    thread_id = params.get("thread_id")
    if not thread_id:
        return None

    thread = await repository.get_thread(thread_id)
    if not thread:
        return None

    inbound = await repository.get_messages_by_thread(thread_id)
    outbound = await repository.get_outbound_messages_by_thread(thread_id)

    timeline = []
    for msg in inbound:
        cl = await repository.get_classification(msg.id)
        timeline.append(
            {
                "id": msg.id,
                "direction": "INBOUND",
                "sender": msg.sender_email,
                "subject": msg.subject,
                "body": msg.text_body,
                "timestamp": msg.received_at.isoformat(),
                "intent": cl.intent if cl else None,
                "confidence": cl.confidence if cl else None,
            }
        )

    for out in outbound:
        timeline.append(
            {
                "id": out.id,
                "direction": "OUTBOUND",
                "sender": smtp_sender.email_address,
                "subject": out.subject,
                "body": out.body_text,
                "timestamp": out.created_at,
                "status": out.status,
            }
        )

    timeline.sort(key=lambda x: x["timestamp"])

    return {
        "thread_id": thread.thread_id,
        "lead_id": thread.lead_id,
        "subject": thread.subject,
        "participants": thread.participants,
        "status": thread.status,
        "messages": timeline,
    }


async def skill_get_message(params: dict[str, Any]) -> dict[str, Any] | None:
    """Skill to retrieve a single message by ID."""
    message_id = params.get("message_id")
    if not message_id:
        return None
    msg = await repository.get_message(message_id)
    if not msg:
        return None
    cl = await repository.get_classification(message_id)
    res = msg.model_dump()
    res["classification"] = cl.model_dump() if cl else None
    return res


async def skill_sync_mailbox(params: dict[str, Any]) -> dict[str, Any]:
    """Skill to trigger manual mailbox sync."""
    mailbox = params.get("mailbox", "INBOX")
    synced = await imap_listener.synchronizer.sync_mailbox(mailbox)
    return {"status": "synced", "count": len(synced), "mailbox": mailbox}


async def skill_classify_email(params: dict[str, Any]) -> dict[str, Any]:
    """Skill to classify raw text email."""
    subject = params.get("subject", "")
    body = params.get("body", "")
    res = await llm_classifier.classify_message("manual_query", subject, body)
    return res.model_dump()
