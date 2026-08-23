from typing import Dict, Any, List, Optional
from pathlib import Path

from utils import logger, truncate_text
from models import (
    WebsiteIntelligence,
    BusinessIntelligence,
    PromptType,
    StructuredOutput,
    PagePlan,
    RecommendedChanges,
)
from config import settings


def build_prompt_context(
    seo: WebsiteIntelligence,
    biz: BusinessIntelligence,
    prompt_type: PromptType,
) -> Dict[str, Any]:
    logger.info("Building prompt context for LLM")

    services_without_pages = [
        s for s in biz.service_analysis.services
        if s.importance == "core" and not s.has_dedicated_page
    ]

    primary_customers = biz.customer_analysis.primary_segments
    customer_needs = []
    for seg in primary_customers:
        customer_needs.extend(seg.needs)

    critical_issues = [f for f in seo.critical_findings]
    high_issues = [f for f in seo.high_findings]

    top_seo_issues = []
    for f in critical_issues[:5] + high_issues[:10]:
        top_seo_issues.append({
            "type": f.type,
            "title": f.title,
            "url": f.url,
            "description": f.description,
        })

    important_pages_summary = []
    for p in seo.important_pages[:10]:
        page_issues = [i.type for i in p.issues]
        important_pages_summary.append({
            "url": p.url,
            "title": p.title,
            "meta_description": p.meta_description[:100] if p.meta_description else "MISSING",
            "h1": p.h1,
            "word_count": p.word_count,
            "issues": page_issues,
        })

    service_pages_summary = []
    for p in seo.service_page_findings[:10]:
        page_issues = [i.type for i in p.issues]
        service_pages_summary.append({
            "url": p.url,
            "title": p.title,
            "meta_description": p.meta_description[:100] if p.meta_description else "MISSING",
            "h1": p.h1,
            "word_count": p.word_count,
            "issues": page_issues,
        })

    business_problems_summary = []
    for p in biz.business_problems:
        business_problems_summary.append({
            "id": p.id,
            "title": p.title,
            "problem": p.problem,
            "description": p.description,
            "impact": p.business_impact,
            "urgency": p.urgency,
            "affected_service": p.affected_service,
            "affected_segment": p.affected_customer_segment,
        })

    opportunities_summary = []
    for o in biz.opportunities:
        opportunities_summary.append({
            "problem_reference": o.problem_reference,
            "opportunity": o.opportunity,
            "recommended_services": o.recommended_services,
            "expected_outcome": o.expected_business_outcome,
            "priority": o.priority,
        })

    competitor_gaps = []
    comp_analysis = biz.competitor_analysis
    if comp_analysis and "comparison_matrix" in comp_analysis:
        for name, metrics in comp_analysis["comparison_matrix"].items():
            if name != biz.company_name:
                gaps = [k for k, v in metrics.items() if v == "not_verified" or v == "unknown"]
                if gaps:
                    competitor_gaps.append({
                        "competitor": name,
                        "gaps": gaps,
                    })

    context = {
        "company_name": biz.company_name,
        "website": biz.website,
        "industry": biz.industry,
        "location": biz.location,
        "prompt_type": prompt_type.value,
        "website_summary": {
            "url": seo.website_url,
            "overall_score": seo.overall_score,
            "category_scores": seo.category_scores,
            "pages_analyzed": seo.pages_analyzed,
            "strengths": seo.strengths[:5],
            "weaknesses": seo.weaknesses[:10],
            "critical_issues_count": len(critical_issues),
            "high_issues_count": len(high_issues),
        },
        "business_summary": {
            "company_name": biz.company_name,
            "industry": biz.industry,
            "location": biz.location,
            "primary_services": [s.name for s in biz.service_analysis.services if s.importance == "core"],
            "all_services": [s.name for s in biz.service_analysis.services],
            "services_without_dedicated_pages": [s.name for s in services_without_pages],
            "primary_customers": [s.segment_name for s in primary_customers],
            "customer_needs": list(set(customer_needs)),
            "business_score": biz.business_score.get("overall_score", 0),
        },
        "top_seo_issues": top_seo_issues,
        "important_pages": important_pages_summary,
        "service_pages": service_pages_summary,
        "business_problems": business_problems_summary,
        "opportunities": opportunities_summary,
        "competitor_gaps": competitor_gaps,
        "evidence_ids": [e.id for e in biz.evidence],
    }

    return context


