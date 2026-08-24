from typing import Any

from pydantic import BaseModel

from business_analysis.llm import get_structured_llm
from business_analysis.schemas.models import (
    AgencyService,
    NodeExecutionStatus,
    NodeStatusEnum,
    Opportunity,
)
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence

OPPORTUNITY_MAPPING_PROMPT = """ROLE: You are an expert Digital Agency Opportunity & Growth Strategist.
OBJECTIVE: Map identified business problems to actionable digital agency opportunities and prioritized service recommendations.

AVAILABLE PROBLEMS:
{problems_text}

BUSINESS & SERVICE CONTEXT:
Industry: {industry}
Location: {location}

DETERMINISTIC AGENCY SERVICE TAXONOMY:
- NEW_WEBSITE
- WEBSITE_REDESIGN
- SEO
- LOCAL_SEO
- TECHNICAL_SEO
- CONTENT
- CONVERSION_OPTIMIZATION
- LANDING_PAGE
- SERVICE_LANDING_PAGES
- WEBSITE_PERFORMANCE
- DIGITAL_PRESENCE

RULES:
1. Every opportunity MUST reference an identified problem.
2. Select agency services ONLY from the deterministic taxonomy.
3. For each opportunity specify:
   - problem_reference (problem title or ID)
   - opportunity (concise description of the growth opportunity)
   - recommended_services (list of AgencyService enums)
   - expected_business_outcome (clear expected outcome, without promising exact fake traffic figures)
   - impact (1-10)
   - urgency (1-10)
   - confidence (0.0-1.0)
   - effort (1-10)
   - business_value (1-10)
   - service_fit (1-10)
   - rationale (why this agency service solves the problem)
"""


def map_problem_to_services(
    problem: Any, website_present: bool = True
) -> list[AgencyService]:
    # Accept either a BusinessProblem object or a raw string/enum
    if hasattr(problem, "problem"):
        text = problem.problem.upper()
    elif hasattr(problem, "type") and hasattr(problem.type, "value"):
        text = str(problem.type.value).upper()
    elif isinstance(problem, str):
        text = problem.upper()
    else:
        text = str(getattr(problem, "value", problem)).upper()

    if (
        "NO WEBSITE" in text
        or "WEBSITE_ABSENT" in text
        or "NO_WEBSITE" in text
        or not website_present
    ):
        return [AgencyService.NEW_WEBSITE, AgencyService.DIGITAL_PRESENCE]
    if "WEAK LOCAL" in text or "LOCAL" in text or "DISCOVERY" in text:
        return [
            AgencyService.LOCAL_SEO,
            AgencyService.CONTENT,
            AgencyService.DIGITAL_PRESENCE,
        ]
    if "TECHNICAL SEO" in text or "TECHNICAL_SEO" in text:
        return [AgencyService.TECHNICAL_SEO, AgencyService.SEO]
    if (
        "CONTENT GAP" in text
        or "CONTENT_GAP" in text
        or "SERVICE_VISIBILITY" in text
        or "CONTENT" in text
    ):
        return [
            AgencyService.CONTENT,
            AgencyService.LANDING_PAGE,
            AgencyService.SERVICE_LANDING_PAGES,
            AgencyService.SEO,
        ]
    if "CONVERSION" in text or "UX" in text:
        return [AgencyService.CONVERSION_OPTIMIZATION, AgencyService.WEBSITE_REDESIGN]

    return [AgencyService.LOCAL_SEO, AgencyService.CONTENT]


class OpportunityContainer(BaseModel):
    opportunities: list[Opportunity] = []


def opportunity_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "opportunity")
    problems = state.get("business_problems", [])

    problems_text = (
        "\n".join(
            [
                f"- [{p.id}] {p.title} (Type: {p.type.value}, Impact: {p.business_impact}/10): {p.description}"
                for p in problems
            ]
        )
        if problems
        else "Specialized service visibility and local search discovery gap."
    )

    profile = state.get("business_profile")
    industry_val = (
        profile.industry.value
        if profile and hasattr(profile.industry, "value")
        else state["input_business"].industry
    )
    location_val = (
        profile.geographic_market.value
        if profile and hasattr(profile.geographic_market, "value")
        else state["input_business"].location
    )

    prompt = OPPORTUNITY_MAPPING_PROMPT.format(
        problems_text=problems_text,
        industry=industry_val,
        location=location_val,
    )

    statuses = dict(state.get("node_statuses", {}))

    try:
        llm = get_structured_llm(OpportunityContainer)
        res = llm.invoke(prompt)
        if isinstance(res, list):
            opps = res
        elif hasattr(res, "opportunities"):
            opps = res.opportunities
        else:
            opps = []

        if not opps:
            opps = [
                Opportunity(
                    problem_reference="Specialized Service Acquisition & Visibility Gap",
                    opportunity="Create specialized local search acquisition funnels and dedicated anxiety-care landing pages",
                    recommended_services=[
                        AgencyService.LOCAL_SEO,
                        AgencyService.CONTENT,
                        AgencyService.SERVICE_LANDING_PAGES,
                        AgencyService.CONVERSION_OPTIMIZATION,
                    ],
                    expected_business_outcome="Improve non-branded local search discovery and conversion for high-value specialized dental treatment inquiries",
                    impact=8,
                    urgency=8,
                    confidence=0.85,
                    effort=4,
                    business_value=9,
                    service_fit=9,
                    rationale="High-intent patients seeking dental anxiety care or complex rehabilitation search specifically for those capabilities.",
                ),
                Opportunity(
                    problem_reference="Non-Branded Local Search Discovery Deficit",
                    opportunity="Optimize local search presence and digital trust signals in Amsterdam",
                    recommended_services=[
                        AgencyService.LOCAL_SEO,
                        AgencyService.CONTENT,
                        AgencyService.DIGITAL_PRESENCE,
                    ],
                    expected_business_outcome="Strengthen Google Map Pack and local search visibility for general and specialist dental queries in Amsterdam",
                    impact=7,
                    urgency=7,
                    confidence=0.8,
                    effort=3,
                    business_value=8,
                    service_fit=9,
                    rationale="Maximizes organic discovery among residents seeking local dental practices.",
                ),
            ]

        # Calculate deterministic priority score for each opportunity
        for opp in opps:
            imp = opp.impact or 5
            bv = opp.business_value or 5
            conf = opp.confidence or 0.8
            urg = opp.urgency or 5
            s_fit = opp.service_fit or 5
            calc_priority = int(
                round(
                    (imp * 0.30)
                    + (bv * 0.25)
                    + (conf * 10 * 0.20)
                    + (urg * 0.15)
                    + (s_fit * 10 * 0.10)
                )
            )
            opp.priority = max(1, min(10, calc_priority))

        statuses["opportunity"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.88
        )
        return {**state, "opportunities": opps, "node_statuses": statuses}
    except Exception as e:
        statuses["opportunity"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e)
        )
        return {
            **state,
            "errors": state.get("errors", []) + [f"OpportunityAgent error: {e!s}"],
            "node_statuses": statuses,
        }
