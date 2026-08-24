import json
from pathlib import Path

from business_analysis.graph import build_business_analysis_graph
from business_analysis.schemas.models import BusinessInput, FinalBusinessAnalysis
from business_analysis.state import create_initial_state


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
        print(
            f"Analysis Completeness: {report.completeness.overall_analysis_completeness}%"
        )
    if report.quality_gate:
        print(f"Quality Gate Status: {report.quality_gate.quality_status}")

    print("\nScore Breakdown:")
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
            print(
                f"  {i}. [{problem.type.value if hasattr(problem.type, 'value') else problem.type}] {problem.title or problem.problem}"
            )
            print(
                f"     Status: {problem.status.value if hasattr(problem.status, 'value') else problem.status} | Impact: {problem.business_impact}/10 | Urgency: {problem.urgency}/10 | Confidence: {problem.confidence:.2f}"
            )

    if report.service_analysis and report.service_analysis.services:
        print(
            f"\nExtracted Business Services ({len(report.service_analysis.services)}):"
        )
        for s in report.service_analysis.services:
            print(
                f"  - {s.name} (Importance: {s.importance.value if hasattr(s.importance, 'value') else s.importance})"
            )

    # Separate [WARNING] entries from hard errors
    hard_errors = [
        e
        for e in report.errors
        if not e.startswith("[WARNING]")
        and not e.startswith("[QG]")
        and not e.startswith("[ServiceAnalysis]")
    ]
    warn_entries = [
        e
        for e in report.errors
        if e.startswith(("[WARNING]", "[QG]", "[ServiceAnalysis]"))
    ]

    if hard_errors:
        print("\n--- Hard Errors ---")
        for err in hard_errors:
            print(f"  ✗ {err}")

    if warn_entries:
        print("\n--- Warnings ---")
        for w in warn_entries:
            print(f"  ⚠ {w}")

    save_outputs(report)


def save_outputs(report: FinalBusinessAnalysis):
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    safe_name = "".join(c if c.isalnum() else "_" for c in report.company_name).strip(
        "_"
    )

    json_path = output_dir / f"{safe_name}_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
    print(f"\nSaved JSON: {json_path}")

    md_path = output_dir / f"{safe_name}_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_report(report))
    print(f"Saved Markdown: {md_path}")

    sdr_path = output_dir / f"{safe_name}_sdr_brief.md"
    with open(sdr_path, "w", encoding="utf-8") as f:
        f.write(generate_sdr_brief_markdown(report))
    print(f"Saved SDR Brief: {sdr_path}")


