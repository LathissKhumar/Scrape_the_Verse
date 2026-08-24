"""
Conversation Agent for Lead Manager.
"""

from typing import Any

from ..config.logging import get_logger
from ..domain.stage import EmailIntent
from .llm_factory import LLMClient

logger = get_logger("ConversationAgent")


class ConversationAgent:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def _heuristic_classify(self, text: str) -> dict[str, Any]:
        lower = text.lower()

        if any(
            w in lower
            for w in [
                "meet",
                "call",
                "schedule",
                "zoom",
                "calendar",
                "tomorrow",
                "tuesday",
                "available at",
            ]
        ):
            return {
                "intent": EmailIntent.REQUEST_MEETING.value,
                "confidence": 0.85,
                "reasoning": "Heuristic match for meeting/call scheduling keywords.",
                "suggested_action": "CREATE_MEETING_TASK",
            }

        if any(
            w in lower
            for w in ["price", "cost", "quote", "rate", "how much", "pricing", "budget"]
        ):
            return {
                "intent": EmailIntent.REQUEST_PRICING.value,
                "confidence": 0.85,
                "reasoning": "Heuristic match for pricing/budget inquiry keywords.",
                "suggested_action": "CREATE_PRICING_REPLY_TASK",
            }

        if any(
            w in lower
            for w in [
                "more info",
                "tell me more",
                "how does it work",
                "case study",
                "portfolio",
                "details",
            ]
        ):
            return {
                "intent": EmailIntent.REQUEST_MORE_INFO.value,
                "confidence": 0.80,
                "reasoning": "Heuristic match for information request.",
                "suggested_action": "CREATE_RESPONSE_TASK",
            }

        if any(
            w in lower
            for w in [
                "not interested",
                "unsubscribe",
                "remove me",
                "stop emailing",
                "no thanks",
                "spam",
            ]
        ):
            return {
                "intent": EmailIntent.NOT_INTERESTED.value,
                "confidence": 0.90,
                "reasoning": "Heuristic match for negative response or opt-out.",
                "suggested_action": "MARK_DISQUALIFIED",
            }

        if any(
            w in lower
            for w in [
                "out of office",
                "on vacation",
                "auto-reply",
                "away from my desk",
                "back on",
            ]
        ):
            return {
                "intent": EmailIntent.OUT_OF_OFFICE.value,
                "confidence": 0.95,
                "reasoning": "Heuristic match for automated out-of-office message.",
                "suggested_action": "SCHEDULE_LATER",
            }

        if any(
            w in lower
            for w in [
                "sounds good",
                "interested",
                "yes",
                "great",
                "let's do it",
                "send over",
            ]
        ):
            return {
                "intent": EmailIntent.INTERESTED.value,
                "confidence": 0.75,
                "reasoning": "Heuristic match for positive sentiment.",
                "suggested_action": "CREATE_FOLLOWUP_TASK",
            }

        return {
            "intent": EmailIntent.AMBIGUOUS.value,
            "confidence": 0.50,
            "reasoning": "Unable to determine intent with heuristics.",
            "suggested_action": "CREATE_RESPONSE_TASK",
        }

    async def analyze_message(
        self,
        lead_name: str,
        company_name: str,
        message_body: str,
        current_intent: str | None = None,
    ) -> dict[str, Any]:
        if current_intent and current_intent != EmailIntent.AMBIGUOUS.value:
            return {
                "intent": current_intent,
                "confidence": 0.95,
                "reasoning": "Pre-classified by communication service.",
                "suggested_action": f"PROCESS_{current_intent}",
            }

        system_prompt = (
            "You are an expert SDR conversation classifier. Analyze the prospect's email response "
            "and classify it into one of the following intents: "
            "REQUEST_MEETING, REQUEST_PRICING, REQUEST_MORE_INFO, INTERESTED, "
            "NEGOTIATING, NOT_INTERESTED, OUT_OF_OFFICE, BOUNCE, UNSUBSCRIBE. "
            "Output a JSON object with keys: intent (str), confidence (float between 0 and 1), "
            "reasoning (str), suggested_action (str)."
        )

        user_prompt = (
            f"Lead Contact: {lead_name}\n"
            f"Company: {company_name}\n\n"
            f"Email Message Body:\n"
            f"'''\n{message_body}\n'''\n\n"
            f"Classify the intent accurately."
        )

        result = await self.llm.generate_json(
            prompt=user_prompt, system_prompt=system_prompt
        )
        if result and "intent" in result:
            return result

        logger.info("Using heuristic classifier for conversation analysis.")
        return self._heuristic_classify(message_body)
