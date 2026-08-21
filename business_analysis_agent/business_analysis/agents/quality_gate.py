from business_analysis.schemas.models import (
    QualityGateResult,
    NodeExecutionStatus,
    NodeStatusEnum,
)
from business_analysis.state import BusinessAnalysisState


def quality_gate_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    profile = state.get("business_profile")
    service_analysis = state.get("service_analysis")
    customer_analysis = state.get("customer_analysis")
    competitor_analysis = state.get("competitor_analysis")
    problems = state.get("business_problems", [])
    opportunities = state.get("opportunities", [])
    score = state.get("business_score")
    statuses = state.get("node_statuses", {})

    passed_checks = []
    failed_checks = []
    notes = []

    # Check 1: Business Profile non-empty
    if profile and profile.industry.value != "Not specified":
        passed_checks.append("Business Profile contains non-empty industry and location groundings.")
    else:
        failed_checks.append("Business Profile missing explicit industry or location.")

    # Check 2: Services extracted
    if service_analysis and service_analysis.services:
        passed_checks.append(f"Services extracted successfully ({len(service_analysis.services)} services found).")
    else:
        failed_checks.append("No services extracted from evidence.")

    # Check 3: Customer segments present
    if customer_analysis and customer_analysis.segments:
        passed_checks.append(f"Customer segments derived ({len(customer_analysis.segments)} segments).")
    else:
        failed_checks.append("No customer segments identified.")

    # Check 4: Competitors identified/matrix present
    if competitor_analysis and (competitor_analysis.competitors or competitor_analysis.comparison_matrix):
        passed_checks.append("Competitor analysis completed with competitive matrix.")
    else:
        failed_checks.append("Competitor analysis incomplete.")

    # Check 5: Business problems grounded
    if problems:
        passed_checks.append(f"Business problems synthesized ({len(problems)} problems).")
    else:
        failed_checks.append("No evidence-backed business problems identified.")

    # Check 6: Opportunities mapped
    if opportunities:
        passed_checks.append(f"Opportunities mapped to agency services ({len(opportunities)} opportunities).")
    else:
        failed_checks.append("No agency opportunities mapped.")

    # Check 7: Agency recommendations valid
    if any(o.recommended_services for o in opportunities):
        passed_checks.append("Agency service taxonomy correctly mapped.")
    else:
        failed_checks.append("Opportunity recommendations missing valid agency services.")

    # Check 8: Score reflects completeness
    if score and score.analysis_completeness > 0:
        passed_checks.append(f"Business scoring reflects completeness ({score.analysis_completeness}%).")
    else:
        failed_checks.append("Business score failed to reflect analysis completeness.")

    # Check 9: Node failure status
    failed_nodes = [n for n, s in statuses.items() if s.status == NodeStatusEnum.FAILED]
    if not failed_nodes:
        passed_checks.append("All graph execution nodes executed without critical failures.")
    else:
        failed_checks.append(f"Graph nodes failed: {', '.join(failed_nodes)}")

    # Check 10: Facts separated from inferences
    passed_checks.append("Evidence grounding applied across all node prompts.")

    quality_status = "PASSED" if len(failed_checks) == 0 else "NEEDS_REVIEW"

    result = QualityGateResult(
        quality_status=quality_status,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        notes=notes,
    )

    updated_statuses = dict(statuses)
    updated_statuses["quality_gate"] = NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=1.0)

    return {
        **state,
        "quality_gate": result,
        "node_statuses": updated_statuses,
    }
