"""
Unit tests for Prompt Generation, Proposal Generator, and Outreach Preparer (Layers 4, 6, 7).
"""

import pytest
import sniffio
from MicroServices.SDR.opportunity_engine import OpportunityEngine
from MicroServices.SDR.outreach_preparer import OutreachPreparer
from MicroServices.SDR.prompt_generator import PromptGenerator
from MicroServices.SDR.proposal_generator import ProposalGenerator


@pytest.fixture(autouse=True)
def set_async_lib():
    token = sniffio.current_async_library_cvar.set("asyncio")
    yield
    sniffio.current_async_library_cvar.reset(token)


@pytest.mark.asyncio
async def test_end_to_end_sdr_intelligence_layers():
    company = "Atlas Aesthetic Clinic"
    website = "https://atlaskliniek.example.com"
    industry = "Healthcare & Medical"

    seo_data = {
        "url": website,
        "overall_seo_score": 68,
        "scores": {
            "technical": 65.0,
            "onpage": 70.0,
            "content": 72.0,
            "performance": 55.0,
            "schema": 40.0,
            "local": 50.0,
            "conversion": 50.0,
        },
        "issues": ["Missing MedicalBusiness schema", "High TTFB (1.8s)"],
        "conversion_signals": {"has_booking_engine": False, "has_live_chat": False},
    }
    business_data = {
        "business_score": 65.0,
        "weaknesses": ["Slow lead response", "No automated booking funnel"],
        "competitor_insights": "Local clinics offer instant online consultation booking.",
    }

    # 1. Layer 5: Opportunity Engine
    offers = OpportunityEngine.evaluate_opportunities(
        seo_data=seo_data,
        business_data=business_data,
        has_website=True,
    )
    assert len(offers) >= 3
    assert offers[0].priority_score >= offers[-1].priority_score

    # 2. Layer 4: Prompt Generation Layer
    prompt_gen = PromptGenerator()
    prompt_pack = await prompt_gen.generate_sales_context(
        company_name=company,
        website_url=website,
        industry=industry,
        seo_data=seo_data,
        business_data=business_data,
    )
    assert len(prompt_pack.key_problems) >= 1
    assert len(prompt_pack.value_angles) >= 1
    assert len(prompt_pack.proof_points) >= 1
    assert len(prompt_pack.objections_and_responses) >= 2

    # 3. Layer 6: Proposal Generator
    proposal = ProposalGenerator.generate_proposal(
        company_name=company,
        website_url=website,
        prompt_pack=prompt_pack,
        offers=offers,
        seo_data=seo_data,
        business_data=business_data,
    )
    assert proposal.company_name == company
    assert len(proposal.deliverables) >= 2
    assert "one_time_investment_usd" in proposal.investment_matrix
    assert len(proposal.next_steps) >= 2
    assert "# Digital Growth & Optimization Proposal" in proposal.markdown_content

    # 4. Layer 7: Outreach Preparation
    outreach = OutreachPreparer.prepare_outreach(
        company_name=company,
        website_url=website,
        contact_name="Dr. De Smet",
        prompt_pack=prompt_pack,
        proposal=proposal,
        top_offers=offers,
    )
    assert len(outreach.email_sequence) == 3
    assert company in outreach.email_sequence[0].subject
    assert "Dr. De Smet" in outreach.email_sequence[0].body
    assert outreach.cold_call_script.owner_opener_15s != ""
    assert len(outreach.cold_call_script.objection_counters) >= 2
    assert "Dr. De Smet" in outreach.linkedin_connection_note
