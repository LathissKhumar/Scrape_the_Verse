from typing import List, Any
from business_analysis.schemas.models import (
    BusinessScore,
    ScoreCategory,
    NodeExecutionStatus,
    NodeStatusEnum,
    AnalysisCompleteness,
)
from business_analysis.llm import get_structured_llm
from business_analysis.state import BusinessAnalysisState


def calculate_business_fit(profile: Any = None, market: Any = None, competitor: Any = None) -> int:
    if not profile:
        return 50
    ind = getattr(profile, "industry", None)
    if not ind or ind == "Not specified" or getattr(ind, "status", None) == "UNKNOWN" or getattr(ind, "value", None) == "Not specified":
        return 50
    score = 85
    if competitor and getattr(competitor, "competitors", None):
        score += 5
    return min(100, score)


def calculate_digital_need(profile: Any = None, market: Any = None, service: Any = None, competitor: Any = None) -> int:
    """Calculate digital need from service gaps and competitor pressure."""
    score = 60
    if service and getattr(service, "key_gaps", None):
        score += min(20, len(service.key_gaps) * 5)
    if service and getattr(service, "services", None):
        low_vis = sum(1 for s in service.services if getattr(s, "visibility", None) and s.visibility.value in ["low", "none"])
        score += min(10, low_vis * 5)
    if competitor and getattr(competitor, "identified_gaps", None):
        score += 5
    return min(100, score)


def calculate_opportunity_value(opportunities: Any = None, problems: Any = None) -> int:
    return 85 if (opportunities or problems) else 40


def calculate_evidence_confidence(evidence: Any = None, problems: Any = None) -> int:
    if not evidence:
        return 50
    return int(round((sum(getattr(e, "confidence", 0.5) for e in evidence) / len(evidence)) * 100))


def calculate_serviceability(profile: Any = None, opportunities: Any = None) -> int:
    return 90


def calculate_overall_score(fit: int, need: int, opp_val: int, confidence: int, serviceability: int, completeness: int = 100) -> int:
    return int(round(
        (fit * 0.20) +
        (need * 0.20) +
        (opp_val * 0.20) +
        (confidence * 0.15) +
        (serviceability * 0.10) +
        (completeness * 0.15)
    ))


def _node_completeness(statuses: dict, node_name: str, output_obj: Any) -> float:
    """
    Derive completeness score for a single node.
    SKIPPED → 0, FAILED → 0, PARTIAL → 50, SUCCESS → quality-based (60-100).
    """
    status = statuses.get(node_name, NodeExecutionStatus())
    st = status.status

    if st == NodeStatusEnum.SKIPPED:
        return 0.0
    if st == NodeStatusEnum.FAILED:
        return 0.0
    if st == NodeStatusEnum.PARTIAL:
        return 50.0
    # SUCCESS — quality-based
    if output_obj is None:
        return 0.0
    return min(100.0, 60.0 + (status.confidence * 40.0))


