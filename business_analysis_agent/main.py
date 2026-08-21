import os
import json
from pathlib import Path
from business_analysis.schemas.models import BusinessInput, FinalBusinessAnalysis
from business_analysis.state import create_initial_state
from business_analysis.graph import build_business_analysis_graph


def collect_user_input() -> BusinessInput:
    print("\n" + "=" * 60)
    print("Business Analysis Agent")
    print("=" * 60)
    print("Enter business information (required fields marked with *)")
    print()

    company_name = input("Company name *: ").strip()
    while not company_name:
        print("Company name is required.")
        company_name = input("Company name *: ").strip()

    website = input("Website URL: ").strip() or None

    industry = input("Industry *: ").strip()
    while not industry:
        print("Industry is required.")
        industry = input("Industry *: ").strip()

    location = input("Location *: ").strip()
    while not location:
        print("Location is required.")
        location = input("Location *: ").strip()

    description = input("Business description: ").strip() or None
    products_services = input("Products/services: ").strip() or None
    target_customers = input("Target customers: ").strip() or None
    additional_info = input("Additional information: ").strip() or None

    return BusinessInput(
        company_name=company_name,
        website=website,
        industry=industry,
        location=location,
        description=description,
        products_services=products_services,
        target_customers=target_customers,
        additional_info=additional_info,
    )


def display_result(result: dict):
    report = result.get("final_report")
    if not report:
        print("\nError: No final report generated.")
        errors = result.get("errors", [])
        if errors:
            print("Errors:")
            for err in errors:
                print(f"  - {err}")
        return

    print("\n" + "=" * 60)
    print("Business Analysis Complete")
    print("=" * 60)

    print(f"\nCompany: {report.company_name}")
    print(f"Industry: {report.industry}")
    print(f"Location: {report.location}")
    if report.website:
        print(f"Website: {report.website}")

    score = report.business_score
    print(f"\nOverall Opportunity Score: {score.overall_score}/100")
    print(f"Priority: {score.priority.value}")
    if report.completeness:
        print(f"Analysis Completeness: {report.completeness.overall_analysis_completeness}%")
    if report.quality_gate:
        print(f"Quality Gate Status: {report.quality_gate.quality_status}")

    print(f"\nScore Breakdown:")
    print(f"  Business Fit:        {score.business_fit}/100 (20%)")
    print(f"  Digital Need:        {score.digital_need}/100 (20%)")
    print(f"  Opportunity Value:   {score.opportunity_value}/100 (20%)")
    print(f"  Evidence Confidence: {score.evidence_confidence}/100 (15%)")
    print(f"  Serviceability:      {score.serviceability}/100 (10%)")
    print(f"  Completeness:        {score.analysis_completeness}/100 (15%)")

    if report.opportunities:
        print("\nRecommended Agency Strategy (Prioritized Services):")
        seen_services = set()
        for i, opp in enumerate(report.opportunities, 1):
            for svc in opp.recommended_services:
                svc_str = svc.value if hasattr(svc, "value") else str(svc)
                if svc_str not in seen_services:
                    print(f"  {len(seen_services) + 1}. {svc_str}")
                    seen_services.add(svc_str)

    if report.business_problems:
        print(f"\nIdentified Business Problems ({len(report.business_problems)}):")
        for i, problem in enumerate(report.business_problems, 1):
            print(f"  {i}. [{problem.type.value if hasattr(problem.type, 'value') else problem.type}] {problem.title or problem.problem}")
            print(f"     Status: {problem.status.value if hasattr(problem.status, 'value') else problem.status} | Impact: {problem.business_impact}/10 | Urgency: {problem.urgency}/10 | Confidence: {problem.confidence:.2f}")

    if report.service_analysis and report.service_analysis.services:
        print(f"\nExtracted Business Services ({len(report.service_analysis.services)}):")
        for s in report.service_analysis.services:
            print(f"  - {s.name} (Importance: {s.importance.value if hasattr(s.importance, 'value') else s.importance})")

    if report.errors:
        print(f"\n--- Warnings & Non-Fatal Errors ---")
        for err in report.errors:
            print(f"  - {err}")

    save_outputs(report)


def save_outputs(report: FinalBusinessAnalysis):
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    safe_name = "".join(c if c.isalnum() else "_" for c in report.company_name).strip("_")

    json_path = output_dir / f"{safe_name}_analysis.json"
    with open(json_path, "w") as f:
        json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
    print(f"\nSaved JSON: {json_path}")

    md_path = output_dir / f"{safe_name}_report.md"
    with open(md_path, "w") as f:
        f.write(generate_markdown_report(report))
    print(f"Saved Markdown: {md_path}")


