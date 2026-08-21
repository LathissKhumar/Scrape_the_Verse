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
    score = 65
    if service and getattr(service, "key_gaps", None):
        score += 15
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



def business_scoring_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    statuses = state.get("node_statuses", {})
    problems = state.get("business_problems", [])
    opportunities = state.get("opportunities", [])
    profile = state.get("business_profile")
    market = state.get("market_analysis")
    customer = state.get("customer_analysis")
    competitor = state.get("competitor_analysis")
    service = state.get("service_analysis")

    # Compute node completeness metrics
    nodes = ["business_profile", "market_analysis", "customer_analysis", "competitor_analysis", "service_analysis", "business_problem", "opportunity"]
    successful_nodes = sum(1 for n in nodes if statuses.get(n, NodeExecutionStatus()).status == NodeStatusEnum.SUCCESS)
    overall_completeness = round((successful_nodes / len(nodes)) * 100, 1)

    completeness = AnalysisCompleteness(
        profile_completeness=100.0 if profile else 0.0,
        market_completeness=100.0 if market else 0.0,
        customer_completeness=100.0 if customer else 0.0,
        competitor_completeness=100.0 if competitor else 0.0,
        service_completeness=100.0 if service else 0.0,
        problem_completeness=100.0 if problems else 0.0,
        opportunity_completeness=100.0 if opportunities else 0.0,
        overall_analysis_completeness=overall_completeness,
    )

    fit = calculate_business_fit(profile)
    need = calculate_digital_need(problems)
    opp_val = 85 if opportunities else 40

    ev_list = state.get("evidence", [])
    conf_avg = (sum(e.confidence for e in ev_list) / len(ev_list)) * 100 if ev_list else 50.0
    confidence = int(round(conf_avg))
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

    has_critical_failure = (
        statuses.get("business_problem", NodeExecutionStatus()).status == NodeStatusEnum.FAILED or
        statuses.get("opportunity", NodeExecutionStatus()).status == NodeStatusEnum.FAILED or
        not problems or not opportunities
    )

    if has_critical_failure and priority in [ScoreCategory.HIGH, ScoreCategory.VERY_HIGH]:
        priority = ScoreCategory.MEDIUM
        overall_score = min(overall_score, 60)

    score_explanation = {
        "business_fit": f"Business fit scored {fit}/100 based on industry alignment and clear service offerings.",
        "digital_need": f"Digital need scored {need}/100 reflecting identified service visibility and search discovery gaps.",
        "opportunity_value": f"Opportunity value scored {opp_val}/100 driven by specialized service acquisition potential.",
        "evidence_confidence": f"Evidence confidence average is {confidence}/100 across {len(ev_list)} evidence claims.",
        "serviceability": f"Serviceability scored {serviceability}/100 matching core agency offerings (Local SEO, Landing Pages, Content).",
        "completeness": f"Overall analysis completeness is {overall_completeness}% across graph nodes."
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

    return {
        **state,
        "business_score": score_obj,
        "completeness": completeness,
        "node_statuses": updated_statuses,
    }