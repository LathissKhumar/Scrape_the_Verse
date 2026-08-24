"""
On-Page SEO Analyzer
Evaluates titles, meta descriptions, headings (H1-H6), image alt attributes, and social tags.
"""

from typing import Any

from ..state import AuditFinding, CategoryAuditResult
from . import is_html_page


def run_onpage_audit(
    pages: list[dict[str, Any]], issues: list[dict[str, Any]]
) -> CategoryAuditResult:
    """Perform deterministic on-page SEO audit."""
    findings: list[AuditFinding] = []
    deductions = 0

    indexable_pages = [
        p for p in pages if p.get("status_code") == 200 and is_html_page(p)
    ]

    total_indexable = len(indexable_pages) or 1

    # 1. Title Tag Audits
    missing_titles = [p for p in indexable_pages if not (p.get("title") or "").strip()]
    short_titles = [
        p
        for p in indexable_pages
        if (p.get("title") or "").strip() and len(p.get("title", "").strip()) < 30
    ]
    long_titles = [
        p for p in indexable_pages if len((p.get("title") or "").strip()) > 60
    ]

    if missing_titles:
        deductions += min(25, len(missing_titles) * 10)
        findings.append(
            {
                "category": "On-Page",
                "severity": "critical",
                "title": "Missing Title Tags",
                "description": f"{len(missing_titles)} page(s) lack a `<title>` tag.",
                "impact": "Title tags are the primary on-page signal for relevance in SERP snippets.",
                "recommendation": "Provide unique, compelling title tags between 50-60 characters for all pages.",
                "affected_urls": [p.get("url", "") for p in missing_titles[:10]],
                "evidence": {"missing_title_count": len(missing_titles)},
            }
        )

    if short_titles:
        deductions += min(10, len(short_titles) * 2)
        findings.append(
            {
                "category": "On-Page",
                "severity": "low",
                "title": "Title Tags Too Short",
                "description": f"{len(short_titles)} page(s) have title tags under 30 characters.",
                "impact": "Missed opportunity to target relevant primary and secondary keyword variations.",
                "recommendation": "Expand titles to 50-60 characters incorporating brand and target topic.",
                "affected_urls": [p.get("url", "") for p in short_titles[:10]],
                "evidence": {"short_title_count": len(short_titles)},
            }
        )

    if long_titles:
        deductions += min(10, len(long_titles) * 2)
        findings.append(
            {
                "category": "On-Page",
                "severity": "medium",
                "title": "Title Tags Truncated in SERP (>60 chars)",
                "description": f"{len(long_titles)} page(s) have title tags exceeding 60 characters.",
                "impact": "Search engines will truncate the title with ellipses ('...'), reducing click-through rates.",
                "recommendation": "Trim title tags to 50-60 characters and move primary keywords to the beginning.",
                "affected_urls": [p.get("url", "") for p in long_titles[:10]],
                "evidence": {"long_title_count": len(long_titles)},
            }
        )

    # 2. Meta Description Audits
    missing_desc = [
        p for p in indexable_pages if not (p.get("meta_description") or "").strip()
    ]
    if missing_desc:
        deductions += min(20, len(missing_desc) * 3)
        findings.append(
            {
                "category": "On-Page",
                "severity": "medium",
                "title": "Missing Meta Descriptions",
                "description": f"{len(missing_desc)} page(s) have no meta description.",
                "impact": "Search engines will generate arbitrary text snippets from page content, hurting SERP CTR.",
                "recommendation": "Write unique, persuasive meta descriptions (120-160 characters) with a clear call to action.",
                "affected_urls": [p.get("url", "") for p in missing_desc[:10]],
                "evidence": {"missing_description_count": len(missing_desc)},
            }
        )

    # 3. Heading (H1) Audits
    missing_h1 = [p for p in indexable_pages if not (p.get("h1") or "").strip()]
    if missing_h1:
        deductions += min(15, len(missing_h1) * 3)
        findings.append(
            {
                "category": "On-Page",
                "severity": "high",
                "title": "Missing H1 Headings",
                "description": f"{len(missing_h1)} page(s) are missing a main `<h1>` heading tag.",
                "impact": "Users and search engines rely on H1 to understand the primary topic of the page.",
                "recommendation": "Ensure every page has exactly one descriptive `<h1>` matching the page intent.",
                "affected_urls": [p.get("url", "") for p in missing_h1[:10]],
                "evidence": {"missing_h1_count": len(missing_h1)},
            }
        )

    # 4. Image Alt Attributes
    images_missing_alt = 0
    pages_with_alt_issues = []
    for p in indexable_pages:
        imgs = p.get("images") or []
        unlabeled = [
            img
            for img in imgs
            if isinstance(img, dict) and not (img.get("alt") or "").strip()
        ]
        if unlabeled:
            images_missing_alt += len(unlabeled)
            pages_with_alt_issues.append(p.get("url", ""))

    if images_missing_alt > 0:
        deductions += min(15, images_missing_alt * 2)
        findings.append(
            {
                "category": "On-Page",
                "severity": "medium",
                "title": "Images Missing Alt Text",
                "description": f"Detected {images_missing_alt} image(s) lacking descriptive alt attributes across {len(pages_with_alt_issues)} page(s).",
                "impact": "Harms accessibility (screen readers) and prevents images from indexing in Google Image search.",
                "recommendation": "Add meaningful `alt='...'` descriptions to all informational images.",
                "affected_urls": pages_with_alt_issues[:10],
                "evidence": {"images_missing_alt": images_missing_alt},
            }
        )

    # 5. OpenGraph & Social Metadata
    pages_missing_og = [p for p in indexable_pages if not p.get("og_tags")]
    if pages_missing_og and len(pages_missing_og) == len(indexable_pages):
        deductions += 10
        findings.append(
            {
                "category": "On-Page",
                "severity": "low",
                "title": "Missing OpenGraph Metadata",
                "description": "Pages lack `og:title`, `og:description`, and `og:image` tags for social sharing previews.",
                "impact": "Links shared on Twitter, LinkedIn, Slack, and Facebook will display unoptimized generic cards.",
                "recommendation": "Implement OpenGraph meta tags on all public landing pages and articles.",
                "affected_urls": [p.get("url", "") for p in pages_missing_og[:10]],
                "evidence": {"missing_og_count": len(pages_missing_og)},
            }
        )

    score = max(0, 100 - deductions)
    status = "passed" if score >= 85 else ("warning" if score >= 60 else "failed")
    summary = f"On-page audit inspected {len(indexable_pages)} indexable pages. Discovered {len(findings)} issues with score {score}/100."

    return {
        "category": "On-Page SEO",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "indexable_pages": len(indexable_pages),
            "missing_titles": len(missing_titles),
            "missing_meta_descriptions": len(missing_desc),
            "missing_h1": len(missing_h1),
            "images_missing_alt": images_missing_alt,
        },
    }
