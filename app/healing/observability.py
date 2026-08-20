"""Structured observability and telemetry subsystem for the self-healing scraping lifecycle."""

import json
import os
import threading
import time
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from app.config.logging import get_logger

logger = get_logger("REPAIR_OBSERVABILITY")


class RepairSessionTelemetry(BaseModel):
    """Structured telemetry record capturing the complete lifecycle of an autonomous repair attempt."""

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    domain: str
    root_cause: str
    initial_health: float
    final_health: float = 0.0
    improvement: float = 0.0
    attempts_count: int = 0
    candidates_generated: int = 0
    actions_executed: int = 0
    multi_page_evaluated: bool = False
    multi_page_count: int = 0
    confidence_score: float = 0.0
    confidence_level: str = "low"
    accepted: bool = False
    persisted: bool = False
    rejection_reason: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class RepairObservability:
    """Singleton-like telemetry buffer and JSONL log persistence for self-healing operations."""

    def __init__(self, log_path: str = ".repair_sessions.jsonl"):
        self.log_path = log_path
        self._sessions: list[RepairSessionTelemetry] = []
        self._lock = threading.Lock()

    def record_session(self, session: RepairSessionTelemetry) -> None:
        """Buffer and append a repair session telemetry event."""
        with self._lock:
            self._sessions.append(session)
            # Keep in-memory buffer bounded to last 200 sessions
            if len(self._sessions) > 200:
                self._sessions = self._sessions[-200:]

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(session.model_dump_json() + "\n")
        except Exception as e:
            logger.debug(f"Could not append session telemetry to file: {e}")

        logger.debug(
            f"Logged repair telemetry: session={session.session_id[:8]}, "
            f"domain={session.domain}, accepted={session.accepted}, "
            f"health={session.initial_health:.2f}->{session.final_health:.2f}, "
            f"confidence={session.confidence_level}"
        )

    def get_recent_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent repair sessions."""
        with self._lock:
            return [s.model_dump() for s in self._sessions[-limit:]]

    def get_summary(self) -> dict[str, Any]:
        """Aggregate statistical summary across all observed repair sessions."""
        with self._lock:
            total = len(self._sessions)
            if total == 0:
                return {"total_sessions": 0, "success_rate": 0.0}

            accepted = sum(1 for s in self._sessions if s.accepted)
            persisted = sum(1 for s in self._sessions if s.persisted)
            avg_duration = sum(s.duration_ms for s in self._sessions) / total
            avg_improvement = sum(s.improvement for s in self._sessions) / total

            return {
                "total_sessions": total,
                "accepted_count": accepted,
                "success_rate": round(accepted / total, 3),
                "persisted_count": persisted,
                "avg_duration_ms": round(avg_duration, 1),
                "avg_improvement": round(avg_improvement, 3),
            }