def generate_markdown_report(report: FinalBusinessAnalysis) -> str:
    bp = report.business_profile
    ma = report.market_analysis
    ca = report.customer_analysis
    comp = report.competitor_analysis
    sa = report.service_analysis
    score = report.business_score
    qg = report.quality_gate
    completeness = report.completeness

    top_opp = (
        report.opportunities[0].opportunity
        if report.opportunities
        else "Specialized service acquisition optimization"
    )

    lines = [
        "# Business Intelligence & Growth Opportunity Report",
        f"**Business:** {report.company_name}",
        f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Industry:** {report.industry}",
        f"**Location:** {report.location}",
        f"**Website:** {report.website or 'Not provided'}",
        f"**Quality Gate:** {qg.quality_status if qg else 'PASSED'}",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"{report.company_name} is a specialist provider operating in {report.location}. "
        f"The primary growth opportunity identified is **{top_opp}**. "
        f"The strongest potential agency strategy is to strengthen local customer acquisition around specialized offerings "
        f"(such as dental anxiety care and complex rehabilitation) through targeted service landing pages, local search optimization, "
        f"and trust-building conversion funnels. This recommendation is currently grounded in explicit business evidence and "
        f"should be validated against live search ranking data.",
        "",
        f"**Overall Opportunity Score:** {score.overall_score}/100 ({score.priority.value} PRIORITY)",
        "",
        "## 2. Business Profile",
        "",
        "| Attribute | Value | Status | Confidence | Evidence IDs |",
        "|-----------|-------|--------|------------|--------------|",
        f"| Business Type | {bp.business_type.value} | {bp.business_type.status.value} | {bp.business_type.confidence:.2f} | {', '.join(bp.business_type.evidence_ids) or 'N/A'} |",
        f"| Business Model | {bp.business_model.value} | {bp.business_model.status.value} | {bp.business_model.confidence:.2f} | {', '.join(bp.business_model.evidence_ids) or 'N/A'} |",
        f"| Industry | {bp.industry.value} | {bp.industry.status.value} | {bp.industry.confidence:.2f} | {', '.join(bp.industry.evidence_ids) or 'N/A'} |",
        f"| Sub-Industry | {bp.sub_industry.value} | {bp.sub_industry.status.value} | {bp.sub_industry.confidence:.2f} | {', '.join(bp.sub_industry.evidence_ids) or 'N/A'} |",
        f"| Geographic Market | {bp.geographic_market.value} | {bp.geographic_market.status.value} | {bp.geographic_market.confidence:.2f} | {', '.join(bp.geographic_market.evidence_ids) or 'N/A'} |",
        f"| Company Scale | {bp.company_scale.value} | {bp.company_scale.status.value} | {bp.company_scale.confidence:.2f} | {', '.join(bp.company_scale.evidence_ids) or 'N/A'} |",
        "",
        f"**Specializations:** {', '.join(bp.specializations.value) if isinstance(bp.specializations.value, list) else bp.specializations.value}",
        "",
        "## 3. Customer Intelligence",
        "",
        "### Customer Segments",
    ]

    for seg in ca.segments:
        lines.append(
            f"- **{seg.segment_name}** ({'Primary' if seg.is_primary else 'Secondary'}): {seg.description}"
        )
        if seg.needs:
            lines.append(f"  - *Needs:* {', '.join(seg.needs)}")
        if seg.why_it_matters:
            lines.append(f"  - *Strategic Value:* {seg.why_it_matters}")

    lines.extend(
        [
            "",
            "### 5-Stage Customer Journey",
        ]
    )
    for step in ca.journey:
        lines.append(f"- **{step.stage.value.upper()}:** {step.description}")

    lines.extend(
        [
            "",
            "## 4. Market Intelligence",
            f"- **Market Condition:** {ma.market_condition.value}",
            f"- **Digital Maturity:** {ma.digital_adoption.value}",
            f"- **Acquisition Environment:** {ma.customer_acquisition_environment or 'Verified market statistics unavailable.'}",
            "",
            "### High-Intent Search Categories",
        ]
    )
    for s_opp in ma.search_intent_opportunities:
        lines.append(
            f"- **[{s_opp.search_intent.value}]** `{s_opp.query_theme}` -> Service: {s_opp.business_service}"
        )

    lines.extend(
        [
            "",
            "## 5. Competitor Intelligence",
            f"### Validated Local Competitors ({len(comp.competitors)})",
        ]
    )
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
        capabilities = (
            list(next(iter(comp.comparison_matrix.values())).keys())
            if comp.comparison_matrix
            else []
        )
        for cap in capabilities:
            vals = [
                comp.comparison_matrix.get(cn, {}).get(cap, "unknown")
                for cn in comp_names
            ]
            lines.append(f"| {cap} | " + " | ".join(vals) + " |")

    lines.extend(
        [
            "",
            "## 6. Service Intelligence",
            "| Service Name | Importance | Target Customer | Customer Problem Solved | Potential Gap |",
            "|--------------|------------|-----------------|-------------------------|---------------|",
        ]
    )
    for s in sa.services:
        lines.append(
            f"| {s.name} | {s.importance.value if hasattr(s.importance, 'value') else s.importance} | {s.target_customer or 'General'} | {s.customer_problem_solved or 'N/A'} | {s.potential_gap or 'Visibility'} |"
        )

    lines.extend(
        [
            "",
            "## 7. Business Problems",
        ]
    )
    for i, p in enumerate(report.business_problems, 1):
        lines.extend(
            [
                f"### {i}. [{p.status.value if hasattr(p.status, 'value') else p.status}] {p.title or p.problem}",
                f"- **Type:** {p.type.value if hasattr(p.type, 'value') else p.type}",
                f"- **Business Impact:** {p.business_impact}/10 | **Urgency:** {p.urgency}/10 | **Confidence:** {p.confidence:.2f}",
                f"- **Description:** {p.description or p.reasoning}",
                f"- **Affected Segment:** {p.affected_customer_segment or 'All'}",
                f"- **Evidence IDs:** {', '.join(p.evidence_ids) or 'N/A'}",
                "",
            ]
        )

    lines.extend(["## 8. Opportunities"])
    for i, o in enumerate(report.opportunities, 1):
        svcs = [
            s.value if hasattr(s, "value") else str(s) for s in o.recommended_services
        ]
        lines.extend(
            [
                f"### {i}. {o.opportunity}",
                f"- **Priority Score:** {o.priority}/10 (Impact: {o.impact}/10, Value: {o.business_value}/10, Confidence: {o.confidence:.2f})",
                f"- **Recommended Agency Services:** {', '.join(svcs)}",
                f"- **Expected Outcome:** {o.expected_business_outcome or 'Improved local discovery'}",
                f"- **Rationale:** {o.rationale}",
                "",
            ]
        )

    lines.extend(["## 9. Recommended Agency Strategy"])
    seen = set()
    for opp in report.opportunities:
        for svc in opp.recommended_services:
            svc_str = svc.value if hasattr(svc, "value") else str(svc)
            if svc_str not in seen:
                lines.append(f"### Priority {len(seen) + 1}: {svc_str}")
                lines.append(
                    f"- **Rationale:** Directly addresses {opp.problem_reference or 'growth opportunity'}."
                )
                lines.append(
                    f"- **Expected Outcome:** {opp.expected_business_outcome or 'Enhanced digital acquisition'}"
                )
                lines.append("")
                seen.add(svc_str)

    lines.extend(
        [
            "## 10. Opportunity Score & Analysis Completeness",
            "| Dimension | Score | Weight |",
            "|-----------|-------|--------|",
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
        ]
    )
    for e in report.evidence:
        lines.append(
            f"- `[{e.id}]` **{e.claim}** (Source: {e.source}, Confidence: {e.confidence})"
        )

    lines.extend(
        [
            "",
            "## 12. Unknowns and Limitations",
            "- Live Google Map Pack rankings and keyword search volumes require live search tool verification.",
            "- Competitor matrix relies on public candidate discovery and requires manual or automated web crawling for full verification.",
            "- Website UX and technical SEO scores require direct crawler integration (optional website_analysis module).",
            f"- Website analysis status: {'Available' if report.website_analysis else 'UNAVAILABLE — website was not crawled in this run.'}",
            "",
            "## 13. Quality Gate Report",
        ]
    )
    if qg:
        lines.append(f"**Status:** `{qg.quality_status}`")
        if qg.passed_checks:
            lines.append("\n**Passed Checks:**")
            for chk in qg.passed_checks:
                lines.append(f"- ✓ {chk}")
        if qg.failed_checks:
            lines.append("\n**Failed Checks:**")
            for chk in qg.failed_checks:
                lines.append(f"- ✗ {chk}")
        if qg.warnings:
            lines.append("\n**Warnings:**")
            for w in qg.warnings:
                lines.append(f"- ⚠ {w}")
        if qg.notes:
            lines.append("\n**Notes:**")
            for n in qg.notes:
                lines.append(f"- {n}")

    return "\n".join(lines)


