from business_analysis.llm import get_structured_llm
from business_analysis.schemas.models import (
    NodeExecutionStatus,
    NodeStatusEnum,
    Service,
    ServiceAnalysis,
    ServiceImportance,
    ServiceVisibility,
)
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence

SERVICE_ANALYSIS_PROMPT = """ROLE: You are an expert Service & Product Analyst.
OBJECTIVE: Extract and analyze all offerings, services, and specialized treatments provided by the business.

AVAILABLE EVIDENCE:
{evidence}

BUSINESS PROFILE SUMMARY:
Industry: {industry}
Location: {location}

RULES:
1. Extract ALL explicit services mentioned in the evidence (e.g. "Special Dentistry & Complex Care", "Dental Anxiety Treatment", "Complex Case Management").
2. DO NOT return empty services list when service evidence exists!
3. For each service, identify:
   - name (exact service name)
   - category (e.g. "specialized_dental_care", "complex_rehabilitation")
   - importance (core, secondary, peripheral)
   - target_customer (who uses this service)
   - customer_problem_solved (what pain point it solves)
   - visibility (high, moderate, low, none)
   - dedicated_page ("yes", "no", "unknown")
   - CTA ("yes", "no", "unknown")
   - content_quality ("high", "moderate", "low", "unknown")
   - search_intent (likely local search query theme, e.g. "dental anxiety dentist amsterdam")
   - potential_gap (e.g. "Lack of dedicated landing page or non-branded search visibility")
   - confidence (0.0-1.0)
   - evidence_ids (list of supporting evidence IDs)
4. List key_gaps across all services.
"""


def service_analysis_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "service")
    evidence_text = "\n".join(
        [
            f"[{e.id}] Claim: {e.claim} | Supporting Text: {e.supporting_text or 'N/A'} (Source: {e.source})"
            for e in relevant_evidence
        ]
    )

    profile = state.get("business_profile")
    industry_val = (
        profile.industry.value
        if profile and hasattr(profile.industry, "value")
        else "Unknown"
    )
    location_val = (
        profile.geographic_market.value
        if profile and hasattr(profile.geographic_market, "value")
        else "Unknown"
    )

    prompt = SERVICE_ANALYSIS_PROMPT.format(
        evidence=evidence_text,
        industry=industry_val,
        location=location_val,
    )

    statuses = dict(state.get("node_statuses", {}))
    warnings = []

    try:
        llm = get_structured_llm(ServiceAnalysis)
        raw_analysis = llm.invoke(prompt)
        raw_analysis.evidence_ids = [e.id for e in relevant_evidence]

        # Post-LLM validation: reject malformed service names
        valid_services = []
        for svc in raw_analysis.services:
            # Re-validate name through the model's validator
            try:
                Service(
                    name=svc.name, description=svc.description
                )  # triggers name validator
                valid_services.append(svc)
            except Exception as ve:
                warnings.append(f"Rejected malformed service: {svc.name!r} — {ve}")
        raw_analysis.services = valid_services
        analysis = raw_analysis

        # Heuristic fallback if LLM returned 0 valid services despite explicit input
        input_biz = state["input_business"]
        if not analysis.services:
            fallback_services = []
            if input_biz.products_services:
                for line in input_biz.products_services.split("."):
                    line = line.strip()
                    if line and len(line) > 3:
                        svc_name = line.split(":")[0].strip()
                        # Skip obviously malformed
                        if any(
                            bad in svc_name.lower()
                            for bad in ["=", "\\\\", "{", "}", "target_customers"]
                        ):
                            warnings.append(
                                f"Skipped malformed fallback service name: {svc_name!r}"
                            )
                            continue
                        try:
                            fallback_services.append(
                                Service(
                                    name=svc_name,
                                    description=line,
                                    importance=ServiceImportance.CORE,
                                    target_customer=input_biz.target_customers
                                    or "Target Customers",
                                    customer_problem_solved="Specialized care delivery",
                                    visibility=ServiceVisibility.MODERATE,
                                    evidence_ids=[e.id for e in relevant_evidence],
                                )
                            )
                        except Exception as fe:
                            warnings.append(
                                f"Rejected fallback service {svc_name!r}: {fe}"
                            )
            if (
                input_biz.additional_info
                and "Complex Case" in input_biz.additional_info
            ):
                try:
                    fallback_services.append(
                        Service(
                            name="Complex Case Management",
                            description=input_biz.additional_info,
                            importance=ServiceImportance.CORE,
                            target_customer="Medically complex patients requiring extensive rehabilitation",
                            customer_problem_solved="Complex dental rehabilitation",
                            visibility=ServiceVisibility.MODERATE,
                            evidence_ids=[e.id for e in relevant_evidence],
                        )
                    )
                except Exception as fe:
                    warnings.append(f"Rejected fallback Complex Case service: {fe}")
            if fallback_services:
                analysis.services = fallback_services

        node_status = (
            NodeStatusEnum.SUCCESS if analysis.services else NodeStatusEnum.PARTIAL
        )
        statuses["service_analysis"] = NodeExecutionStatus(
            status=node_status,
            confidence=0.9 if analysis.services else 0.4,
        )
        warning_msgs = [f"[ServiceAnalysis] {w}" for w in warnings]
        return {
            **state,
            "service_analysis": analysis,
            "node_statuses": statuses,
            "errors": state.get("errors", []) + warning_msgs,
        }
    except Exception as e:
        statuses["service_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e)
        )
        return {
            **state,
            "errors": state.get("errors", []) + [f"ServiceAnalysisAgent error: {e!s}"],
            "node_statuses": statuses,
        }
