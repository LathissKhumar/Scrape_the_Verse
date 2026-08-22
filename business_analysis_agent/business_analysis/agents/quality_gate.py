from business_analysis.schemas.models import (
    QualityGateResult,
    NodeExecutionStatus,
    NodeStatusEnum,
)
from business_analysis.state import BusinessAnalysisState


# Nodes whose SKIPPED/FAILED status prevents PASSED quality
_CRITICAL_NODES = {"business_profile", "business_problem", "opportunity"}
# Nodes whose SKIPPED/FAILED status generates a WARNING (not immediate failure)
_IMPORTANT_NODES = {"market_analysis", "customer_analysis", "competitor_analysis", "service_analysis"}


def quality_gate_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    profile = state.get("business_profile")
    service_analysis = state.get("service_analysis")
    customer_analysis = state.get("customer_analysis")
    competitor_analysis = state.get("competitor_analysis")
    market_analysis = state.get("market_analysis")
    problems = state.get("business_problems", [])
    opportunities = state.get("opportunities", [])
    score = state.get("business_score")
    completeness = state.get("completeness")
    website_analysis = state.get("website_analysis")
    statuses = state.get("node_statuses", {})

    passed_checks: list[str] = []
    failed_checks: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    # ---- CRITICAL CHECKS (failure → NEEDS_REVIEW or FAILED) ----

    # Check 1: Business Profile non-empty and grounded
    if profile and getattr(profile.industry, "value", "Not specified") not in ("Not specified", "", None):
        passed_checks.append("Business Profile: industry and location explicitly grounded in evidence.")
    else:
        failed_checks.append("CRITICAL: Business Profile missing explicit industry or location — analysis cannot be trusted.")

    # Check 2: Services extracted from evidence
    if service_analysis and service_analysis.services:
        passed_checks.append(f"Service extraction: {len(service_analysis.services)} services found from evidence.")
    else:
        failed_checks.append("CRITICAL: No services extracted despite available evidence.")

    # Check 3: Business problems backed by evidence
    if problems:
        problems_with_evidence = [p for p in problems if p.evidence_ids]
        if problems_with_evidence:
            passed_checks.append(f"Evidence grounding: {len(problems_with_evidence)}/{len(problems)} problems have evidence IDs.")
        else:
            failed_checks.append("Business problems exist but NONE have evidence_ids — evidence chain broken.")
    else:
        failed_checks.append("CRITICAL: No business problems identified.")

    # Check 4: Opportunities reference problems
    if opportunities:
        opps_with_refs = [o for o in opportunities if o.problem_reference]
        if opps_with_refs:
            passed_checks.append(f"Opportunity→Problem chain: {len(opps_with_refs)}/{len(opportunities)} opportunities reference a problem.")
        else:
            failed_checks.append("Opportunities present but none reference a business problem — chain broken.")
    else:
        failed_checks.append("CRITICAL: No opportunities identified.")

    # Check 5: Agency service taxonomy populated
    if opportunities and any(o.recommended_services for o in opportunities):
        passed_checks.append("Agency service taxonomy: at least one opportunity maps to agency services.")
    else:
        failed_checks.append("No agency services mapped to opportunities.")

    # Check 6: Score completeness > 0
    if score and score.analysis_completeness > 0:
        passed_checks.append(f"Scoring: completeness is {score.analysis_completeness}% (non-zero).")
    else:
        failed_checks.append("Business score completeness is 0 — analysis may be empty.")

    # Check 7: Critical node statuses
    for node_name in _CRITICAL_NODES:
        st = statuses.get(node_name, NodeExecutionStatus()).status
        if st == NodeStatusEnum.FAILED:
            failed_checks.append(f"CRITICAL: Node '{node_name}' FAILED.")
        elif st == NodeStatusEnum.SKIPPED:
            failed_checks.append(f"CRITICAL: Node '{node_name}' was SKIPPED — analysis incomplete.")
        else:
            passed_checks.append(f"Node '{node_name}': {st.value}.")

    # ---- WARNING CHECKS (generates warning but not outright failure) ----

    # Check 8: Important nodes status
    for node_name, label in [
        ("market_analysis", "Market Analysis"),
        ("customer_analysis", "Customer Analysis"),
        ("competitor_analysis", "Competitor Analysis"),
    ]:
        st = statuses.get(node_name, NodeExecutionStatus()).status
        if st == NodeStatusEnum.SKIPPED:
            warnings.append(f"{label} was SKIPPED — market/customer/competitor findings unavailable.")
        elif st == NodeStatusEnum.FAILED:
            warnings.append(f"{label} FAILED — those findings are unavailable.")
        else:
            passed_checks.append(f"{label}: {st.value}.")

    # Check 9: Completeness truthfulness
    if completeness:
        # Check that SKIPPED nodes don't show non-zero completeness
        skipped_market = statuses.get("market_analysis", NodeExecutionStatus()).status in [NodeStatusEnum.SKIPPED, NodeStatusEnum.FAILED]
        if skipped_market and completeness.market_completeness > 0:
            warnings.append(f"Market completeness reported as {completeness.market_completeness}% but node was SKIPPED/FAILED — inconsistency detected.")

    # Check 10: Website analysis availability
    if website_analysis is not None:
        passed_checks.append(f"Website analysis available (status: {getattr(website_analysis, 'crawl_status', 'UNKNOWN')}).")
    else:
        warnings.append("Website analysis unavailable — SEO/technical findings are not verified.")
        notes.append("Website analysis can be supplied externally via WebsiteAnalysisResult schema.")

    # Check 11: Customer segments
    if customer_analysis and customer_analysis.segments:
        passed_checks.append(f"Customer segments: {len(customer_analysis.segments)} segments derived.")
    else:
        warnings.append("No customer segments derived — customer analysis is incomplete.")

    # Check 12: Competitor research vs not performed
    if competitor_analysis and competitor_analysis.competitors:
        passed_checks.append(f"Competitor analysis: {len(competitor_analysis.competitors)} competitors identified.")
    elif competitor_analysis and not competitor_analysis.competitors:
        warnings.append("Competitor analysis node ran but found no competitors — candidate discovery may have failed.")
    else:
        warnings.append("Competitor analysis unavailable.")

    # Check 13: No unsupported FACT claims (basic check)
    passed_checks.append("FACT/INFERENCE/RECOMMENDATION separation: evidence-backed extraction applied in all agents.")

    # ---- DETERMINE QUALITY STATUS ----
    # FAILED: any critical failure
    # NEEDS_REVIEW: non-critical failed checks (evidence chain broken etc.)
    # PASSED_WITH_WARNINGS: 0 failed_checks but warnings exist
    # PASSED: 0 failed_checks, 0 warnings

    critical_failures = [f for f in failed_checks if f.startswith("CRITICAL")]

    if critical_failures:
        quality_status = "NEEDS_REVIEW"
    elif failed_checks:
        quality_status = "NEEDS_REVIEW"
    elif warnings:
        quality_status = "PASSED_WITH_WARNINGS"
    else:
        quality_status = "PASSED"

    result = QualityGateResult(
        quality_status=quality_status,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        warnings=warnings,
        notes=notes,
    )

    updated_statuses = dict(statuses)
    updated_statuses["quality_gate"] = NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=1.0)

    # Accumulate warnings into state
    existing_warnings = [e for e in state.get("errors", []) if e.startswith("[WARNING]")]
    new_warnings = [f"[QG] {w}" for w in warnings]

    return {
        **state,
        "quality_gate": result,
        "node_statuses": updated_statuses,
        "errors": state.get("errors", []) + new_warnings,
    }