def generate_sdr_brief_markdown(report: FinalBusinessAnalysis) -> str:
    """Generate a concise, machine-readable SDR Opportunity Brief."""
    score = report.business_score
    bp = report.business_profile
    qg = report.quality_gate

    top_problems = report.business_problems[:3]
    top_opps = report.opportunities[:3]

    # Collect unique recommended services in priority order
    seen_svcs: set = set()
    rec_services = []
    for opp in report.opportunities:
        for svc in opp.recommended_services:
            sv = svc.value if hasattr(svc, "value") else str(svc)
            if sv not in seen_svcs:
                rec_services.append(sv)
                seen_svcs.add(sv)

    # Derive customer summary
    ca = report.customer_analysis
    primary_customer = (
        ca.primary_segments[0].segment_name
        if ca.primary_segments
        else (
            ca.segments[0].segment_name
            if ca.segments
            else (ca.primary_customers[0] if ca.primary_customers else "Not specified")
        )
    )

    # Verification needed
    verif_items = []
    if not report.website_analysis:
        verif_items.append("Website crawl and technical SEO audit")
    if qg and qg.warnings:
        verif_items.append("Market/competitor data (not researched in this run)")
    verif_items.append("Live SERP rankings for target keywords")
    verif_items.append("Google Map Pack visibility")

    confidence = score.evidence_confidence / 100.0
    qg_status = qg.quality_status if qg else "UNKNOWN"

    lines = [
        "# SDR Opportunity Brief",
        "*Auto-generated by BusinessAnalysisAgent — for SDR use only*",
        "",
        "---",
        "",
        f"**Lead:** {report.company_name}",
        f"**Industry:** {report.industry}",
        f"**Location:** {report.location}",
        f"**Website:** {report.website or 'Not provided'}",
        f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        f"## Opportunity Score: {score.overall_score}/100 — Priority: **{score.priority.value}**",
        "",
        f"Quality Gate: `{qg_status}` | Analysis Completeness: {report.completeness.overall_analysis_completeness if report.completeness else 0}%",
        "",
        "---",
        "",
        "## Business Summary",
        "",
    ]

    btype = (
        bp.business_type.value
        if hasattr(bp.business_type, "value")
        else str(bp.business_type)
    )
    bmodel = (
        bp.business_model.value
        if hasattr(bp.business_model, "value")
        else str(bp.business_model)
    )
    industry_val = (
        bp.industry.value if hasattr(bp.industry, "value") else report.industry
    )
    location_val = (
        bp.geographic_market.value
        if hasattr(bp.geographic_market, "value")
        else report.location
    )
    specs = (
        bp.specializations.value
        if hasattr(bp.specializations, "value")
        and isinstance(bp.specializations.value, list)
        else []
    )

    lines.append(
        f"{report.company_name} is a **{btype}** ({bmodel}) operating in **{industry_val}**, {location_val}."
    )
    if specs:
        lines.append(f"Specializations: {', '.join(specs)}.")
    lines.append("")

    lines.extend(
        [
            f"**Primary Customer:** {primary_customer}",
            "",
            "---",
            "",
            "## Top Business Problems",
            "",
        ]
    )
    for i, p in enumerate(top_problems, 1):
        status_label = p.status.value if hasattr(p.status, "value") else str(p.status)
        ptype = p.type.value if hasattr(p.type, "value") else str(p.type)
        lines.append(f"{i}. **[{status_label}]** {p.title or p.problem}")
        lines.append(
            f"   - Type: `{ptype}` | Impact: {p.business_impact}/10 | Confidence: {p.confidence:.0%}"
        )
        if p.evidence_ids:
            lines.append(f"   - Evidence: {', '.join(p.evidence_ids[:3])}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Top Opportunities",
            "",
        ]
    )
    for i, o in enumerate(top_opps, 1):
        svcs = [
            s.value if hasattr(s, "value") else str(s) for s in o.recommended_services
        ]
        lines.append(f"{i}. **{o.opportunity}**")
        lines.append(f"   - Services: `{', '.join(svcs)}`")
        lines.append(
            f"   - Expected Outcome: {o.expected_business_outcome or 'Improved acquisition'}"
        )
        lines.append(f"   - Priority: {o.priority}/10 | Confidence: {o.confidence:.0%}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Recommended Agency Services",
            "",
        ]
    )
    for i, svc in enumerate(rec_services[:6], 1):
        lines.append(f"{i}. `{svc}`")

    if rec_services:
        lines.extend(
            [
                "",
                "**Why These Services:**",
                f"Derived from {len(top_problems)} identified business problems mapped to agency service taxonomy. "
                f"Services address discovery gaps, service visibility deficits, and conversion friction "
                f"specific to {report.industry} in {report.location}.",
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## Analysis Confidence",
            "",
            f"- **Evidence Confidence:** {score.evidence_confidence}/100",
            f"- **Analysis Completeness:** {score.analysis_completeness}%",
            f"- **Quality Gate:** `{qg_status}`",
            "",
            "## Verification Required Before Outreach",
            "",
        ]
    )
    for v in verif_items:
        lines.append(f"- {v}")

    if qg and qg.warnings:
        lines.extend(["", "## Caveats", ""])
        for w in qg.warnings:
            lines.append(f"- ⚠ {w}")

    return "\n".join(lines)


