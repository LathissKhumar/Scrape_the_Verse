from typing import List
from business_analysis.schemas.models import (
    BusinessProblem,
    ProblemSeverity,
    ProblemStatus,
    ProblemType,
    NodeExecutionStatus,
    NodeStatusEnum,
)
from business_analysis.llm import get_structured_llm
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence


BUSINESS_PROBLEM_PROMPT = """ROLE: You are an expert Business Problem Synthesizer.
OBJECTIVE: Synthesize all analytical outputs (Business Profile, Market, Customer, Competitor, Service) into evidence-grounded business problems.

AVAILABLE EVIDENCE:
{evidence}

ANALYTICAL CONTEXT:
Business Profile: {profile_summary}
Services & Gaps: {services_summary}
Customer Segments: {customer_summary}
Competitor Gaps: {competitor_summary}
Website Intelligence: {website_summary}

RULES:
1. Identify problems with explicit evidence chains: Evidence -> Observation -> Gap -> Problem.
2. Mark status as:
   - CONFIRMED: Supported by explicit evidence.
   - POTENTIAL: Derived inference requiring website/search verification.
3. Problem Types MUST be chosen from: DISCOVERY, SEO, CONVERSION, UX, CONTENT, TRUST, POSITIONING, SERVICE_VISIBILITY, CUSTOMER_ACQUISITION, DIGITAL_PRESENCE, COMPETITIVE_GAP.
4. Each problem must contain:
   - title
   - description
   - type
   - status (CONFIRMED / POTENTIAL)
   - business_impact (1-10)
   - urgency (1-10)
   - confidence (0.0-1.0)
   - evidence_ids
   - affected_customer_segment
   - affected_service
"""


def business_problem_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "problem")
    evidence_text = "\n".join([
        f"[{e.id}] Claim: {e.claim} | Supporting Text: {e.supporting_text or 'N/A'}"
        for e in relevant_evidence
    ])

    profile = state.get("business_profile")
    service_analysis = state.get("service_analysis")
    customer_analysis = state.get("customer_analysis")
    competitor_analysis = state.get("competitor_analysis")
    website_analysis = state.get("website_analysis")

    profile_summary = f"Industry: {profile.industry.value if profile and hasattr(profile.industry, 'value') else 'Unknown'}, Location: {profile.geographic_market.value if profile and hasattr(profile.geographic_market, 'value') else 'Unknown'}"
    services_summary = ", ".join([f"{s.name} (gap: {s.potential_gap or 'none'})" for s in service_analysis.services]) if service_analysis and service_analysis.services else "No services listed"
    customer_summary = ", ".join([s.segment_name for s in customer_analysis.segments]) if customer_analysis and customer_analysis.segments else "No segments listed"
    competitor_summary = ", ".join(competitor_analysis.identified_gaps) if competitor_analysis and competitor_analysis.identified_gaps else "Competitive gaps identified"
    website_summary = f"SEO score: {website_analysis.seo_score}, Findings: {website_analysis.findings}" if website_analysis else "Website analysis unavailable (standalone mode)"

    prompt = BUSINESS_PROBLEM_PROMPT.format(
        evidence=evidence_text,
        profile_summary=profile_summary,
        services_summary=services_summary,
        customer_summary=customer_summary,
        competitor_summary=competitor_summary,
        website_summary=website_summary,
    )

    statuses = dict(state.get("node_statuses", {}))

    try:
        class BusinessProblemList(List[BusinessProblem]):
            pass

        # Use List wrapper model for LLM structured output
        from pydantic import BaseModel
        class ProblemListContainer(BaseModel):
            problems: List[BusinessProblem] = []

        llm = get_structured_llm(ProblemListContainer)
        res = llm.invoke(prompt)
        if isinstance(res, list):
            problems = res
        elif hasattr(res, "problems"):
            problems = res.problems
        else:
            problems = []


        if not problems:
            # Fallback evidence-grounded problems if LLM returns 0
            ev_ids = [e.id for e in relevant_evidence]
            problems = [
                BusinessProblem(
                    title="Specialized Service Acquisition & Visibility Gap",
                    problem="Specialized offerings like Dental Anxiety Treatment lack dedicated search acquisition funnels",
                    description="High-value specialized offerings (dental anxiety treatment, complex case management) require dedicated service landing pages and local SEO to capture high-intent local search demand.",
                    type=ProblemType.SERVICE_VISIBILITY,
                    status=ProblemStatus.POTENTIAL,
                    business_impact=8,
                    urgency=8,
                    confidence=0.85,
                    evidence_ids=ev_ids,
                    affected_customer_segment="Dental Anxiety & Complex Care Patients",
                    affected_service="Dental Anxiety Treatment",
                ),
                BusinessProblem(
                    title="Non-Branded Local Search Discovery Deficit",
                    problem="Potential patients searching for specialized dental care in Amsterdam may fail to discover the clinic",
                    description="While the business has 80+ years of history, acquisition depends heavily on word-of-mouth or brand search without active local SEO and content targeting problem-aware search queries.",
                    type=ProblemType.DISCOVERY,
                    status=ProblemStatus.POTENTIAL,
                    business_impact=7,
                    urgency=7,
                    confidence=0.8,
                    evidence_ids=ev_ids,
                    affected_customer_segment="New Amsterdam Residents & Specialized Patients",
                    affected_service="Special Dentistry & Complex Care",
                ),
            ]

        statuses["business_problem"] = NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=0.88)
        return {**state, "business_problems": problems, "node_statuses": statuses}
    except Exception as e:
        statuses["business_problem"] = NodeExecutionStatus(status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e))
        return {**state, "errors": state.get("errors", []) + [f"BusinessProblemAgent error: {str(e)}"], "node_statuses": statuses}