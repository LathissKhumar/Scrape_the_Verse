from business_analysis.llm import get_structured_llm
from business_analysis.schemas.models import (
    MarketAnalysis,
    NodeExecutionStatus,
    NodeStatusEnum,
    SearchIntentCategory,
    SearchIntentOpportunity,
)
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence

MARKET_ANALYSIS_PROMPT = """ROLE: You are an expert Local Market & Search Intelligence Analyst.
OBJECTIVE: Analyze the digital acquisition environment, local market conditions, search discovery intent, and digital opportunities.

AVAILABLE EVIDENCE:
{evidence}

BUSINESS CONTEXT:
Industry: {industry}
Location: {location}
Services: {services}

RULES:
1. Do NOT generate generic industry essays or hallucinate verified statistics if unavailable.
2. If exact market statistics are not in evidence, state: "Verified market statistics unavailable."
3. Distinguish:
   - OBSERVED MARKET FACT: Explicitly grounded in evidence.
   - INFERENCE: Derived search behavior and digital adoption dynamics.
   - OPPORTUNITY: Actionable acquisition potential.
4. Extract search intent opportunities across categories:
   - BRANDED (e.g. "{company_name}")
   - LOCAL (e.g. "dentist amsterdam", "dental clinic amsterdam")
   - SERVICE (e.g. "specialist dentist amsterdam")
   - PROBLEM (e.g. "dental anxiety dentist amsterdam", "teeth phobia care amsterdam")
"""


def market_analysis_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "market")
    evidence_text = "\n".join(
        [
            f"[{e.id}] Claim: {e.claim} | Supporting Text: {e.supporting_text or 'N/A'}"
            for e in relevant_evidence
        ]
    )

    profile = state.get("business_profile")
    service_analysis = state.get("service_analysis")
    company_name = state["input_business"].company_name

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
    services_val = (
        ", ".join([s.name for s in service_analysis.services])
        if service_analysis and service_analysis.services
        else "Dental Services"
    )

    prompt = MARKET_ANALYSIS_PROMPT.format(
        evidence=evidence_text,
        company_name=company_name,
        industry=industry_val,
        location=location_val,
        services=services_val,
    )

    statuses = dict(state.get("node_statuses", {}))

    try:
        llm = get_structured_llm(MarketAnalysis)
        analysis = llm.invoke(prompt)
        analysis.evidence_ids = [e.id for e in relevant_evidence]
        analysis.industry = industry_val
        analysis.local_market = location_val

        # Ensure search intent opportunities populated
        if not analysis.search_intent_opportunities:
            analysis.search_intent_opportunities = [
                SearchIntentOpportunity(
                    search_intent=SearchIntentCategory.BRANDED,
                    query_theme=f"{company_name}",
                    business_service="Brand discovery",
                    customer_need="Existing patient lookup or brand verification",
                    priority=8,
                ),
                SearchIntentOpportunity(
                    search_intent=SearchIntentCategory.LOCAL,
                    query_theme=f"dentist {location_val}",
                    business_service="General dentistry",
                    customer_need="Local dental care provider search",
                    priority=7,
                ),
                SearchIntentOpportunity(
                    search_intent=SearchIntentCategory.PROBLEM,
                    query_theme=f"dental anxiety dentist {location_val}",
                    business_service="Dental Anxiety Treatment",
                    customer_need="Specialized gentle dental care for phobia",
                    priority=9,
                ),
            ]

        statuses["market_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.88
        )
        return {**state, "market_analysis": analysis, "node_statuses": statuses}
    except Exception as e:
        statuses["market_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e)
        )
        return {
            **state,
            "errors": state.get("errors", []) + [f"MarketAnalysisAgent error: {e!s}"],
            "node_statuses": statuses,
        }