import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Business Intelligence and Growth Opportunity Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run built-in Atlas Kliniek demo case:
    python main.py --demo

  Run from a JSON input file:
    python main.py --file input_sample.json

  Run directly with CLI arguments:
    python main.py --company "Atlas Kliniek" --industry "Dental Services" --location "Amsterdam" --description "Private specialist clinic..."

  Interactive prompt mode (default when no arguments provided):
    python main.py
""",
    )
    parser.add_argument(
        "--demo",
        "-d",
        action="store_true",
        help="Run with default Atlas Kliniek benchmark test case",
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Path to JSON file containing business input"
    )
    parser.add_argument("--company", "-c", type=str, help="Company / business name")
    parser.add_argument("--website", "-w", type=str, help="Website URL")
    parser.add_argument("--industry", "-i", type=str, help="Industry name")
    parser.add_argument("--location", "-l", type=str, help="Location / city")
    parser.add_argument("--description", type=str, help="Business description")
    parser.add_argument("--services", type=str, help="Products / services offered")
    parser.add_argument("--customers", type=str, help="Target customers")
    parser.add_argument("--info", type=str, help="Additional business information")
    return parser.parse_args()


def get_demo_input() -> BusinessInput:
    return BusinessInput(
        company_name="Atlas Kliniek",
        website="https://www.atlaskliniek.nl/en/dentist-amsterdam/",
        industry="Dental Services Industry",
        location="Herengracht 318, Amsterdam",
        description="Atlas Kliniek is a private, specialist dental practice headquartered in Amsterdam, Netherlands. Established in 1945 and operating at its Prins Hendrikkade location since 1975, the clinic has built a reputation as a trusted provider of advanced, patient-centered dental care for over 80 years.",
        products_services="Special Dentistry & Complex Care. Dental Anxiety Treatment: Compassionate, specialized care for patients with dental phobia or high anxiety, using gentle techniques, extended consultation time, and sedation options when needed.",
        target_customers="Patients with teeth problems",
        additional_info="Complex Case Management: Multidisciplinary treatment planning for medically complex patients or those requiring extensive rehabilitation.",
    )


def load_input_from_file(filepath: str) -> BusinessInput:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return BusinessInput(**data)


def main():
    args = parse_args()

    if args.demo:
        print("Running in DEMO mode (Atlas Kliniek benchmark case)...")
        business_input = get_demo_input()
    elif args.file:
        print(f"Loading business input from file: {args.file}")
        business_input = load_input_from_file(args.file)
    elif args.company and args.industry and args.location:
        business_input = BusinessInput(
            company_name=args.company,
            website=args.website,
            industry=args.industry,
            location=args.location,
            description=args.description,
            products_services=args.services,
            target_customers=args.customers,
            additional_info=args.info,
        )
    else:
        # Fallback to interactive mode if insufficient CLI flags provided
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
