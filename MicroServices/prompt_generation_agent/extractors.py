import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils import (
    load_json_file,
    logger,
    count_findings_by_severity,
    format_issue_summary,
    normalize_string,
)
from models import (
    WebsiteIntelligence,
    BusinessIntelligence,
    IssueFinding,
    PageFinding,
    PromptType,
    BusinessProfile,
    CustomerSegment,
    CustomerAnalysis,
    Service,
    ServiceAnalysis,
    BusinessProblem,
    Opportunity,
    Evidence,
)
from config import settings


def extract_website_intelligence(seo_data: Dict[str, Any], seo_report_path: str) -> WebsiteIntelligence:
    logger.info("Extracting website intelligence from SEO report")

    url = seo_data.get("url", "") or seo_data.get("base_url", "")
    crawl_status = seo_data.get("status", "")
    raw_crawl = seo_data.get("raw_crawl_data", {})
    summary = raw_crawl.get("summary", {})
    pages_crawled = summary.get("total_pages_crawled", 0)

    # Find the domain subdirectory (e.g., atlaskliniek.nl)
    report_dir = Path(seo_report_path).parent
    domain_dirs = [d for d in report_dir.iterdir() if d.is_dir() and "." in d.name]
    domain_dir = domain_dirs[0] if domain_dirs else report_dir

    overview_path = domain_dir / "summary" / "overview.json"
    overview_data, _ = load_json_file(str(overview_path))

    if overview_data:
        overall_score = overview_data.get("overall_score", 0)
        category_scores = overview_data.get("category_scores", {})
    else:
        overall_score = 0
        category_scores = {}

    issues_by_category_path = domain_dir / "issues" / "by_category.json"
    issues_data, _ = load_json_file(str(issues_by_category_path))

    all_findings = []
    if issues_data:
        for category, findings in issues_data.items():
            if isinstance(findings, list):
                for f in findings:
                    f["category"] = category
                    all_findings.append(f)

    severity_counts = count_findings_by_severity(all_findings)

    critical_findings = [f for f in all_findings if f.get("severity") == "critical"]
    high_findings = [f for f in all_findings if f.get("severity") == "high"]
    medium_findings = [f for f in all_findings if f.get("severity") == "medium"]
    low_findings = [f for f in all_findings if f.get("severity") == "low"]

    seo_findings = [f for f in all_findings if f.get("category") == "Seo"]
    accessibility_findings = [f for f in all_findings if f.get("category") == "Accessibility"]
    technical_findings = [f for f in all_findings if f.get("category") in ("Technical", "Performance")]

    pages_path = domain_dir / "pages"
    page_findings = []
    service_page_findings = []
    important_pages = []

    if pages_path.exists():
        for page_file in pages_path.glob("*.json"):
            page_data, _ = load_json_file(str(page_file))
            if not page_data:
                continue

            page_url = page_data.get("url", "")
            if not page_url or page_data.get("content_type") != "text/html":
                continue

            seo = page_data.get("seo", {})
            pf = PageFinding(
                url=page_url,
                title=seo.get("title") or "",
                meta_description=seo.get("meta_description") or "",
                h1=seo.get("h1") or "",
                word_count=seo.get("word_count", 0) or 0,
                status_code=page_data.get("status_code", 0) or 0,
            )

            page_issues = [f for f in all_findings if f.get("url") == page_url]
            pf.issues = [IssueFinding(**f) for f in page_issues]

            page_findings.append(pf)

            url_lower = page_url.lower()
            if "/behandeling/" in url_lower or "/service/" in url_lower or "/treatment/" in url_lower:
                service_page_findings.append(pf)

            if any(x in url_lower for x in ["/", "index", "home", "contact", "about", "team", "behandeling/angst"]):
                if page_url.endswith("/") or "behandeling/angst" in url_lower or "dentist-amsterdam" in url_lower:
                    important_pages.append(pf)

    strengths = []
    weaknesses = []

    if overall_score >= 80:
        strengths.append(f"Good overall SEO score: {overall_score}/100")
    else:
        weaknesses.append(f"Overall SEO score needs improvement: {overall_score}/100")

    for cat, score in category_scores.items():
        if score >= 80:
            strengths.append(f"Strong {cat}: {score}/100")
        elif score < 50:
            weaknesses.append(f"Weak {cat}: {score}/100")

    if severity_counts["critical"] == 0 and severity_counts["high"] == 0:
        strengths.append("No critical or high severity issues")
    else:
        weaknesses.append(f"{severity_counts['critical']} critical and {severity_counts['high']} high severity issues found")

    missing_meta = len([f for f in seo_findings if f.get("type") in ("missing_meta_description", "meta_description_too_short")])
    if missing_meta > 10:
        weaknesses.append(f"{missing_meta} pages with missing or too short meta descriptions")

    long_titles = len([f for f in seo_findings if f.get("type") == "title_too_long"])
    if long_titles > 5:
        weaknesses.append(f"{long_titles} pages with titles exceeding 60 characters")

    missing_h1 = len([f for f in seo_findings if f.get("type") == "missing_h1"])
    if missing_h1 > 0:
        weaknesses.append(f"{missing_h1} pages missing H1 tags")

    images_no_alt = len(accessibility_findings)
    if images_no_alt > 10:
        weaknesses.append(f"{images_no_alt} images missing alt text")

    return WebsiteIntelligence(
        website_url=url,
        website_exists=crawl_status == "completed" and pages_crawled > 0,
        crawl_status=crawl_status,
        pages_analyzed=pages_crawled,
        overall_score=overall_score,
        category_scores=category_scores,
        technical_findings=[IssueFinding(**f) for f in technical_findings[:20]],
        seo_findings=[IssueFinding(**f) for f in seo_findings[:30]],
        content_findings=[IssueFinding(**f) for f in accessibility_findings[:20]],
        ux_findings=[],
        conversion_findings=[],
        page_findings=page_findings[:30],
        service_page_findings=service_page_findings[:20],
        important_pages=important_pages[:15],
        strengths=strengths[:10],
        weaknesses=weaknesses[:15],
        critical_findings=[IssueFinding(**f) for f in critical_findings[:10]],
        high_findings=[IssueFinding(**f) for f in high_findings[:15]],
        medium_findings=[IssueFinding(**f) for f in medium_findings[:20]],
        low_findings=[IssueFinding(**f) for f in low_findings[:20]],
    )


