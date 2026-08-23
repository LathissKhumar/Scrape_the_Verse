"""
Event Publisher for SSE & internal event distribution.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from ..config.logging import get_logger

logger = get_logger("EventPublisher")


class EventPublisher:
    _instance: Optional["EventPublisher"] = None

    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    @classmethod
    def get_instance(cls) -> "EventPublisher":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, topic: str, data: Dict[str, Any]) -> None:
        payload = {"topic": topic, "data": data}
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass
            except Exception as e:
                logger.warning(f"Failed to publish to queue: {e}")
