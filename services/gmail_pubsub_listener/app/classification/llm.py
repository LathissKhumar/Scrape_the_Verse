"""Local LLM-based intent classifier using Ollama and Qwen."""

import json
import logging

import httpx

from app.classification.rules import RuleClassifier
from app.config import get_settings
from app.persistence.models import ClassificationRecord

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "INTERESTED",
    "REQUEST_PRICING",
    "REQUEST_MEETING",
    "QUESTION",
    "REQUEST_MORE_INFO",
    "NOT_INTERESTED",
    "OUT_OF_OFFICE",
    "BOUNCE",
    "UNSUBSCRIBE",
    "UNKNOWN",
}

SYSTEM_PROMPT = """You are an AI email intent classifier for an agency communication system.
Classify the given email into EXACTLY ONE of the following canonical intents:
- INTERESTED: Prospect expresses interest in services or proposals.
- REQUEST_PRICING: Prospect asks about costs, pricing, or rates.
- REQUEST_MEETING: Prospect asks to schedule a call, demo, or meeting.
- QUESTION: Prospect has specific questions regarding capabilities or process.
- REQUEST_MORE_INFO: Prospect requests more case studies, deck, or details.
- NOT_INTERESTED: Prospect declines the offer.
- OUT_OF_OFFICE: Automated out-of-office response.
- BOUNCE: Mailbox or delivery failure.
- UNSUBSCRIBE: Prospect asks to stop contact.
- UNKNOWN: Cannot determine or unrelated chatter.

Respond ONLY with valid JSON in this exact structure:
{
  "intent": "<ONE_OF_THE_INTENTS_ABOVE>",
  "confidence": <float between 0.0 and 1.0>,
  "reason": "<short explanation>",
  "suggested_action": "<action name or null>"
}"""


class LLMClassifier:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        settings = get_settings()
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def classify_message(
        self, message_id: str, subject: str | None, body: str | None
    ) -> ClassificationRecord:
        """First runs fast deterministic rules; if ambiguous, queries local Ollama."""
        rule_result = RuleClassifier.classify(message_id, subject, body)
        if rule_result:
            return rule_result

        # Ambiguous message -> Call local Ollama LLM
        return await self._call_ollama(message_id, subject, body)

    async def _call_ollama(
        self, message_id: str, subject: str | None, body: str | None
    ) -> ClassificationRecord:
        email_content = (
            f"Subject: {subject or 'No Subject'}\n\nBody:\n{body or 'No Body'}"
        )
        prompt = f"Classify this email:\n\n{email_content}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        "format": "json",
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("message", {}).get("content", "{}")
                    parsed = json.loads(content)

                    intent = parsed.get("intent", "UNKNOWN").upper()
                    if intent not in VALID_INTENTS:
                        intent = "UNKNOWN"

                    confidence = float(parsed.get("confidence", 0.75))
                    reason = str(parsed.get("reason", "Classified by local LLM"))
                    action = parsed.get("suggested_action")

                    return ClassificationRecord(
                        message_id=message_id,
                        intent=intent,
                        confidence=confidence,
                        reason=reason,
                        suggested_action=action,
                        model=f"ollama/{self.model}",
                    )
                else:
                    logger.warning(
                        f"Ollama returned status {response.status_code}: {response.text}"
                    )
        except Exception as e:
            logger.info(
                f"Ollama local model unavailable or timed out: {e}. Falling back to default."
            )

        # Fallback if Ollama is not currently running
        return ClassificationRecord(
            message_id=message_id,
            intent="UNKNOWN",
            confidence=0.5,
            reason="Ambiguous email body and local LLM was offline.",
            suggested_action="manual_review",
            model="fallback",
        )


llm_classifier = LLMClassifier()
