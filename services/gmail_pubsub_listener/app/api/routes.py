"""API route definitions for Communication Service."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.api.schemas import (
    HealthResponse,
    MailboxStatusResponse,
    SyncRequest,
    SyncResponse,
    SendMailRequest,
    SendMailResponse,
    ThreadDetailResponse,
    TimelineMessage,
    A2AInvokeRequest,
)
from app.a2a.agent import communication_agent
from app.config import get_settings
from app.events.dispatcher import event_dispatcher
from app.imap.listener import imap_listener
from app.persistence.models import EmailMessage, EmailThread, EventRecord
from app.persistence.repository import repository
from app.smtp.sender import OutboundEmail, smtp_sender

router = APIRouter()


# ---------------- Health & Readiness ----------------
@router.get("/health", response_model=HealthResponse)
async def get_health():
    return HealthResponse(
        status="ok" if imap_listener.client.is_connected or not imap_listener.settings.GMAIL_ADDRESS else "degraded",
        imap_connected=imap_listener.client.is_connected,
        listener_running=imap_listener.is_running,
    )


@router.get("/ready")
async def get_ready():
    return {"status": "ready"}


# ---------------- Mailbox Control ----------------
@router.get("/api/v1/mailbox/status", response_model=MailboxStatusResponse)
async def get_mailbox_status():
    settings = get_settings()
    state = await repository.get_mailbox_state(settings.IMAP_MAILBOX)
    return MailboxStatusResponse(
        mailbox=state.mailbox,
        status=state.status,
        last_uid=state.last_uid,
        last_sync_at=state.last_sync_at,
        imap_host=settings.IMAP_SERVER,
        listener_active=imap_listener.is_running,
    )


@router.post("/api/v1/mailbox/start")
async def start_mailbox_listener():
    await imap_listener.start()
    return {"status": "started", "mailbox": imap_listener.settings.IMAP_MAILBOX}


@router.post("/api/v1/mailbox/stop")
async def stop_mailbox_listener():
    await imap_listener.stop()
    return {"status": "stopped", "mailbox": imap_listener.settings.IMAP_MAILBOX}


@router.post("/api/v1/mailbox/sync", response_model=SyncResponse)
async def sync_mailbox_now(req: SyncRequest = SyncRequest()):
    messages = await imap_listener.synchronizer.sync_mailbox(req.mailbox)
    return SyncResponse(
        status="synced",
        synced_messages_count=len(messages),
        mailbox=req.mailbox,
    )


# ---------------- Messages ----------------
@router.get("/api/v1/messages/{message_id}")
async def get_message_detail(message_id: str):
    msg = await repository.get_message(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    classification = await repository.get_classification(message_id)
    data = msg.model_dump()
    data["classification"] = classification.model_dump() if classification else None
    return data


@router.get("/api/v1/messages", response_model=List[EmailMessage])
async def list_messages(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return await repository.get_all_messages(limit=limit, offset=offset)


# ---------------- Threads & Conversation Timeline ----------------
@router.get("/api/v1/threads/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread_timeline(thread_id: str):
    thread = await repository.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    inbound = await repository.get_messages_by_thread(thread_id)
    outbound = await repository.get_outbound_messages_by_thread(thread_id)

    timeline_items: List[TimelineMessage] = []
    for msg in inbound:
        cl = await repository.get_classification(msg.id)
        timeline_items.append(
            TimelineMessage(
                id=msg.id,
                direction="INBOUND",
                sender=msg.sender_email,
                subject=msg.subject,
                body=msg.text_body,
                timestamp=msg.received_at.isoformat(),
                intent=cl.intent if cl else None,
                confidence=cl.confidence if cl else None,
            )
        )

    for out in outbound:
        timeline_items.append(
            TimelineMessage(
                id=out.id,
                direction="OUTBOUND",
                sender=smtp_sender.email_address or "agency@company.com",
                subject=out.subject,
                body=out.body_text,
                timestamp=out.created_at,
                status=out.status,
            )
        )

    timeline_items.sort(key=lambda x: x.timestamp)

    return ThreadDetailResponse(
        thread_id=thread.thread_id,
        lead_id=thread.lead_id,
        subject=thread.subject,
        participants=thread.participants,
        status=thread.status,
        messages=timeline_items,
    )


@router.get("/api/v1/threads", response_model=List[EmailThread])
async def list_threads(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return await repository.get_all_threads(limit=limit, offset=offset)


# ---------------- Outbound Sending ----------------
@router.post("/api/v1/mail/send", response_model=SendMailResponse)
async def send_mail(req: SendMailRequest):
    outbound = OutboundEmail(
        to=req.to,
        subject=req.subject,
        body_text=req.body_text,
        body_html=req.body_html,
        cc=req.cc,
        bcc=req.bcc,
        lead_id=req.lead_id,
        thread_id=req.thread_id,
        in_reply_to=req.in_reply_to,
        references=req.references,
    )
    res = await smtp_sender.send(outbound)
    return SendMailResponse(
        status=res.status,
        message_id=res.message_id,
        provider_message_id=res.provider_message_id,
        sent_at=res.sent_at,
        error=res.error,
    )


# ---------------- Events & Replay ----------------
@router.get("/api/v1/events", response_model=List[EventRecord])
async def get_events_log(
    status: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await repository.get_events(status=status, limit=limit)


@router.post("/api/v1/events/replay")
async def replay_events():
    count = await event_dispatcher.replay_unprocessed()
    return {"status": "replayed", "count": count}


# ---------------- Agent-to-Agent (A2A) ----------------
@router.get("/.well-known/agent-card.json")
async def get_agent_card():
    return communication_agent.get_agent_card()


@router.post("/api/v1/a2a/invoke")
async def invoke_a2a_skill(req: A2AInvokeRequest):
    try:
        result = await communication_agent.execute_skill(req.skill, req.parameters)
        return {"status": "success", "skill": req.skill, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
