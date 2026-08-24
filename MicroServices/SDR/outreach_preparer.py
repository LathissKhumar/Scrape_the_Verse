"""
Outreach Preparation Layer (Layer 7 in AI SDR Architecture).
Generates a multi-touch omnichannel outreach pack:
- 3-Step Cold Email Sequence (Hook -> Value/Proof -> Soft Breakup)
- Dynamic Cold Call Script (Gatekeeper, Owner 15s Hook, Objection Branches, Meeting Close)
- LinkedIn Connection & Message
- SMS / WhatsApp Teaser
"""

from pydantic import BaseModel, Field

from .opportunity_engine import SelectedOffer
from .prompt_generator import PersonalizedPromptPack
from .proposal_generator import ProposalDocument


class ColdEmailStep(BaseModel):
    step_number: int
    day_delay: int
    subject: str
    body: str


class CallScriptStructure(BaseModel):
    gatekeeper_opener: str
    owner_opener_15s: str
    value_hook: str
    call_to_action_close: str
    objection_counters: list[dict[str, str]] = Field(default_factory=list)


class OmnichannelOutreachPack(BaseModel):
    email_sequence: list[ColdEmailStep] = Field(default_factory=list)
    cold_call_script: CallScriptStructure
    linkedin_connection_note: str
    linkedin_followup_message: str
    sms_whatsapp_teaser: str


class OutreachPreparer:
    """
    Crafts customized omnichannel outreach assets for sales execution.
    """

    @classmethod
    def prepare_outreach(
        cls,
        company_name: str,
        website_url: str | None,
        contact_name: str | None,
        prompt_pack: PersonalizedPromptPack,
        proposal: ProposalDocument,
        top_offers: list[SelectedOffer],
    ) -> OmnichannelOutreachPack:
        name = contact_name or "there"
        top_problem = (
            prompt_pack.key_problems[0]
            if prompt_pack.key_problems
            else "digital growth barriers"
        )
        primary_service = (
            top_offers[0].service_title if top_offers else "Conversion Architecture"
        )
        proof_point = (
            prompt_pack.proof_points[0]
            if prompt_pack.proof_points
            else "Clients average +35% higher inbound calls."
        )

        # 1. Email Sequence (3 Touches)
        email_sequence = [
            ColdEmailStep(
                step_number=1,
                day_delay=0,
                subject=f"Quick question regarding {company_name}'s website audit",
                body=(
                    f"Hi {name},\n\n"
                    f"I was recently reviewing {company_name}'s digital presence ({website_url or 'in your local area'}) and ran a technical performance audit.\n\n"
                    f"We noticed a critical item that may be leaking customer inquiries: {top_problem}.\n\n"
                    f"We prepared a quick 3-point action plan to address this: {primary_service}.\n\n"
                    f"Would you be open to a brief 10-minute chat this week to review the findings?\n\n"
                    f"Best regards,\n"
                    f"AgencyOS Growth Team"
                ),
            ),
            ColdEmailStep(
                step_number=2,
                day_delay=3,
                subject=f"Re: Quick question regarding {company_name}'s website audit",
                body=(
                    f"Hi {name},\n\n"
                    f"Wanted to share a quick data point from similar local businesses: {proof_point}\n\n"
                    f"We can implement these exact optimizations for {company_name} in under 2 weeks without disrupting your operations.\n\n"
                    f"Let me know if Thursday or Friday works for a quick screen share.\n\n"
                    f"Best,\nAgencyOS Team"
                ),
            ),
            ColdEmailStep(
                step_number=3,
                day_delay=7,
                subject=f"Closing the loop for {company_name}",
                body=(
                    f"Hi {name},\n\n"
                    f"I haven't heard back, so I assume addressing {top_problem} isn't a priority for {company_name} right now.\n\n"
                    f"I'll close your audit file for now. If you'd like to revisit in the future, feel free to reach out anytime.\n\n"
                    f"Wishing you continued success!\n\n"
                    f"Best,\nAgencyOS Team"
                ),
            ),
        ]

        # 2. Dynamic Call Script
        cold_call_script = CallScriptStructure(
            gatekeeper_opener=(
                f"Hi, I'm calling for {name or 'the business owner'}. "
                f"We recently completed a technical digital audit of {company_name}'s customer intake funnel and had a quick question regarding their web listings."
            ),
            owner_opener_15s=(
                f"Hi {name}, this is with the AgencyOS Growth team. "
                f"I'm calling because our audit of {company_name} uncovered a couple specific items with {top_problem} that are likely costing you booked client appointments. Do you have 30 seconds?"
            ),
            value_hook=(
                f"We specialize in {primary_service}. "
                f"For businesses in your area, our fixes typically generate a 35% boost in booked phone calls within 3 weeks."
            ),
            call_to_action_close=(
                "I can email you the 1-page report and follow up with a quick 10-minute walkthrough on Thursday. Does morning or afternoon work better?"
            ),
            objection_counters=prompt_pack.objections_and_responses,
        )

        # 3. LinkedIn Notes
        linkedin_connection_note = (
            f"Hi {name}, noticed your work at {company_name}. We ran a complimentary site speed & Local SEO analysis "
            f"for {company_name} and found a couple quick wins for {primary_service}. Happy to connect and share the report!"
        )

        linkedin_followup_message = (
            f"Thanks for connecting, {name}! In case it's helpful, here is the executive summary from the audit: "
            f"Fixing {top_problem} can substantially increase your local search calls. Let me know if you'd like to see the full checklist."
        )

        # 4. SMS / WhatsApp Teaser
        sms_whatsapp_teaser = (
            f"Hi {name}, this is the Growth Team. We ran a complimentary digital audit for {company_name} "
            f"and spotted a quick fix for {top_problem}. Let us know if you'd like the 1-page report sent over!"
        )

        return OmnichannelOutreachPack(
            email_sequence=email_sequence,
            cold_call_script=cold_call_script,
            linkedin_connection_note=linkedin_connection_note,
            linkedin_followup_message=linkedin_followup_message,
            sms_whatsapp_teaser=sms_whatsapp_teaser,
        )