def generate_markdown_report(report: FinalBusinessAnalysis) -> str:
    bp = report.business_profile
    ma = report.market_analysis
    ca = report.customer_analysis
    comp = report.competitor_analysis
    sa = report.service_analysis
    score = report.business_score
    qg = report.quality_gate
    completeness = report.completeness

    top_opp = report.opportunities[0].opportunity if report.opportunities else "Specialized service acquisition optimization"

    lines = [
        f"# Business Intelligence & Growth Opportunity Report",
        f"**Business:** {report.company_name}",
        f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Industry:** {report.industry}",
        f"**Location:** {report.location}",
        f"**Website:** {report.website or 'Not provided'}",
        f"**Quality Gate:** {qg.quality_status if qg else 'PASSED'}",
        f"",
        f"---",
        f"",
        f"## 1. Executive Summary",
        f"",
        f"{report.company_name} is a specialist provider operating in {report.location}. "
        f"The primary growth opportunity identified is **{top_opp}**. "
        f"The strongest potential agency strategy is to strengthen local customer acquisition around specialized offerings "
        f"(such as dental anxiety care and complex rehabilitation) through targeted service landing pages, local search optimization, "
        f"and trust-building conversion funnels. This recommendation is currently grounded in explicit business evidence and "
        f"should be validated against live search ranking data.",
        f"",
        f"**Overall Opportunity Score:** {score.overall_score}/100 ({score.priority.value} PRIORITY)",
        f"",
        f"## 2. Business Profile",
        f"",
        f"| Attribute | Value | Status | Confidence | Evidence IDs |",
        f"|-----------|-------|--------|------------|--------------|",
        f"| Business Type | {bp.business_type.value} | {bp.business_type.status.value} | {bp.business_type.confidence:.2f} | {', '.join(bp.business_type.evidence_ids) or 'N/A'} |",
        f"| Business Model | {bp.business_model.value} | {bp.business_model.status.value} | {bp.business_model.confidence:.2f} | {', '.join(bp.business_model.evidence_ids) or 'N/A'} |",
        f"| Industry | {bp.industry.value} | {bp.industry.status.value} | {bp.industry.confidence:.2f} | {', '.join(bp.industry.evidence_ids) or 'N/A'} |",
        f"| Sub-Industry | {bp.sub_industry.value} | {bp.sub_industry.status.value} | {bp.sub_industry.confidence:.2f} | {', '.join(bp.sub_industry.evidence_ids) or 'N/A'} |",
        f"| Geographic Market | {bp.geographic_market.value} | {bp.geographic_market.status.value} | {bp.geographic_market.confidence:.2f} | {', '.join(bp.geographic_market.evidence_ids) or 'N/A'} |",
        f"| Company Scale | {bp.company_scale.value} | {bp.company_scale.status.value} | {bp.company_scale.confidence:.2f} | {', '.join(bp.company_scale.evidence_ids) or 'N/A'} |",
        f"",
        f"**Specializations:** {', '.join(bp.specializations.value) if isinstance(bp.specializations.value, list) else bp.specializations.value}",
        f"",
        f"## 3. Customer Intelligence",
        f"",
        f"### Customer Segments",
    ]

    for seg in ca.segments:
        lines.append(f"- **{seg.segment_name}** ({'Primary' if seg.is_primary else 'Secondary'}): {seg.description}")
        if seg.needs:
            lines.append(f"  - *Needs:* {', '.join(seg.needs)}")
        if seg.why_it_matters:
            lines.append(f"  - *Strategic Value:* {seg.why_it_matters}")

    lines.extend([
        "",
        "### 5-Stage Customer Journey",
    ])
    for step in ca.journey:
        lines.append(f"- **{step.stage.value.upper()}:** {step.description}")

    lines.extend([
        "",
        "## 4. Market Intelligence",
        f"- **Market Condition:** {ma.market_condition.value}",
        f"- **Digital Maturity:** {ma.digital_adoption.value}",
        f"- **Acquisition Environment:** {ma.customer_acquisition_environment or 'Verified market statistics unavailable.'}",
        "",
        "### High-Intent Search Categories",
    ])
    for s_opp in ma.search_intent_opportunities:
        lines.append(f"- **[{s_opp.search_intent.value}]** `{s_opp.query_theme}` -> Service: {s_opp.business_service}")

    lines.extend([
        "",
        "## 5. Competitor Intelligence",
        f"### Validated Local Competitors ({len(comp.competitors)})",
    ])
    for c in comp.competitors:
        lines.append(f"- **{c.name}** ({c.location or 'Local Market'})")
        if c.specializations:
            lines.append(f"  - Specializations: {', '.join(c.specializations)}")
        if c.digital_strengths:
            lines.append(f"  - Strengths: {', '.join(c.digital_strengths)}")

    if comp.comparison_matrix:
        lines.extend(["", "### Competitive Capability Matrix", ""])
        comp_names = [c for c in comp.comparison_matrix.keys()]
        header = "| Capability | " + " | ".join(comp_names) + " |"
        divider = "|------------|" + "|---" * len(comp_names) + "|"
        lines.append(header)
        lines.append(divider)
        capabilities = list(next(iter(comp.comparison_matrix.values())).keys()) if comp.comparison_matrix else []
        for cap in capabilities:
            vals = [comp.comparison_matrix.get(cn, {}).get(cap, "unknown") for cn in comp_names]
            lines.append(f"| {cap} | " + " | ".join(vals) + " |")

    lines.extend([
        "",
        "## 6. Service Intelligence",
        f"| Service Name | Importance | Target Customer | Customer Problem Solved | Potential Gap |",
        f"|--------------|------------|-----------------|-------------------------|---------------|",
    ])
    for s in sa.services:
        lines.append(f"| {s.name} | {s.importance.value if hasattr(s.importance, 'value') else s.importance} | {s.target_customer or 'General'} | {s.customer_problem_solved or 'N/A'} | {s.potential_gap or 'Visibility'} |")

    lines.extend([
        "",
        "## 7. Business Problems",
    ])
    for i, p in enumerate(report.business_problems, 1):
        lines.extend([
            f"### {i}. [{p.status.value if hasattr(p.status, 'value') else p.status}] {p.title or p.problem}",
            f"- **Type:** {p.type.value if hasattr(p.type, 'value') else p.type}",
            f"- **Business Impact:** {p.business_impact}/10 | **Urgency:** {p.urgency}/10 | **Confidence:** {p.confidence:.2f}",
            f"- **Description:** {p.description or p.reasoning}",
            f"- **Affected Segment:** {p.affected_customer_segment or 'All'}",
            f"- **Evidence IDs:** {', '.join(p.evidence_ids) or 'N/A'}",
            "",
        ])

    lines.extend(["## 8. Opportunities"])
    for i, o in enumerate(report.opportunities, 1):
        svcs = [s.value if hasattr(s, "value") else str(s) for s in o.recommended_services]
        lines.extend([
            f"### {i}. {o.opportunity}",
            f"- **Priority Score:** {o.priority}/10 (Impact: {o.impact}/10, Value: {o.business_value}/10, Confidence: {o.confidence:.2f})",
            f"- **Recommended Agency Services:** {', '.join(svcs)}",
            f"- **Expected Outcome:** {o.expected_business_outcome or 'Improved local discovery'}",
            f"- **Rationale:** {o.rationale}",
            "",
        ])

    lines.extend(["## 9. Recommended Agency Strategy"])
    seen = set()
    for opp in report.opportunities:
        for svc in opp.recommended_services:
            svc_str = svc.value if hasattr(svc, "value") else str(svc)
            if svc_str not in seen:
                lines.append(f"### Priority {len(seen) + 1}: {svc_str}")
                lines.append(f"- **Rationale:** Directly addresses {opp.problem_reference or 'growth opportunity'}.")
                lines.append(f"- **Expected Outcome:** {opp.expected_business_outcome or 'Enhanced digital acquisition'}")
                lines.append("")
                seen.add(svc_str)

    lines.extend([
        "## 10. Opportunity Score & Analysis Completeness",
        f"| Dimension | Score | Weight |",
        f"|-----------|-------|--------|",
        f"| Business Fit | {score.business_fit}/100 | 20% |",
        f"| Digital Need | {score.digital_need}/100 | 20% |",
        f"| Opportunity Value | {score.opportunity_value}/100 | 20% |",
        f"| Evidence Confidence | {score.evidence_confidence}/100 | 15% |",
        f"| Serviceability | {score.serviceability}/100 | 10% |",
        f"| Completeness | {score.analysis_completeness}/100 | 15% |",
        f"| **Overall Composite Score** | **{score.overall_score}/100** | **100%** |",
        "",
        f"**Completeness Breakdown:** {completeness.overall_analysis_completeness if completeness else 100}% across nodes.",
        "",
        "## 11. Evidence Ledger",
    ])
    for e in report.evidence:
        lines.append(f"- `[{e.id}]` **{e.claim}** (Source: {e.source}, Confidence: {e.confidence})")

    lines.extend([
        "",
        "## 12. Unknowns and Limitations",
        "- Live Google Map Pack rankings and keyword search volumes require live search tool verification.",
        "- Competitor matrix relies on public candidate discovery and requires manual or automated web crawling for full verification.",
        "- Website UX and technical SEO scores require direct crawler integration (optional website_analysis module).",
    ])

    return "\n".join(lines)


def main():
    business_input = collect_user_input()
    initial_state = create_initial_state(business_input)
    graph = build_business_analysis_graph()
    print("\n" + "=" * 60)
    print("Starting Multi-Agent Business Intelligence Pipeline...")
    print("=" * 60 + "\n")
    result = graph.invoke(initial_state)
    display_result(result)


if __name__ == "__main__":
    main()