def format_context_for_llm(context: Dict[str, Any]) -> str:
    lines = []

    lines.append(f"Company: {context['company_name']}")
    lines.append(f"Website: {context['website']}")
    lines.append(f"Industry: {context['industry']}")
    lines.append(f"Location: {context['location']}")
    lines.append(f"Prompt Type: {context['prompt_type']}")
    lines.append("")

    ws = context['website_summary']
    lines.append(f"SEO Score: {ws['overall_score']}/100 | Pages: {ws['pages_analyzed']}")
    lines.append(f"Categories: {', '.join(f'{k}:{v}' for k,v in ws['category_scores'].items())}")
    lines.append(f"Strengths: {'; '.join(ws['strengths'][:3])}")
    lines.append(f"Weaknesses: {'; '.join(ws['weaknesses'][:5])}")
    lines.append("")

    bs = context['business_summary']
    lines.append(f"Core Services: {', '.join(bs['primary_services'])}")
    lines.append(f"Missing Pages: {', '.join(bs['services_without_dedicated_pages'])}")
    lines.append(f"Primary Customers: {', '.join(bs['primary_customers'])}")
    lines.append(f"Customer Needs: {', '.join(bs['customer_needs'][:5])}")
    lines.append("")

    lines.append("Top SEO Issues:")
    for issue in context['top_seo_issues'][:3]:
        lines.append(f"  [{issue['type']}] {issue['title'][:40]} - {issue['url']}")
    lines.append("")

    lines.append("Key Pages:")
    for page in context['important_pages'][:3]:
        lines.append(f"  {page['url']} | Title: {page['title'][:30]} | Meta: {page['meta_description'][:30]} | Issues: {','.join(page['issues'][:2])}")
    lines.append("")

    lines.append("Service Pages:")
    for page in context['service_pages'][:3]:
        lines.append(f"  {page['url']} | Issues: {','.join(page['issues'][:2])}")
    lines.append("")

    lines.append("Business Problems:")
    for prob in context['business_problems'][:2]:
        lines.append(f"  {prob['title']}: {prob['problem'][:50]} (Impact:{prob['impact']})")
    lines.append("")

    lines.append("Opportunities:")
    for opp in context['opportunities'][:2]:
        lines.append(f"  {opp['opportunity'][:60]} (Priority:{opp['priority']})")

    return "\n".join(lines)[:1800]


from prompts import SYSTEM_PROMPT, build_user_prompt


def generate_prompt_with_llm(context: Dict[str, Any]) -> str:
    logger.info("Generating prompt with Ollama (chat API)")

    try:
        import httpx
    except ImportError:
        logger.error("httpx not installed")
        return ""

    formatted_context = format_context_for_llm(context)
    user_prompt = build_user_prompt(formatted_context)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        with httpx.Client(timeout=600.0) as client:
            response = client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.7,
                        "num_predict": 2500,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            msg = result.get("message", {})
            # qwen3 outputs to 'thinking' field, check both
            generated = msg.get("content", "").strip()
            if not generated:
                generated = msg.get("thinking", "").strip()
            logger.info(f"Generated prompt length: {len(generated)} characters")
            return generated
    except httpx.TimeoutException:
        logger.error("LLM generation timed out")
        return ""
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return ""


