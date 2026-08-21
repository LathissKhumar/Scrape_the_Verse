"""Repair record freshness and lifecycle management subsystem."""

import json
from typing import Any, Optional
from app.config.logging import get_logger
from app.healing.fingerprint import DOMFingerprinter
from app.healing.schemas import RepairFreshnessStatus, RepairMemoryRecord

logger = get_logger("REPAIR_FRESHNESS")


class RepairFreshnessLifecycle:
    """Evaluates and transitions repair memory statuses (ACTIVE, PROBATION, STALE, DISABLED)."""

    def __init__(self, fingerprinter: Optional[DOMFingerprinter] = None) -> None:
        self.fingerprinter = fingerprinter or DOMFingerprinter()

    def evaluate_freshness(
        self,
        record: RepairMemoryRecord,
        current_fingerprint: Optional[dict[str, Any]] = None,
    ) -> RepairFreshnessStatus:
        """Assess the current trust tier and status of a stored repair memory record."""
        # 1. Disabled if excessive consecutive failures
        if record.failure_count >= 4:
            logger.warning(f"Repair {record.memory_id} disabled due to excessive failures ({record.failure_count})")
            return RepairFreshnessStatus.DISABLED

        # 2. Stale if structural drift detected between stored and current page
        if current_fingerprint and record.structural_fingerprint:
            try:
                stored_fp = json.loads(record.structural_fingerprint)
                if self.fingerprinter.is_significant_drift(stored_fp, current_fingerprint):
                    logger.warning(f"Repair {record.memory_id} marked STALE due to structural DOM drift.")
                    return RepairFreshnessStatus.STALE
            except Exception:
                pass

        # 3. Stale if failure count >= 2
        if record.failure_count >= 2:
            return RepairFreshnessStatus.STALE

        # 4. Probation if low success count or marked probation
        if record.success_count < 2 or record.status == RepairFreshnessStatus.PROBATION:
            return RepairFreshnessStatus.PROBATION

        return RepairFreshnessStatus.ACTIVE

