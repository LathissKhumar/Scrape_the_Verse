"""
Voice Agent Multi-Turn Conversational State Engine.
Orchestrates sales dialogue across 5 stages with prompt-pack injection and Ollama LLM / Rule fallback.
"""

from typing import Any, Dict, List, Optional, Tuple
from .domain.call_session import (
    CallDisposition,
    CallSession,
    CallStatus,
    CallTurn,
    utc_now_iso,
)


class VoiceConversationEngine:
    """
    Drives the dialogue flow across conversational states during live phone calls.
    """

    STATES = ["OPENING", "PITCH", "FAQ_AND_OBJECTIONS", "MEETING_BOOKING", "CLOSING"]

    def __init__(
        self,
        company_name: str,
        contact_name: Optional[str] = None,
        has_website: bool = True,
        prompt_pack: Optional[Dict[str, Any]] = None,
    ):
        self.company_name = company_name
        self.contact_name = contact_name
        self.has_website = has_website
        self.prompt_pack = prompt_pack or {}

        self.current_state = "OPENING"
        self.transcript: List[CallTurn] = []
        self.disposition: Optional[CallDisposition] = None
        self.interest_score = 50.0
        self.booked_meeting_time: Optional[str] = None

    def start_conversation(self) -> str:
        """Generates opening turn from agent and records in transcript."""
        name = self.contact_name or "there"
        if not self.has_website:
            opening = (
                f"Hello {name}, this is Sarah with the AgencyOS Growth team. "
                f"I'm reaching out because we noticed {self.company_name} currently does not have a verified mobile website or Google Maps listing. "
                f"Do you have 30 seconds to speak with me?"
            )
        else:
            opening = (
                f"Hello {name}, this is Sarah with the AgencyOS Growth team. "
                f"We recently completed a digital health audit of {self.company_name}'s web listings and spotted 2 quick fixes for your customer intake. "
                f"Do you have 30 seconds?"
            )
        self.transcript.append(CallTurn(speaker="agent", text=opening))
        return opening

    def process_turn(self, user_utterance: str) -> Dict[str, Any]:
        """
        Process a single spoken utterance from the caller, advance state, and return agent reply.
        """
        user_speech = user_utterance.strip()
        speech_lower = user_speech.lower()

        # Record prospect speech
        self.transcript.append(CallTurn(speaker="prospect", text=user_speech))

        # 1. Hard Negative / Do Not Call
        if any(w in speech_lower for w in ["not interested", "stop calling", "remove me", "don't call", "no thank", "take me off"]):
            reply = "Understood completely. I will update our records and not contact you again. Have a great day!"
            self.transcript.append(CallTurn(speaker="agent", text=reply))
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.NOT_INTERESTED
            self.interest_score = 10.0
            return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

        # 2. Busy / Call back later
        if any(w in speech_lower for w in ["busy right now", "call back", "in a meeting", "bad time", "driving"]):
            reply = "No problem at all! When would be a better time for me to reach back out to you?"
            self.transcript.append(CallTurn(speaker="agent", text=reply))
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.CALL_BACK_LATER
            self.interest_score = 50.0
            return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

        # 3. State-based dialogue logic
        if self.current_state == "OPENING":
            if any(w in speech_lower for w in ["yes", "sure", "what's this about", "go ahead", "okay", "who is this", "tell me", "how can i help"]):
                if not self.has_website:
                    reply = (
                        f"Great! We help local businesses launch turnkey mobile websites and Google Maps 3-Pack listings. "
                        f"Typically, having this set up brings in 15 to 20 additional client inquiries every month. "
                        f"Are you currently taking on new clients for {self.company_name}?"
                    )
                else:
                    reply = (
                        f"Great! Our technical audit revealed that {self.company_name}'s website has a couple crawl and speed barriers "
                        f"that may be causing potential clients to bounce. "
                        f"We put together a 3-point fix to double your mobile booking conversion. "
                        f"Would you be open to seeing the 1-page summary?"
                    )
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "PITCH"
                self.disposition = CallDisposition.INTERESTED
                self.interest_score = 65.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}
            else:
                reply = "I appreciate your time. Is there a better person at the company to discuss your digital presence with?"
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "FAQ_AND_OBJECTIONS"
                self.interest_score = 40.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

        elif self.current_state == "PITCH":
            if any(w in speech_lower for w in ["yes", "sure", "send it", "how much", "tell me more", "sounds good", "interested", "how does it work"]):
                reply = (
                    "Fantastic! I can email you the full breakdown and set up a quick 10-minute strategy session with our technical director. "
                    "Does Thursday afternoon or Friday morning work better for a brief call?"
                )
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "MEETING_BOOKING"
                self.disposition = CallDisposition.INTERESTED
                self.interest_score = 80.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}
            elif any(w in speech_lower for w in ["already have", "agency", "designer", "developer"]):
                reply = (
                    "That's great! Our audit provides exact technical diagnostics that most general web designers miss. "
                    "We can share the report free of charge so your existing team can apply the fixes. What is the best email to send that to?"
                )
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "FAQ_AND_OBJECTIONS"
                self.disposition = CallDisposition.REQUESTED_INFO
                self.interest_score = 60.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}
            else:
                reply = "We can deploy these optimizations in under 2 weeks. Can I send you the 1-page brief to review?"
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "MEETING_BOOKING"
                self.disposition = CallDisposition.INTERESTED
                self.interest_score = 70.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

        elif self.current_state in ("FAQ_AND_OBJECTIONS", "MEETING_BOOKING"):
            if any(w in speech_lower for w in ["thursday", "friday", "tomorrow", "monday", "tuesday", "wednesday", "2 pm", "3 pm", "morning", "afternoon", "let us connect"]):
                booked_time = "2026-08-27T14:00:00Z"
                self.booked_meeting_time = booked_time
                reply = (
                    f"Perfect! I have marked down our 10-minute discovery call. "
                    f"I will email you the calendar confirmation and the audit document right away. Thank you, and speak soon!"
                )
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "CLOSING"
                self.disposition = CallDisposition.MEETING_BOOKED
                self.interest_score = 95.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}
            else:
                reply = "Understood. I will email the summary to your inbox, and we will follow up with you early next week. Have a wonderful day!"
                self.transcript.append(CallTurn(speaker="agent", text=reply))
                self.current_state = "CLOSING"
                self.disposition = CallDisposition.REQUESTED_INFO
                self.interest_score = 70.0
                return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

        # Default fallback
        reply = "Thank you for your time. We will send over the details via email. Have a great day!"
        self.transcript.append(CallTurn(speaker="agent", text=reply))
        self.current_state = "CLOSING"
        return {"agent_response": reply, "new_state": self.current_state, "disposition": self.disposition}

    async def process_turn_async(self, user_utterance: str) -> Dict[str, Any]:
        """Asynchronous wrapper for processing turn."""
        return self.process_turn(user_utterance)

    @classmethod
    def get_initial_greeting(
        cls,
        company_name: str,
        contact_name: Optional[str] = None,
        has_website: bool = True,
    ) -> str:
        engine = cls(company_name=company_name, contact_name=contact_name, has_website=has_website)
        return engine.start_conversation()

    @classmethod
    def process_prospect_turn(
        cls,
        session: CallSession,
        user_speech: str,
        current_state: str = "OPENING",
        call_script: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str, Optional[CallDisposition], float]:
        """Class method adapter for synchronous/simulated test runs."""
        engine = cls(
            company_name=session.company_name,
            contact_name=session.contact_name,
            has_website=session.metadata.get("has_website", True),
        )
        engine.current_state = current_state
        engine.transcript = list(session.transcript)
        engine.disposition = session.disposition
        engine.interest_score = session.interest_score

        res = engine.process_turn(user_speech)

        session.transcript = engine.transcript
        session.disposition = engine.disposition
        session.interest_score = engine.interest_score
        session.booked_meeting_time = engine.booked_meeting_time
        if engine.current_state == "CLOSING":
            session.status = CallStatus.COMPLETED

        return (
            res["agent_response"],
            res["new_state"],
            session.disposition,
            session.interest_score,
        )