def build_structured_output(
    seo: WebsiteIntelligence,
    biz: BusinessIntelligence,
    prompt_type: PromptType,
    generated_prompt: str,
    context: Dict[str, Any],
    seo_report_path: str,
    biz_report_path: str,
) -> StructuredOutput:
    logger.info("Building structured output")

    identified_problems = []
    for f in seo.critical_findings + seo.high_findings:
        identified_problems.append({
            "source": "SEO",
            "type": f.type,
            "title": f.title,
            "url": f.url,
            "severity": f.severity,
            "description": f.description,
        })

    for p in biz.business_problems:
        identified_problems.append({
            "source": "Business",
            "type": p.type,
            "title": p.title,
            "problem": p.problem,
            "impact": p.business_impact,
            "urgency": p.urgency,
            "affected_service": p.affected_service,
            "affected_segment": p.affected_customer_segment,
        })

    business_opportunities = []
    for o in biz.opportunities:
        business_opportunities.append({
            "problem_reference": o.problem_reference,
            "opportunity": o.opportunity,
            "recommended_services": o.recommended_services,
            "expected_outcome": o.expected_business_outcome,
            "priority": o.priority,
        })

    services_without_pages = [
        s for s in biz.service_analysis.services
        if s.importance == "core" and not s.has_dedicated_page
    ]

    # Build evidence-based recommended changes from actual findings
    seo_changes = []
    seo_findings = seo.seo_findings + seo.technical_findings
    
    meta_issues = [f for f in seo_findings if 'meta' in f.type.lower() and 'description' in f.type.lower()]
    if meta_issues:
        seo_changes.append(f"Fix missing/short meta descriptions on {len(meta_issues)} identified pages")
    
    title_issues = [f for f in seo_findings if 'title' in f.type.lower()]
    if title_issues:
        seo_changes.append(f"Optimize title tags exceeding 60 characters on {len(title_issues)} identified pages")
    
    h1_issues = [f for f in seo_findings if 'h1' in f.type.lower()]
    if h1_issues:
        seo_changes.append(f"Add missing H1 tags on {len(h1_issues)} identified pages")
    
    alt_issues = [f for f in seo.accessibility_findings] if hasattr(seo, 'accessibility_findings') else []
    if alt_issues:
        seo_changes.append(f"Add missing alt text to images on {len(alt_issues)} identified pages")
    
    schema_issues = [f for f in seo_findings if 'schema' in f.type.lower() or 'structured' in f.type.lower()]
    if schema_issues:
        seo_changes.append("Address structured data/schema markup issues")
    
    canonical_issues = [f for f in seo_findings if 'canonical' in f.type.lower()]
    if canonical_issues:
        seo_changes.append("Fix canonical URL issues")
    
    internal_link_issues = [f for f in seo_findings if 'internal' in f.type.lower() and 'link' in f.type.lower()]
    if internal_link_issues:
        seo_changes.append("Improve internal linking structure")
    
    if not seo_changes:
        seo_changes = ["Address identified SEO issues from analysis"]

    # UX changes from business analysis
    ux_changes = []
    if services_without_pages:
        ux_changes.append("Improve navigation to specialized service pages missing dedicated pages")
    
    anxiety_segments = [s for s in biz.customer_analysis.primary_segments if 'anxiety' in s.segment_name.lower() or 'fear' in s.segment_name.lower()]
    if anxiety_segments:
        ux_changes.append("Add clear trust signals and reassurance paths for anxiety patients")
    
    contact_pages = [p for p in seo.important_pages if 'contact' in p.url.lower() or 'booking' in p.url.lower()]
    if contact_pages:
        ux_changes.append("Optimize contact/booking flow on identified pages")
    
    mobile_issues = [f for f in seo_findings if 'mobile' in f.type.lower() or 'viewport' in f.type.lower()]
    if mobile_issues:
        ux_changes.append("Improve mobile navigation experience per identified issues")
    
    if not ux_changes:
        ux_changes = ["Address identified UX friction points from analysis"]

    # Content changes
    content_changes = []
    if services_without_pages:
        content_changes.append(f"Create dedicated service pages for: {', '.join([s.name for s in services_without_pages])}")
    
    thin_content = [f for f in seo.content_findings if 'thin' in f.type.lower()] if hasattr(seo, 'content_findings') else []
    if thin_content:
        content_changes.append(f"Expand thin content on {len(thin_content)} identified pages")
    
    if anxiety_segments:
        content_changes.append("Add FAQ sections addressing anxiety patient needs")
    
    if not content_changes:
        content_changes = ["Address identified content gaps from analysis"]

    # Conversion changes
    conversion_changes = []
    if services_without_pages:
        conversion_changes.append("Add prominent CTAs on new service pages")
    
    if contact_pages:
        conversion_changes.append("Improve contact form visibility and usability on identified pages")
    
    mobile_cta_issues = [f for f in seo_findings if 'mobile' in f.type.lower() and ('cta' in f.type.lower() or 'click' in f.type.lower())]
    if mobile_cta_issues:
        conversion_changes.append("Add click-to-call for mobile users on affected pages")
    
    if not conversion_changes:
        conversion_changes = ["Address identified conversion friction from analysis"]

    # Design changes - only if supported by analysis
    design_changes = []
    if anxiety_segments:
        design_changes.append("Use calming color palette and reassuring visual hierarchy for anxiety-focused content")
    design_changes.append("Establish clear visual hierarchy for service offerings")
    design_changes.append("Improve typography readability")
    if hasattr(seo, 'accessibility_findings') and seo.accessibility_findings:
        design_changes.append("Ensure sufficient color contrast per accessibility findings")

    # Technical changes from actual findings
    technical_changes = []
    perf_score = seo.category_scores.get('Performance', 0)
    if perf_score < 80:
        technical_changes.append("Optimize Core Web Vitals (LCP, CLS, INP) per performance findings")
    
    if alt_issues:
        technical_changes.append("Compress and add alt text to images per identified issues")
    
    cache_issues = [f for f in seo_findings if 'cach' in f.type.lower()]
    if cache_issues:
        technical_changes.append("Enable browser caching per identified issues")
    
    render_blocking = [f for f in seo_findings if 'render' in f.type.lower() and 'block' in f.type.lower()]
    if render_blocking:
        technical_changes.append("Minimize render-blocking resources per identified issues")
    
    if not technical_changes:
        technical_changes = ["Address identified technical issues from analysis"]

    recommended_changes = RecommendedChanges(
        seo=seo_changes,
        ux=ux_changes,
        content=content_changes,
        conversion=conversion_changes,
        design=design_changes,
        technical=technical_changes,
    )

    page_plan = []
    for p in seo.important_pages[:10]:
        issues_list = [i.type for i in p.issues] if p.issues else []
        seo_reason = f"Address {len(issues_list)} identified SEO issues" if issues_list else "Optimize per page analysis"
        
        # Determine page type for appropriate reasoning
        url_lower = p.url.lower()
        is_service = any(x in url_lower for x in ['behandeling', 'service', 'treatment'])
        is_contact = 'contact' in url_lower or 'booking' in url_lower
        is_about = 'about' in url_lower or 'team' in url_lower
        is_terms = 'terms' in url_lower or 'voorwaarden' in url_lower
        is_blog = any(x in url_lower for x in ['2023/', '2024/', '2025/', '2026/', 'blog', 'news'])
        
        if is_service:
            biz_reason = "Service page for verified core service"
            conv_reason = "Service-specific conversion pathway"
        elif is_contact:
            biz_reason = "Primary contact/conversion page"
            conv_reason = "Direct conversion pathway"
        elif is_about:
            biz_reason = "Trust and credibility building page"
            conv_reason = "Support trust signals"
        elif is_terms:
            biz_reason = "Legal compliance page"
            conv_reason = "Not a primary conversion page"
        elif is_blog:
            biz_reason = "Content marketing page"
            conv_reason = "Informational content, not primary conversion"
        else:
            biz_reason = "Key page identified in SEO analysis"
            conv_reason = "Support overall site goals"
        
        ux_reason = "Improve user engagement and navigation per page issues"
        
        page_plan.append(PagePlan(
            page_url=p.url,
            page_name=p.title or p.url.split("/")[-2] or "Homepage",
            current_problem=f"SEO issues: {', '.join(issues_list) if issues_list else 'None identified'}",
            required_improvement="Optimize on-page SEO per identified issues; improve content depth where thin",
            business_reason=biz_reason,
            seo_reason=seo_reason,
            ux_reason=ux_reason,
            conversion_reason=conv_reason,
        ))

    for s in services_without_pages:
        page_plan.append(PagePlan(
            page_url=f"/{normalize_service_name(s.name)}/",
            page_name=s.name,
            current_problem="No dedicated service page exists per business analysis",
            required_improvement="Create dedicated service landing page with value proposition, trust elements, FAQ, CTA",
            business_reason=f"Core service '{s.name}' identified as high-value offering in business analysis",
            seo_reason="Capture high-intent search traffic for specialized service",
            ux_reason="Provide dedicated path for customer segment seeking this service",
            conversion_reason="Enable direct conversion for high-value service",
        ))

    preservation_rules = [
        f"Company name: {biz.company_name}",
        f"Website URL: {biz.website}",
        f"Location: {biz.location}",
        f"Verified services: {', '.join([s.name for s in biz.service_analysis.services if s.confidence > 0.8])}",
        "Contact information from existing website",
        "Existing brand identity (logo, colors) if present on current website",
        "Verified trust signals present in source data or existing website",
        "Existing valuable content and functionality",
    ]

    # Evidence-based success criteria - no invented numerical targets
    success_criteria = [
        f"Address identified on-page SEO weaknesses (current: {seo.category_scores.get('On-Page SEO', 'N/A')}/100)",
        "Resolve identified high-severity technical issues",
        f"Address missing meta descriptions ({len([f for f in seo.seo_findings if 'meta' in f.type.lower()])} pages affected)",
        f"Fix title tag issues ({len([f for f in seo.seo_findings if 'title' in f.type.lower()])} pages affected)",
        f"Add missing H1 tags ({len([f for f in seo.seo_findings if 'h1' in f.type.lower()])} pages affected)",
        f"Improve performance issues (current performance score: {seo.category_scores.get('Performance', 'N/A')}/100)",
        f"Represent all verified core services: {', '.join([s.name for s in biz.service_analysis.services if s.importance == 'core'])}",
        "Address identified customer needs from business analysis",
        "Improve navigation to specialized services per business analysis",
        "Preserve existing SEO strengths (Technical SEO, Content Quality, Structured Data, Local SEO)",
        "Preserve all verified business information",
        "Introduce no unsupported claims or fabricated trust signals",
    ]

    all_evidence_ids = []
    for e in biz.evidence:
        all_evidence_ids.append(e.id)

    return StructuredOutput(
        company_name=biz.company_name,
        website=biz.website,
        prompt_type=prompt_type.value,
        source_files={
            "seo_report": seo_report_path,
            "business_analysis": biz_report_path,
        },
        website_summary={
            "url": seo.website_url,
            "overall_score": seo.overall_score,
            "category_scores": seo.category_scores,
            "pages_analyzed": seo.pages_analyzed,
            "strengths": seo.strengths,
            "weaknesses": seo.weaknesses,
        },
        business_summary={
            "company_name": biz.company_name,
            "industry": biz.industry,
            "location": biz.location,
            "primary_services": [s.name for s in biz.service_analysis.services if s.importance == "core"],
            "primary_customers": [s.segment_name for s in biz.customer_analysis.primary_segments],
            "business_score": biz.business_score.get("overall_score", 0),
        },
        identified_problems=identified_problems,
        business_opportunities=business_opportunities,
        recommended_changes=recommended_changes,
        page_plan=page_plan,
        preservation_rules=preservation_rules,
        success_criteria=success_criteria,
        evidence_ids=all_evidence_ids,
        confidence=0.85,
        generated_prompt=generated_prompt,
    )


