"""Deterministic rule-based intent classifier for zero-cost immediate classification."""
import re
from typing import Optional
from app.persistence.models import ClassificationRecord


class RuleClassifier:
    """Classifies deterministic email patterns without calling an LLM."""

    # Pre-compiled regex patterns
    OUT_OF_OFFICE_PATTERNS = [
        re.compile(r"out\s+of\s+(the\s+)?office", re.IGNORECASE),
        re.compile(r"auto(-|\s*)reply", re.IGNORECASE),
        re.compile(r"automatic\s+reply", re.IGNORECASE),
        re.compile(r"away\s+from\s+(my\s+)?desk", re.IGNORECASE),
        re.compile(r"on\s+annual\s+leave", re.IGNORECASE),
        re.compile(r"on\s+vacation", re.IGNORECASE),
        re.compile(r"i\s+am\s+(currently\s+)?out", re.IGNORECASE),
    ]

    UNSUBSCRIBE_PATTERNS = [
        re.compile(r"\bunsubscribe\b", re.IGNORECASE),
        re.compile(r"opt(-|\s*)out", re.IGNORECASE),
        re.compile(r"remove\s+me\s+from\s+(your\s+)?list", re.IGNORECASE),
        re.compile(r"stop\s+emailing\s+me", re.IGNORECASE),
        re.compile(r"do\s+not\s+contact\s+me", re.IGNORECASE),
    ]

    BOUNCE_PATTERNS = [
        re.compile(r"delivery\s+status\s+notification", re.IGNORECASE),
        re.compile(r"undeliverable", re.IGNORECASE),
        re.compile(r"failure\s+notice", re.IGNORECASE),
        re.compile(r"mail\s+delivery\s+failed", re.IGNORECASE),
        re.compile(r"550\s+user\s+unknown", re.IGNORECASE),
        re.compile(r"mailbox\s+unavailable", re.IGNORECASE),
    ]

    NOT_INTERESTED_PATTERNS = [
        re.compile(r"not\s+interested", re.IGNORECASE),
        re.compile(r"no\s+thanks", re.IGNORECASE),
        re.compile(r"no\s+thank\s+you", re.IGNORECASE),
        re.compile(r"we\s+are\s+good\s+for\s+now", re.IGNORECASE),
        re.compile(r"pass\s+on\s+this", re.IGNORECASE),
    ]

    REQUEST_MEETING_PATTERNS = [
        re.compile(r"(schedule|book|set\s+up)\s+a\s+(call|meeting|chat|demo)", re.IGNORECASE),
        re.compile(r"calendar\s+link", re.IGNORECASE),
        re.compile(r"are\s+you\s+available\s+(on|for|this|next)", re.IGNORECASE),
        re.compile(r"let('s|\s+us)\s+(talk|chat|connect|meet)", re.IGNORECASE),
    ]

    REQUEST_PRICING_PATTERNS = [
        re.compile(r"(send|what\s+is|share)\s+(the\s+)?(pricing|price|rate\s+card|cost|quote)", re.IGNORECASE),
        re.compile(r"how\s+much\s+does\s+it\s+cost", re.IGNORECASE),
    ]

    @classmethod
    def classify(cls, message_id: str, subject: Optional[str], body: Optional[str]) -> Optional[ClassificationRecord]:
        full_text = f"{subject or ''}\n{body or ''}".strip()
        if not full_text:
            return None

        # 1. Check Bounce
        for pat in cls.BOUNCE_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="BOUNCE",
                    confidence=0.99,
                    reason="Matched automated delivery failure notification pattern.",
                    suggested_action="mark_bounced",
                    model="rules",
                )

        # 2. Check Out of Office
        for pat in cls.OUT_OF_OFFICE_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="OUT_OF_OFFICE",
                    confidence=0.98,
                    reason="Matched out-of-office automated response pattern.",
                    suggested_action="snooze_followup",
                    model="rules",
                )

        # 3. Check Unsubscribe
        for pat in cls.UNSUBSCRIBE_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="UNSUBSCRIBE",
                    confidence=0.96,
                    reason="Prospect explicitly requested to be removed or unsubscribed.",
                    suggested_action="suppress_contact",
                    model="rules",
                )

        # 4. Check Not Interested
        for pat in cls.NOT_INTERESTED_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="NOT_INTERESTED",
                    confidence=0.92,
                    reason="Prospect stated they are not interested.",
                    suggested_action="mark_not_interested",
                    model="rules",
                )

        # 5. Check Clear Meeting Request
        for pat in cls.REQUEST_MEETING_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="REQUEST_MEETING",
                    confidence=0.90,
                    reason="Prospect expressed clear interest in scheduling a meeting or call.",
                    suggested_action="create_meeting_task",
                    model="rules",
                )

        # 6. Check Clear Pricing Request
        for pat in cls.REQUEST_PRICING_PATTERNS:
            if pat.search(full_text):
                return ClassificationRecord(
                    message_id=message_id,
                    intent="REQUEST_PRICING",
                    confidence=0.90,
                    reason="Prospect asked directly for pricing or cost breakdown.",
                    suggested_action="send_pricing_details",
                    model="rules",
                )

        # If ambiguous, return None to trigger LLM fallback
        return None
