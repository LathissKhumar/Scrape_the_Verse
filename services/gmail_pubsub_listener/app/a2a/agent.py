"""CommunicationAgent managing Agent-to-Agent discovery and execution."""

from typing import Any

from app.a2a.skills import (
    skill_classify_email,
    skill_get_message,
    skill_get_thread,
    skill_send_email,
    skill_sync_mailbox,
)


class CommunicationAgent:
    def __init__(self):
        self.skills = {
            "send_email": skill_send_email,
            "get_thread": skill_get_thread,
            "get_message": skill_get_message,
            "sync_mailbox": skill_sync_mailbox,
            "classify_email": skill_classify_email,
        }

    def get_agent_card(self) -> dict[str, Any]:
        """Returns the A2A Agent Card for discovery at /.well-known/agent-card.json."""
        return {
            "schema_version": "1.0",
            "name": "CommunicationAgent",
            "description": "Zero-cloud Communication Service managing Gmail IMAP IDLE real-time ingestion, SMTP outbound messaging, intent classification, and conversation threading for AgencyOS.",
            "url": "http://localhost:8083",
            "skills": [
                {
                    "name": "send_email",
                    "description": "Send an outbound email or thread-aware reply via Gmail SMTP.",
                    "parameters": {
                        "to": "list of recipient email addresses",
                        "subject": "email subject",
                        "body_text": "plain text body content",
                        "lead_id": "optional associated lead ID",
                        "thread_id": "optional conversation thread ID for threading",
                    },
                },
                {
                    "name": "get_thread",
                    "description": "Retrieve complete conversation timeline for a given thread.",
                    "parameters": {"thread_id": "unique thread ID"},
                },
                {
                    "name": "get_message",
                    "description": "Fetch parsed email and classification intent by message ID.",
                    "parameters": {"message_id": "unique message ID"},
                },
                {
                    "name": "sync_mailbox",
                    "description": "Trigger on-demand incremental mailbox synchronization.",
                    "parameters": {"mailbox": "mailbox name, default INBOX"},
                },
                {
                    "name": "classify_email",
                    "description": "Classify intent of an email body using rules + local Qwen LLM.",
                    "parameters": {"subject": "subject", "body": "email body text"},
                },
            ],
        }

    async def execute_skill(self, skill_name: str, params: dict[str, Any]) -> Any:
        handler = self.skills.get(skill_name)
        if not handler:
            raise ValueError(f"Skill '{skill_name}' not found.")
        return await handler(params)


communication_agent = CommunicationAgent()
