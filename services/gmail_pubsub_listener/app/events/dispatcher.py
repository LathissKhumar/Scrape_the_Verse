"""Event dispatcher sending events downstream and recording persistence."""

import json
import logging

import httpx

from app.config import get_settings
from app.events.models import CommunicationEvent
from app.persistence.models import EventRecord
from app.persistence.repository import Repository
from app.persistence.repository import repository as default_repo

logger = logging.getLogger(__name__)


class EventDispatcher:
    def __init__(self, repo: Repository | None = None):
        self.repo = repo or default_repo
        self.settings = get_settings()

    async def handle_event(self, event: CommunicationEvent) -> None:
        """Saves event in SQLite store and notifies external services."""
        # 1. Save event to SQLite store
        event_record = EventRecord(
            id=event.id,
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            payload=json.dumps(event.payload),
            status="PROCESSING",
            created_at=event.created_at,
        )
        await self.repo.save_event(event_record)

        # 2. Dispatch downstream asynchronously so callers are never blocked
        async def _dispatch():
            try:
                if event.event_type in [
                    "email.received",
                    "email.classified",
                    "lead.email.correlated",
                ]:
                    await self._notify_lead_manager(event)
                elif event.event_type in ["email.sent", "thread.updated"]:
                    await self._notify_sdr_service(event)
                await self.repo.update_event_status(event.id, "COMPLETED")
            except Exception as e:
                logger.warning(f"Failed to dispatch event {event.id} downstream: {e}")
                await self.repo.update_event_status(event.id, "FAILED")

        asyncio.create_task(_dispatch())

    async def _notify_lead_manager(self, event: CommunicationEvent) -> None:
        url = (
            f"{self.settings.LEAD_MANAGER_URL.rstrip('/')}/api/v1/events/inbound-email"
        )
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.post(url, json=event.model_dump())
        except Exception as e:
            logger.debug(f"Lead Manager not reached at {url}: {e}")

    async def _notify_sdr_service(self, event: CommunicationEvent) -> None:
        url = f"{self.settings.SDR_SERVICE_URL.rstrip('/')}/api/v1/events/communication"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.post(url, json=event.model_dump())
        except Exception as e:
            logger.debug(f"SDR service not reached at {url}: {e}")

    async def replay_unprocessed(self) -> int:
        """Replays pending or failed events from SQLite."""
        pending_events = await self.repo.get_events(status="PENDING")
        for rec in pending_events:
            event = CommunicationEvent(
                id=rec.id,
                event_type=rec.event_type,
                aggregate_type=rec.aggregate_type,
                aggregate_id=rec.aggregate_id,
                payload=json.loads(rec.payload),
                created_at=rec.created_at,
            )
            await self.handle_event(event)
        return len(pending_events)


event_dispatcher = EventDispatcher()
