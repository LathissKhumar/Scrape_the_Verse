"""Exponential backoff strategy for network reconnections."""
import asyncio
import logging

logger = logging.getLogger(__name__)


class BackoffStrategy:
    def __init__(self, initial: float = 1.0, multiplier: float = 2.0, max_delay: float = 60.0):
        self.initial = initial
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.current = initial
        self.attempts = 0

    def next_delay(self) -> float:
        delay = self.current
        self.attempts += 1
        self.current = min(self.current * self.multiplier, self.max_delay)
        return delay

    def reset(self) -> None:
        self.current = self.initial
        self.attempts = 0

    async def wait(self) -> float:
        delay = self.next_delay()
        logger.info(f"Reconnection attempt {self.attempts}: waiting {delay:.1f}s before retrying...")
        await asyncio.sleep(delay)
        return delay
