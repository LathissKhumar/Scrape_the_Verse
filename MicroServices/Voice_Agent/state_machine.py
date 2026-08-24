"""
Voice Agent Multi-Turn Conversational State Engine.
Orchestrates sales dialogue across conversational states with real-time LLM reasoning
(Ollama / Gemini Flash fallback) and high-speed NLP heuristic fallback.
Includes high-EQ 2-strike soft-rejection handling with free PDF audit dispatch.
"""

import asyncio
import logging
from typing import Any

from MicroServices.Lead_Manager.agents.llm_factory import LLMClient

from .domain.call_session import (
    CallDisposition,
    CallSession,
    CallStatus,
    CallTurn,
)

logger = logging.getLogger("VoiceConversationEngine")


class VoiceConversationEngine:
    """
    Drives dynamic, context-aware dialogue across conversational states during live phone calls.
    Listens actively, classifies sentiment/intent, handles objections, answers questions,
    and gently soft-convinces on initial 'No' by offering a free audit PDF before final polite exit.
    """

    STATES = ["OPENING", "PITCH", "FAQ_AND_OBJECTIONS", "MEETING_BOOKING", "CLOSING"]

    def __init__(
        self,
        company_name: str,
        contact_name: str | None = None,
        has_website: bool = True,
        prompt_pack: dict[str, Any] | None = None,
        llm_client: LLMClient | None = None,
    ):
        self.company_name = company_name
        self.contact_name = contact_name
        self.has_website = has_website
        self.prompt_pack = prompt_pack or {}
        self.llm = llm_client or LLMClient()

        self.current_state = "OPENING"
        self.transcript: list[CallTurn] = []
        self.disposition: CallDisposition | None = None
        self.interest_score = 50.0
        self.booked_meeting_time: str | None = None
        self.rejection_count: int = 0
        self.pdf_audit_sent: bool = False

    def start_conversation(self) -> str:
        """Generates natural, spoken opening greeting from agent."""
        name = self.contact_name or "there"
        if not self.has_website:
            opening = (
                f"Hi {name}, Sarah here with AgencyOS. "
                f"We noticed {self.company_name} doesn't have a mobile website or Google Maps listing yet. "
                f"Do you have a quick 30 seconds?"
            )
        else:
            opening = (
                f"Hi {name}, Sarah here with AgencyOS. "
                f"We ran a quick digital audit on {self.company_name}'s site and spotted 2 speed fixes. "
                f"Do you have 30 seconds?"
            )
        self.transcript.append(CallTurn(speaker="agent", text=opening))
        return opening

    async def process_turn_async(self, user_utterance: str) -> dict[str, Any]:
        """
        Asynchronously process caller speech with real-time LLM reasoning.
        Falls back to enhanced heuristic engine if LLM times out or is offline.
        """
        user_speech = user_utterance.strip()
        if not user_speech:
            user_speech = "..."

        # Record prospect turn
        self.transcript.append(CallTurn(speaker="prospect", text=user_speech))

        # 1. Attempt Real-Time Fast LLM Reasoning
        llm_result = await self._run_llm_reasoning(user_speech)
        if llm_result:
            return self._apply_llm_turn(llm_result)

        # 2. Fallback to High-Speed Heuristic Engine
        logger.info("Using enhanced heuristic conversation fallback engine.")
        return self._process_turn_heuristics(user_speech)

    def process_turn(self, user_utterance: str) -> dict[str, Any]:
        """Synchronous wrapper for test compatibility."""
        user_speech = user_utterance.strip()
        if not user_speech:
            user_speech = "..."

        self.transcript.append(CallTurn(speaker="prospect", text=user_speech))
        return self._process_turn_heuristics(user_speech)

    async def _run_llm_reasoning(self, user_speech: str) -> dict[str, Any] | None:
        """Invokes LLM with a 1.5-second strict timeout for natural telephony latency."""
        try:
            transcript_lines = []
            for t in self.transcript[-6:]:
                speaker_label = "Agent" if t.speaker == "agent" else "Prospect"
                transcript_lines.append(f"{speaker_label}: {t.text}")
            formatted_transcript = "\n".join(transcript_lines)

            seo_issues = self.prompt_pack.get(
                "key_problems",
                ["Mobile page speed bottlenecks", "Missing local schema"],
            )
            value_angles = self.prompt_pack.get(
                "value_angles", ["Convert 2x more mobile inquiries into booked calls"]
            )

            system_prompt = (
                "You are Sarah, a warm, professional, high-EQ phone sales specialist at AgencyOS. "
                "You are having a live voice phone call with a business owner.\n\n"
                "CRITICAL SPOKEN TELEPHONY RULES:\n"
                "1. Spoken responses MUST be ultra-concise (10 to 22 words MAX). Never speak long paragraphs.\n"
                "2. Speak naturally like a real human. Use warm conversational softeners ('Got it', 'Totally understand', 'Makes sense').\n"
                "3. FIRST 'NO' OR HESITATION: Warmly empathize and offer to simply shoot over their free 1-page website/SEO audit PDF with zero commitment.\n"
                "4. SECOND 'NO', 'STOP CALLING', OR 'DON'T EMAIL': Immediately apologize, thank them, and exit politely without pushing.\n"
                "5. If the prospect asks a question (pricing, what's wrong with site, AI identity): Answer directly in ONE sentence and re-engage.\n"
                "6. If the prospect mentions a time/day (e.g., Thursday, tomorrow at 2): Confirm enthusiastically.\n\n"
                "Return a JSON object with keys:\n"
                "{\n"
                '  "spoken_response": "10-22 word natural conversational reply",\n'
                '  "detected_intent": "HARD_NEGATIVE | SOFT_NEGATIVE_PIVOT | SOFT_OBJECTION | QUESTION | POSITIVE_INTEREST | SCHEDULING | REQUEST_EMAIL | BUSY_CALLBACK",\n'
                '  "new_state": "PITCH | FAQ_AND_OBJECTIONS | MEETING_BOOKING | CLOSING",\n'
                '  "disposition": "MEETING_BOOKED | INTERESTED | REQUESTED_INFO | NOT_INTERESTED | CALL_BACK_LATER",\n'
                '  "interest_score": 0 to 100\n'
                "}"
            )

            user_prompt = (
                f"Target Business: {self.company_name} ({self.contact_name or 'Owner'})\n"
                f"Website Status: {'Has Website' if self.has_website else 'No Website'}\n"
                f"Identified Flaws: {', '.join(seo_issues[:2])}\n"
                f"Value Angles: {', '.join(value_angles[:2])}\n"
                f"Current State: {self.current_state} (Rejection Count: {self.rejection_count})\n\n"
                f"Recent Transcript:\n{formatted_transcript}\n\n"
                f'Prospect just said: "{user_speech}"\n'
                f"Generate the exact spoken response and intent JSON."
            )

            result = await asyncio.wait_for(
                self.llm.generate_json(prompt=user_prompt, system_prompt=system_prompt),
                timeout=1.5,
            )
            if result and isinstance(result, dict) and "spoken_response" in result:
                return result
        except Exception as e:
            logger.debug(
                f"LLM voice generation timed out or failed ({e}), switching to heuristic engine."
            )
        return None

    def _apply_llm_turn(self, llm_result: dict[str, Any]) -> dict[str, Any]:
        """Applies structured LLM result to engine state."""
        reply = llm_result.get(
            "spoken_response", "Thank you for your time. Have a great day!"
        )
        intent = llm_result.get("detected_intent", "POSITIVE_INTEREST")
        new_state = llm_result.get("new_state", self.current_state)
        disp_str = llm_result.get("disposition", "INTERESTED")
        score = float(llm_result.get("interest_score", 50.0))

        try:
            self.disposition = CallDisposition[disp_str]
        except Exception:
            self.disposition = CallDisposition.INTERESTED

        self.current_state = new_state
        self.interest_score = score

        if intent in ("HARD_NEGATIVE", "SOFT_NEGATIVE_PIVOT"):
            self.rejection_count += 1

        if intent == "HARD_NEGATIVE" or self.rejection_count >= 2:
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.NOT_INTERESTED
            self.interest_score = 10.0
        elif intent == "SCHEDULING":
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.MEETING_BOOKED
            self.interest_score = 95.0
            self.booked_meeting_time = "2026-08-27T14:00:00Z"
        elif intent in ("REQUEST_EMAIL", "SOFT_NEGATIVE_PIVOT"):
            self.pdf_audit_sent = True
            self.disposition = CallDisposition.REQUESTED_INFO
        elif intent == "BUSY_CALLBACK":
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.CALL_BACK_LATER
            self.interest_score = 45.0

        self.transcript.append(
            CallTurn(speaker="agent", text=reply, intent_detected=intent)
        )
        return {
            "agent_response": reply,
            "new_state": self.current_state,
            "disposition": self.disposition,
            "intent": intent,
        }

    def _process_turn_heuristics(self, user_speech: str) -> dict[str, Any]:
        """
        High-Speed NLP Heuristic Engine.
        Accurately classifies sentiment, objections, questions, and booking intent.
        Implements 2-strike soft convincing with free audit PDF on initial 'No'.
        """
        speech_lower = user_speech.lower()
        tokens = set(
            speech_lower.replace(",", " ")
            .replace(".", " ")
            .replace("!", " ")
            .replace("?", " ")
            .split()
        )

        # 1. BUSY / CALL BACK LATER
        busy_signals = [
            "busy",
            "driving",
            "in a meeting",
            "bad time",
            "call back",
            "call later",
            "cant talk",
            "cannot talk",
            "call me back",
            "reach back out",
        ]
        if any(w in speech_lower for w in busy_signals):
            reply = "No problem at all! When would be a better time for me to reach back out?"
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="BUSY_CALLBACK")
            )
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.CALL_BACK_LATER
            self.interest_score = 45.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "BUSY_CALLBACK",
            }

        # 2. NEGATIVE / REJECTION EVALUATION (2-Strike Soft-Convince Engine)
        negative_words = {"no", "nah", "nope", "never"}
        negative_phrases = [
            "not interested",
            "stop calling",
            "remove me",
            "don't call",
            "don't email",
            "no thanks",
            "no thank you",
            "take me off",
            "leave me alone",
            "don't need",
            "not looking",
            "not for us",
            "wrong number",
            "uninterested",
        ]
        has_negative_token = bool(tokens & negative_words)
        has_negative_phrase = any(phrase in speech_lower for phrase in negative_phrases)

        # Check for hard DNC phrases that skip soft-convince (immediate exit)
        hard_dnc_phrases = [
            "stop calling",
            "remove me",
            "take me off",
            "leave me alone",
            "never call",
            "don't email",
            "wrong number",
        ]
        is_hard_dnc = any(p in speech_lower for p in hard_dnc_phrases)

        if (has_negative_token or has_negative_phrase) and not any(
            pos in speech_lower
            for pos in ["no problem", "why not", "no doubt", "no worries"]
        ):
            self.rejection_count += 1

            # If it's a hard DNC or the second rejection -> Leave immediately
            if is_hard_dnc or self.rejection_count >= 2:
                reply = "Understood completely! I appreciate your time and will update our records so we don't contact you again. Have a wonderful day!"
                self.transcript.append(
                    CallTurn(
                        speaker="agent", text=reply, intent_detected="HARD_NEGATIVE"
                    )
                )
                self.current_state = "CLOSING"
                self.disposition = CallDisposition.NOT_INTERESTED
                self.interest_score = 10.0
                return {
                    "agent_response": reply,
                    "new_state": self.current_state,
                    "disposition": self.disposition,
                    "intent": "HARD_NEGATIVE",
                }
            else:
                # FIRST REJECTION: Soft-convince gently with the free audit PDF
                reply = (
                    f"Totally understand! We actually already prepared a complimentary 1-page website audit PDF for {self.company_name}. "
                    f"Can I at least shoot that over to your email for your records?"
                )
                self.transcript.append(
                    CallTurn(
                        speaker="agent",
                        text=reply,
                        intent_detected="SOFT_NEGATIVE_PIVOT",
                    )
                )
                self.current_state = "FAQ_AND_OBJECTIONS"
                self.disposition = CallDisposition.REQUESTED_INFO
                self.interest_score = 40.0
                return {
                    "agent_response": reply,
                    "new_state": self.current_state,
                    "disposition": self.disposition,
                    "intent": "SOFT_NEGATIVE_PIVOT",
                }

        # 3. DIRECT QUESTIONS (Pricing, What is wrong, Identity, AI)
        if any(
            w in speech_lower
            for w in [
                "how much",
                "pricing",
                "what's the cost",
                "what does it cost",
                "is it free",
            ]
        ):
            reply = (
                "Our initial audit and 1-page PDF report are completely free with zero obligation. "
                "Can I email that over for you to review?"
            )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="QUESTION")
            )
            self.current_state = "FAQ_AND_OBJECTIONS"
            self.disposition = CallDisposition.INTERESTED
            self.interest_score = 65.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "QUESTION",
            }

        if any(
            w in speech_lower
            for w in [
                "what's wrong",
                "what issues",
                "what did you find",
                "what flaws",
                "explain",
            ]
        ):
            if self.has_website:
                reply = (
                    f"We noticed {self.company_name}'s mobile site takes over 4 seconds to load, which hurts Google rankings. "
                    f"Would you like our free 1-page PDF audit?"
                )
            else:
                reply = (
                    f"{self.company_name} is missing a mobile-friendly site and Google 3-Pack listing. "
                    f"Can I send you a quick PDF preview of how it would look?"
                )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="QUESTION")
            )
            self.current_state = "PITCH"
            self.disposition = CallDisposition.INTERESTED
            self.interest_score = 70.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "QUESTION",
            }

        if any(
            w in speech_lower
            for w in ["are you a robot", "are you ai", "are you real", "is this an ai"]
        ):
            reply = (
                "I'm an AI assistant with the AgencyOS Growth team! "
                "We spotted a few high-impact fixes for your site. Would you like to see the free PDF report?"
            )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="QUESTION")
            )
            self.current_state = "FAQ_AND_OBJECTIONS"
            self.disposition = CallDisposition.INTERESTED
            self.interest_score = 60.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "QUESTION",
            }

        # 4. OBJECTION HANDLING (Already have designer / word of mouth / no budget)
        if any(
            w in speech_lower
            for w in [
                "already have",
                "existing agency",
                "web designer",
                "web guy",
                "in-house",
                "developer",
            ]
        ):
            reply = (
                "That's great! Our technical PDF report has diagnostics your web team can apply for free. "
                "What is the best email to send that to?"
            )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="SOFT_OBJECTION")
            )
            self.current_state = "FAQ_AND_OBJECTIONS"
            self.disposition = CallDisposition.REQUESTED_INFO
            self.pdf_audit_sent = True
            self.interest_score = 60.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "SOFT_OBJECTION",
            }

        if any(
            w in speech_lower
            for w in ["word of mouth", "referrals", "don't need marketing"]
        ):
            reply = (
                "Word of mouth is fantastic! When referrals look you up on mobile, a fast site locks in the booking. "
                "Can I send over the free 1-page PDF overview?"
            )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="SOFT_OBJECTION")
            )
            self.current_state = "FAQ_AND_OBJECTIONS"
            self.disposition = CallDisposition.INTERESTED
            self.interest_score = 60.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "SOFT_OBJECTION",
            }

        # 5. SCHEDULING / CALENDAR BOOKING
        time_keywords = [
            "thursday",
            "friday",
            "tomorrow",
            "monday",
            "tuesday",
            "wednesday",
            "saturday",
            "2 pm",
            "3 pm",
            "10 am",
            "11 am",
            "morning",
            "afternoon",
            "let's connect",
            "book it",
            "schedule",
        ]
        if any(w in speech_lower for w in time_keywords):
            self.booked_meeting_time = "2026-08-27T14:00:00Z"
            reply = (
                "Perfect! I have marked down our 10-minute discovery call. "
                "I will email you the calendar confirmation and the audit document right away. Speak soon!"
            )
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="SCHEDULING")
            )
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.MEETING_BOOKED
            self.interest_score = 95.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "SCHEDULING",
            }

        # 6. REQUEST EMAIL / SEND PDF REPORT
        email_pdf_signals = [
            "email me",
            "send it",
            "send email",
            "send the details",
            "send me the report",
            "send the pdf",
            "shoot me an email",
            "sure send it",
            "go ahead and send",
            "email it",
            "email over",
            "email the",
            "send over",
            "email the free pdf",
        ]
        has_email_request = (
            any(w in speech_lower for w in email_pdf_signals)
            or (
                "email" in speech_lower
                and any(
                    w in speech_lower
                    for w in ["pdf", "report", "audit", "free", "summary", "over"]
                )
            )
            or (
                "send" in speech_lower
                and any(
                    w in speech_lower
                    for w in ["pdf", "report", "audit", "free", "summary", "over"]
                )
            )
        )
        if has_email_request:
            self.pdf_audit_sent = True
            reply = "Will do! I'll email the free 1-page audit PDF over to your inbox. Have a wonderful day!"
            self.transcript.append(
                CallTurn(speaker="agent", text=reply, intent_detected="REQUEST_EMAIL")
            )
            self.current_state = "CLOSING"
            self.disposition = CallDisposition.REQUESTED_INFO
            self.interest_score = 70.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "REQUEST_EMAIL",
            }

        # 7. POSITIVE INTEREST / AFFIRMATION
        positive_keywords = [
            "yes",
            "sure",
            "tell me more",
            "go ahead",
            "okay",
            "sounds good",
            "interested",
            "who is this",
            "how can i help",
        ]
        if any(w in speech_lower for w in positive_keywords) or bool(
            tokens & {"yes", "yeah", "yep", "sure", "okay", "ok"}
        ):
            if self.current_state == "OPENING":
                if not self.has_website:
                    reply = (
                        f"Great! We help businesses launch turnkey mobile sites that bring 15+ new client inquiries a month. "
                        f"Are you taking on new clients for {self.company_name}?"
                    )
                else:
                    reply = (
                        f"Great! We found 2 quick mobile speed bottlenecks on {self.company_name}'s site. "
                        f"Would you be open to seeing our free 1-page PDF audit?"
                    )
                self.current_state = "PITCH"
            elif self.current_state in ("FAQ_AND_OBJECTIONS", "PITCH"):
                # If they agreed to see the PDF / report
                self.pdf_audit_sent = True
                reply = (
                    "Awesome! I'll email the free audit PDF over right now. "
                    "Does Thursday afternoon or Friday morning work better if you'd like a quick 5-minute walkthrough?"
                )
                self.current_state = "MEETING_BOOKING"
            else:
                reply = (
                    "Fantastic! I can email you the full breakdown and set up a quick 10-minute chat. "
                    "Does Thursday afternoon or Friday morning work better?"
                )
                self.current_state = "MEETING_BOOKING"

            self.transcript.append(
                CallTurn(
                    speaker="agent", text=reply, intent_detected="POSITIVE_INTEREST"
                )
            )
            self.disposition = CallDisposition.INTERESTED
            self.interest_score = 75.0
            return {
                "agent_response": reply,
                "new_state": self.current_state,
                "disposition": self.disposition,
                "intent": "POSITIVE_INTEREST",
            }

        # Default Neutral Fallback
        reply = (
            "We put together a complimentary 1-page digital audit for your team. "
            "Would you like me to email that over for you to review?"
        )
        self.transcript.append(
            CallTurn(speaker="agent", text=reply, intent_detected="NEUTRAL")
        )
        self.current_state = "FAQ_AND_OBJECTIONS"
        self.disposition = CallDisposition.INTERESTED
        self.interest_score = 55.0
        return {
            "agent_response": reply,
            "new_state": self.current_state,
            "disposition": self.disposition,
            "intent": "NEUTRAL",
        }

    @classmethod
    def get_initial_greeting(
        cls,
        company_name: str,
        contact_name: str | None = None,
        has_website: bool = True,
    ) -> str:
        engine = cls(
            company_name=company_name,
            contact_name=contact_name,
            has_website=has_website,
        )
        return engine.start_conversation()

    @classmethod
    def process_prospect_turn(
        cls,
        session: CallSession,
        user_speech: str,
        current_state: str = "OPENING",
        call_script: dict[str, Any] | None = None,
    ) -> tuple[str, str, CallDisposition | None, float]:
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
        engine.rejection_count = session.metadata.get("rejection_count", 0)

        res = engine.process_turn(user_speech)

        session.transcript = engine.transcript
        session.disposition = engine.disposition
        session.interest_score = engine.interest_score
        session.booked_meeting_time = engine.booked_meeting_time
        session.metadata["rejection_count"] = engine.rejection_count
        session.metadata["pdf_audit_sent"] = engine.pdf_audit_sent
        if engine.current_state == "CLOSING":
            session.status = CallStatus.COMPLETED

        return (
            res["agent_response"],
            res["new_state"],
            session.disposition,
            session.interest_score,
        )