def extract_business_intelligence(biz_data: Dict[str, Any], biz_report_path: str) -> BusinessIntelligence:
    logger.info("Extracting business intelligence from Business Analysis report")

    company_name = biz_data.get("company_name", "")
    website = biz_data.get("website", "")
    industry = biz_data.get("industry", "")
    location = biz_data.get("location", "")

    bp_data = biz_data.get("business_profile", {})
    business_profile = BusinessProfile(
        business_name=bp_data.get("business_name", {}).get("value"),
        official_name=bp_data.get("official_name", {}).get("value"),
        business_type=bp_data.get("business_type", {}).get("value"),
        business_model=bp_data.get("business_model", {}).get("value"),
        industry=bp_data.get("industry", {}).get("value"),
        sub_industry=bp_data.get("sub_industry", {}).get("value"),
        geographic_market=bp_data.get("geographic_market", {}).get("value"),
        primary_location=bp_data.get("primary_location", {}).get("value"),
        service_area=bp_data.get("service_area", {}).get("value"),
        primary_offerings=bp_data.get("primary_offerings", {}).get("value", []),
        secondary_offerings=bp_data.get("secondary_offerings", {}).get("value", []),
        positioning=bp_data.get("positioning", {}).get("value"),
        value_proposition=bp_data.get("value_proposition", {}).get("value"),
        target_market=bp_data.get("target_market", {}).get("value"),
        company_scale=bp_data.get("company_scale", {}).get("value"),
        business_age=bp_data.get("business_age", {}).get("value"),
        specializations=bp_data.get("specializations", {}).get("value", []),
        evidence_ids=bp_data.get("evidence_ids", []),
    )

    ca_data = biz_data.get("customer_analysis", {})
    segments = []
    for seg in ca_data.get("segments", []):
        segments.append(CustomerSegment(
            segment_name=seg.get("segment_name", ""),
            description=seg.get("description", ""),
            is_primary=seg.get("is_primary", False),
            why_it_matters=seg.get("why_it_matters", ""),
            needs=seg.get("needs", []),
            intent_signals=seg.get("intent_signals", []),
            evidence_ids=seg.get("evidence_ids", []),
            confidence=seg.get("confidence", 0.0),
        ))

    primary_segments = [s for s in segments if s.is_primary]
    secondary_segments = [s for s in segments if not s.is_primary]

    customer_analysis = CustomerAnalysis(
        segments=segments,
        primary_segments=primary_segments,
        secondary_segments=secondary_segments,
        journey=ca_data.get("journey", []),
        evidence_ids=ca_data.get("evidence_ids", []),
    )

    sa_data = biz_data.get("service_analysis", {})
    services = []
    for svc in sa_data.get("services", []):
        services.append(Service(
            name=svc.get("name", ""),
            description=svc.get("description", ""),
            category=svc.get("category"),
            importance=svc.get("importance"),
            target_customer=svc.get("target_customer"),
            customer_problem_solved=svc.get("customer_problem_solved"),
            visibility=svc.get("visibility"),
            discoverability=svc.get("discoverability"),
            has_dedicated_page=svc.get("has_dedicated_page", False),
            cta_present=svc.get("cta_present", False),
            confidence=svc.get("confidence", 0.0),
            evidence_ids=svc.get("evidence_ids", []),
        ))

    service_analysis = ServiceAnalysis(
        services=services,
        overall_visibility=sa_data.get("overall_visibility"),
        key_gaps=sa_data.get("key_gaps", []),
        evidence_ids=sa_data.get("evidence_ids", []),
    )

    business_problems = []
    for prob in biz_data.get("business_problems", []):
        business_problems.append(BusinessProblem(
            id=prob.get("id", ""),
            title=prob.get("title", ""),
            problem=prob.get("problem", ""),
            description=prob.get("description", ""),
            type=prob.get("type", ""),
            status=prob.get("status", ""),
            evidence_ids=prob.get("evidence_ids", []),
            business_impact=prob.get("business_impact", 0),
            urgency=prob.get("urgency", 0),
            confidence=prob.get("confidence", 0.0),
            reasoning=prob.get("reasoning", ""),
            severity=prob.get("severity", ""),
            affected_customer_segment=prob.get("affected_customer_segment"),
            affected_service=prob.get("affected_service"),
        ))

    opportunities = []
    for opp in biz_data.get("opportunities", []):
        opportunities.append(Opportunity(
            problem_reference=opp.get("problem_reference", ""),
            opportunity=opp.get("opportunity", ""),
            recommended_services=opp.get("recommended_services", []),
            expected_business_outcome=opp.get("expected_business_outcome", ""),
            priority=opp.get("priority", 0),
            impact=opp.get("impact", 0),
            urgency=opp.get("urgency", 0),
            confidence=opp.get("confidence", 0.0),
            effort=opp.get("effort", 0),
            business_value=opp.get("business_value", 0),
            service_fit=opp.get("service_fit", 0),
            rationale=opp.get("rationale", ""),
        ))

    evidence = []
    for ev in biz_data.get("evidence", []):
        evidence.append(Evidence(
            id=ev.get("id", ""),
            claim=ev.get("claim", ""),
            source=ev.get("source", ""),
            source_type=ev.get("source_type", ""),
            supporting_text=ev.get("supporting_text", ""),
            confidence=ev.get("confidence", 0.0),
            relevance=ev.get("relevance", 0.0),
            timestamp=ev.get("timestamp", ""),
        ))

    return BusinessIntelligence(
        company_name=company_name,
        website=website,
        industry=industry,
        location=location,
        business_profile=business_profile,
        market_analysis=biz_data.get("market_analysis", {}),
        customer_analysis=customer_analysis,
        competitor_analysis=biz_data.get("competitor_analysis", {}),
        service_analysis=service_analysis,
        business_problems=business_problems,
        opportunities=opportunities,
        business_score=biz_data.get("business_score", {}),
        evidence=evidence,
        quality_gate=biz_data.get("quality_gate", {}),
        warnings=biz_data.get("warnings", []),
        errors=biz_data.get("errors", []),
    )


