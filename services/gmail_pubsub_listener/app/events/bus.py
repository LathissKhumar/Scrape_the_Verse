"""In-memory event bus for fast asynchronous pub/sub."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from app.events.models import CommunicationEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[CommunicationEvent], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._wildcard_subscribers: list[EventHandler] = []
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._consumer_task: asyncio.Task = None

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribes an async handler to a specific event type or '*'."""
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    async def publish(self, event: CommunicationEvent) -> None:
        """Enqueues an event for asynchronous processing."""
        await self._queue.put(event)

    async def start(self) -> None:
        """Starts background queue processing."""
        if self._running:
            return
        self._running = True
        self._consumer_task = asyncio.create_task(self._process_queue())
        logger.info("EventBus started background consumer task.")

    async def stop(self) -> None:
        """Stops background queue processing."""
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped.")

    async def _process_queue(self) -> None:
        while self._running:
            try:
                event: CommunicationEvent = await self._queue.get()
                handlers = (
                    self._subscribers.get(event.event_type, [])
                    + self._wildcard_subscribers
                )
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event.event_type}: {e}",
                            exc_info=True,
                        )
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in EventBus worker: {e}", exc_info=True)


event_bus = EventBus()
