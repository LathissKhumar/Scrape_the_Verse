"""
Telephony Adapter & Call Management for Voice Agent (Layer 9).
Handles both live Twilio PSTN calls and simulated call testing sessions with Lead Manager integration.
"""

from typing import Any, Dict, List, Optional
import httpx
from .domain.call_session import (
    CallDisposition,
    CallSession,
    CallStatus,
    CallTurn,
    utc_now_iso,
)
from .state_machine import VoiceConversationEngine


class TelephonyAdapter:
    def __init__(self, lead_manager_url: str = "http://127.0.0.1:8082"):
        self.lead_manager_url = lead_manager_url.rstrip("/")

    async def sync_session_to_lead_manager(self, session: CallSession) -> None:
        """
        Public method to synchronize a completed call session (live or simulated) to Lead Manager.
        """
        await self.dispatch_call_to_lead_manager(session)

    async def simulate_call(
        self,
        company_name: str,
        prospect_phone: Optional[str] = None,
        contact_name: Optional[str] = None,
        has_website: bool = True,
        lead_id: Optional[str] = None,
        simulated_prospect_responses: Optional[List[str]] = None,
    ) -> CallSession:
        """
        Runs an automated simulated call conversation across multiple turns.
        """
        session = CallSession(
            lead_id=lead_id,
            company_name=company_name,
            prospect_phone=prospect_phone,
            contact_name=contact_name,
            status=CallStatus.IN_PROGRESS,
            metadata={"has_website": has_website},
        )

        # 1. Initial Greeting
        greeting = VoiceConversationEngine.get_initial_greeting(
            company_name=company_name,
            contact_name=contact_name,
            has_website=has_website,
        )
        session.transcript.append(CallTurn(speaker="agent", text=greeting))

        # 2. Process simulated user turns
        turns = simulated_prospect_responses or [
            "Yes, this is they. What is this about?",
            "Sure, sounds interesting, how does your booking system work?",
            "Thursday at 2 PM works great for me.",
        ]

        current_state = "OPENING"
        for user_speech in turns:
            agent_resp, next_state, disp, score = VoiceConversationEngine.process_prospect_turn(
                session=session,
                user_speech=user_speech,
                current_state=current_state,
            )
            current_state = next_state
            if session.status == CallStatus.COMPLETED:
                break

        session.status = CallStatus.COMPLETED
        session.call_summary = (
            f"Voice call with {company_name} ({contact_name or 'Owner'}). "
            f"Disposition: {session.disposition.value if session.disposition else 'COMPLETED'}. "
            f"Interest Score: {session.interest_score}/100."
        )

        # 3. If lead_id is provided, dispatch results to Lead Manager (:8082)
        if lead_id:
            await self.dispatch_call_to_lead_manager(session)

        return session

    async def dispatch_call_to_lead_manager(self, session: CallSession) -> None:
        """
        Posts call activity, transcript, interest score, and meetings to Lead Manager.
        """
        if not session.lead_id:
            return

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                # 1. Log call activity
                event_payload = {
                    "type": "email.intent_detected" if session.disposition == CallDisposition.MEETING_BOOKED else "lead.qualified",
                    "lead_id": session.lead_id,
                    "actor": "VoiceAgent",
                    "payload": {
                        "intent": "REQUEST_MEETING" if session.disposition == CallDisposition.MEETING_BOOKED else "INTERESTED",
                        "summary": session.call_summary,
                        "interest_score": session.interest_score,
                        "disposition": session.disposition.value if session.disposition else None,
                        "transcript": [t.model_dump() for t in session.transcript],
                    },
                }
                await client.post(
                    f"{self.lead_manager_url}/api/v1/events",
                    json=event_payload,
                )

                # 2. If meeting was booked, create Meeting in Lead Manager
                if session.disposition == CallDisposition.MEETING_BOOKED:
                    meeting_payload = {
                        "lead_id": session.lead_id,
                        "title": f"Discovery Call with {session.company_name}",
                        "scheduled_at": session.booked_meeting_time or "2026-08-27T14:00:00Z",
                        "duration_minutes": 30,
                        "organizer_email": "sales@agencyos.local",
                        "attendee_email": "prospect@client.com",
                        "notes": session.call_summary,
                    }
                    await client.post(
                        f"{self.lead_manager_url}/api/v1/meetings",
                        json=meeting_payload,
                    )
            except Exception:
                pass