def classify_prompt_type(
    seo: WebsiteIntelligence,
    biz: BusinessIntelligence,
) -> PromptType:
    logger.info("Classifying prompt type based on analysis")

    overall_score = seo.overall_score
    critical_count = len(seo.critical_findings)
    high_count = len(seo.high_findings)
    on_page_score = seo.category_scores.get("On-Page SEO", 100)
    technical_score = seo.category_scores.get("Technical SEO", 100)
    content_score = seo.category_scores.get("Content Quality", 100)

    tech_seo_issues = (
        technical_score < 60
        or on_page_score < 50
        or critical_count > 3
        or high_count > 10
    )

    ux_conversion_issues = (
        len(seo.page_findings) > 10
        or any(f.url for f in seo.page_findings if "contact" in f.url.lower() and not f.meta_description)
        or len([s for s in biz.service_analysis.services if not s.has_dedicated_page]) > 0
    )

    website_poor = overall_score < 50 or critical_count > 5

    services_without_pages = [
        s for s in biz.service_analysis.services
        if s.importance == "core" and not s.has_dedicated_page
    ]

    logger.info(f"Scores - Overall: {overall_score}, Technical: {technical_score}, On-Page: {on_page_score}, Content: {content_score}")
    logger.info(f"Issues - Critical: {critical_count}, High: {high_count}")
    logger.info(f"Services without dedicated pages: {len(services_without_pages)}")
    logger.info(f"Tech/SEO dominates: {tech_seo_issues}, UX/Conversion dominates: {ux_conversion_issues}")

    if website_poor:
        return PromptType.WEBSITE_REDESIGN
    elif tech_seo_issues and not ux_conversion_issues:
        return PromptType.SEO_OPTIMIZATION
    elif ux_conversion_issues and not tech_seo_issues:
        return PromptType.UX_CONVERSION_OPTIMIZATION
    else:
        return PromptType.COMBINED_WEBSITE_OPTIMIZATION