def extract_clean_prompt(generated: str) -> str:
    """Extract only the 25 clean sections from model output (which may contain thinking)."""
    if not generated:
        return ""
    
    # The 25 required section headers in order - IMPLEMENTATION PROMPT FORMAT
    required_sections = [
        "ROLE",
        "WEBSITE PURPOSE",
        "BUSINESS CONTEXT",
        "TARGET AUDIENCE",
        "WEBSITE GOALS",
        "BRAND DIRECTION",
        "SITE ARCHITECTURE",
        "NAVIGATION",
        "HOMEPAGE",
        "ABOUT PAGE",
        "SERVICE PAGES",
        "CONTACT PAGE",
        "UI DESIGN",
        "UX DESIGN",
        "CONTENT REQUIREMENTS",
        "SEO IMPLEMENTATION",
        "LOCAL SEO",
        "CONVERSION FLOW",
        "MOBILE EXPERIENCE",
        "TRUST ELEMENTS",
        "PRESERVATION RULES",
        "DO NOT INVENT",
        "SUCCESS CRITERIA",
        "FINAL IMPLEMENTATION INSTRUCTION",
    ]
    
    # Find first occurrence of ROLE
    lines = generated.split('\n')
    start_idx = -1
    for i, line in enumerate(lines):
        if line.strip().upper() == "ROLE":
            start_idx = i
            break
    
    if start_idx == -1:
        return ""
    
    # Extract from ROLE onwards
    relevant_lines = lines[start_idx:]
    
    # Build clean output by finding each section
    section_content = {section: [] for section in required_sections}
    current_section = None
    
    for line in relevant_lines:
        line_stripped = line.strip()
        line_upper = line_stripped.upper()
        
        # Check if this line is a section header
        found_section = None
        for section in required_sections:
            if line_upper == section:
                found_section = section
                break
        
        if found_section:
            current_section = found_section
            # Don't include the header in content - we'll add it properly
            continue
        
        if current_section and line_stripped:
            section_content[current_section].append(line.rstrip())
    
    # Build final output
    output_lines = []
    for section in required_sections:
        output_lines.append(section)
        content = section_content.get(section, [])
        if content:
            output_lines.extend(content)
        output_lines.append("")  # blank line after each section
    
    return "\n".join(output_lines).rstrip() + "\n"


def normalize_service_name(name: str) -> str:
    import re
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name