def business_scoring_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    statuses = state.get("node_statuses", {})
    problems = state.get("business_problems", [])
    opportunities = state.get("opportunities", [])
    profile = state.get("business_profile")
    market = state.get("market_analysis")
    customer = state.get("customer_analysis")
    competitor = state.get("competitor_analysis")
    service = state.get("service_analysis")

    # -- Derive per-node completeness from actual NodeExecutionStatus --
    profile_comp = _node_completeness(statuses, "business_profile", profile)
    market_comp = _node_completeness(statuses, "market_analysis", market)
    customer_comp = _node_completeness(statuses, "customer_analysis", customer)
    competitor_comp = _node_completeness(statuses, "competitor_analysis", competitor)
    service_comp = _node_completeness(statuses, "service_analysis", service)
    problem_comp = _node_completeness(statuses, "business_problem", problems or None)
    opportunity_comp = _node_completeness(statuses, "opportunity", opportunities or None)

    overall_completeness = round(
        (profile_comp + market_comp + customer_comp + competitor_comp +
         service_comp + problem_comp + opportunity_comp) / 7.0, 1
    )

    completeness = AnalysisCompleteness(
        profile_completeness=profile_comp,
        market_completeness=market_comp,
        customer_completeness=customer_comp,
        competitor_completeness=competitor_comp,
        service_completeness=service_comp,
        problem_completeness=problem_comp,
        opportunity_completeness=opportunity_comp,
        overall_analysis_completeness=overall_completeness,
    )

    ev_list = state.get("evidence", [])
    fit = calculate_business_fit(profile, market, competitor)
    need = calculate_digital_need(profile, market, service, competitor)
    opp_val = 85 if opportunities else 40
    confidence = calculate_evidence_confidence(ev_list)
    serviceability = 90
    comp_score = int(round(overall_completeness))

    overall_score = calculate_overall_score(fit, need, opp_val, confidence, serviceability, comp_score)

    if overall_score >= 80:
        priority = ScoreCategory.VERY_HIGH
    elif overall_score >= 65:
        priority = ScoreCategory.HIGH
    elif overall_score >= 50:
        priority = ScoreCategory.MEDIUM
    else:
        priority = ScoreCategory.LOW

    # Enforce penalty if critical agents failed
    has_critical_failure = (
        statuses.get("business_problem", NodeExecutionStatus()).status == NodeStatusEnum.FAILED or
        statuses.get("opportunity", NodeExecutionStatus()).status == NodeStatusEnum.FAILED or
        not problems or not opportunities
    )

    if has_critical_failure and priority in [ScoreCategory.HIGH, ScoreCategory.VERY_HIGH]:
        priority = ScoreCategory.MEDIUM
        overall_score = min(overall_score, 60)

    # Collect warnings for SKIPPED nodes
    skipped_warnings = []
    for node_name, label in [
        ("market_analysis", "Market analysis"),
        ("customer_analysis", "Customer analysis"),
        ("competitor_analysis", "Competitor analysis"),
    ]:
        st = statuses.get(node_name, NodeExecutionStatus()).status
        if st == NodeStatusEnum.SKIPPED:
            skipped_warnings.append(f"{label} was SKIPPED — completeness reduced.")
        elif st == NodeStatusEnum.FAILED:
            skipped_warnings.append(f"{label} FAILED — analysis is incomplete.")

    score_explanation = {
        "business_fit": f"Business fit scored {fit}/100 based on industry alignment and clear service offerings.",
        "digital_need": f"Digital need scored {need}/100 reflecting service visibility gaps and search discovery.",
        "opportunity_value": f"Opportunity value scored {opp_val}/100 driven by specialized service acquisition potential.",
        "evidence_confidence": f"Evidence confidence average is {confidence}/100 across {len(ev_list)} evidence claims.",
        "serviceability": f"Serviceability scored {serviceability}/100 matching core agency offerings.",
        "completeness": f"Analysis completeness is {overall_completeness}% (P:{profile_comp:.0f} M:{market_comp:.0f} C:{customer_comp:.0f} Co:{competitor_comp:.0f} S:{service_comp:.0f} Pr:{problem_comp:.0f} O:{opportunity_comp:.0f}).",
    }

    score_obj = BusinessScore(
        business_fit=fit,
        digital_need=need,
        opportunity_value=opp_val,
        evidence_confidence=confidence,
        serviceability=serviceability,
        analysis_completeness=comp_score,
        overall_score=overall_score,
        priority=priority,
        score_explanation=score_explanation,
    )

    updated_statuses = dict(statuses)
    updated_statuses["business_scoring"] = NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=1.0)

    result = {
        **state,
        "business_score": score_obj,
        "completeness": completeness,
        "node_statuses": updated_statuses,
    }
    if skipped_warnings:
        result["errors"] = state.get("errors", []) + [f"[WARNING] {w}" for w in skipped_warnings]
    return result