from typing import List
from business_analysis.schemas.models import (
    BusinessProfile,
    BusinessType,
    BusinessModel,
    CompanyScale,
    FieldStatus,
    FieldStatusEnum,
    NodeExecutionStatus,
    NodeStatusEnum,
)
from business_analysis.llm import get_structured_llm
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence


BUSINESS_PROFILE_PROMPT = """ROLE: You are an expert Business Intelligence Analyst.
OBJECTIVE: Analyze the provided evidence to extract a detailed, accurate Business Profile.

AVAILABLE EVIDENCE:
{evidence}

RULES:
1. Extract values strictly grounded in the evidence provided.
2. For EVERY field, classify status as:
   - KNOWN: Explicitly stated in the evidence.
   - INFERRED: Logically derived from explicit facts.
   - UNKNOWN: Insufficient evidence available (set value to "Not specified").
3. Do NOT leave fields empty or generic if evidence exists.
4. Extract specializations (e.g. "Dental Anxiety Treatment", "Complex Case Management") into specializations list.
5. Reference evidence IDs for every extracted field.

Determine:
- business_name (FieldStatus with value, status KNOWN/INFERRED/UNKNOWN, confidence 0.0-1.0, evidence_ids)
- official_name (FieldStatus)
- business_type (FieldStatus with value from: local_service, ecommerce, saas, b2b_service, restaurant, retail, healthcare, professional_services, manufacturing, other)
- business_model (FieldStatus with value from: b2c, b2b, b2b2c, marketplace, subscription, transactional, hybrid)
- industry (FieldStatus, e.g. "Dental Services" / "Healthcare")
- sub_industry (FieldStatus, e.g. "Specialist Dentistry")
- geographic_market (FieldStatus, e.g. "Amsterdam, Netherlands")
- primary_location (FieldStatus)
- service_area (FieldStatus)
- primary_offerings (FieldStatus with list of strings)
- secondary_offerings (FieldStatus with list of strings)
- positioning (FieldStatus)
- value_proposition (FieldStatus)
- target_market (FieldStatus)
- company_scale (FieldStatus with value from: solo, small, medium, large, enterprise, unknown)
- business_age (FieldStatus)
- specializations (FieldStatus with list of strings)
"""


def business_profile_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "business")
    evidence_text = "\n".join([
        f"[{e.id}] Claim: {e.claim} | Supporting Text: {e.supporting_text or 'N/A'} (Source: {e.source}, Confidence: {e.confidence})"
        for e in relevant_evidence
    ])

    prompt = BUSINESS_PROFILE_PROMPT.format(evidence=evidence_text)
    statuses = dict(state.get("node_statuses", {}))

    try:
        llm = get_structured_llm(BusinessProfile)
        profile = llm.invoke(prompt)
        profile.evidence_ids = [e.id for e in relevant_evidence]

        # Post-process fallback if industry or location missing from initial user input
        input_biz = state["input_business"]
        if profile.industry.status == FieldStatusEnum.UNKNOWN and input_biz.industry:
            profile.industry = FieldStatus(value=input_biz.industry, status=FieldStatusEnum.KNOWN, confidence=1.0, evidence_ids=[relevant_evidence[0].id if relevant_evidence else "fact_001"])
        if profile.geographic_market.status == FieldStatusEnum.UNKNOWN and input_biz.location:
            profile.geographic_market = FieldStatus(value=input_biz.location, status=FieldStatusEnum.KNOWN, confidence=1.0, evidence_ids=[relevant_evidence[0].id if relevant_evidence else "fact_001"])

        statuses["business_profile"] = NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=0.95)
        return {**state, "business_profile": profile, "node_statuses": statuses}
    except Exception as e:
        statuses["business_profile"] = NodeExecutionStatus(status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e))
        return {**state, "errors": state.get("errors", []) + [f"BusinessProfileAgent error: {str(e)}"], "node_statuses": statuses}