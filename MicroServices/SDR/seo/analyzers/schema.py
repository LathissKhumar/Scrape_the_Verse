"""
Structured Data & Schema.org Analyzer
Evaluates JSON-LD and Microdata markup across crawled pages.
"""

import json
from typing import Any

from ..state import AuditFinding, CategoryAuditResult
from . import is_html_page


def run_schema_audit(pages: list[dict[str, Any]]) -> CategoryAuditResult:
    """Perform schema.org structured data audit."""
    findings: list[AuditFinding] = []
    deductions = 0

    indexable_pages = [
        p for p in pages if p.get("status_code") == 200 and is_html_page(p)
    ]

    pages_with_schema = []
    schema_types_found = set()

    for p in indexable_pages:
        json_ld_list = p.get("json_ld") or []
        if json_ld_list:
            pages_with_schema.append(p.get("url", ""))
            for item in json_ld_list:
                if isinstance(item, dict):
                    stype = item.get("@type")
                    if stype:
                        if isinstance(stype, list):
                            schema_types_found.update(stype)
                        else:
                            schema_types_found.add(str(stype))
                elif isinstance(item, str):
                    try:
                        parsed = json.loads(item)
                        if isinstance(parsed, dict) and "@type" in parsed:
                            schema_types_found.add(str(parsed["@type"]))
                    except Exception:
                        pass

    # 1. Total Schema Coverage
    coverage_ratio = len(pages_with_schema) / max(len(indexable_pages), 1)
    if not pages_with_schema:
        deductions += 25
        findings.append(
            {
                "category": "Schema",
                "severity": "medium",
                "title": "No Structured Data (Schema.org) Detected",
                "description": "None of the crawled pages contain JSON-LD or Microdata structured data.",
                "impact": "Misses opportunities for Google Rich Snippets (Star Ratings, Breadcrumbs, FAQs, Sitename).",
                "recommendation": "Implement JSON-LD structured data (e.g. Organization, WebSite, BreadcrumbList) in the `<head>`.",
                "affected_urls": [p.get("url", "") for p in indexable_pages[:10]],
                "evidence": {"schema_coverage_percent": 0},
            }
        )
    elif coverage_ratio < 0.5:
        deductions += 10
        findings.append(
            {
                "category": "Schema",
                "severity": "low",
                "title": "Incomplete Structured Data Coverage",
                "description": f"Only {len(pages_with_schema)} of {len(indexable_pages)} pages ({round(coverage_ratio * 100)}%) contain structured data.",
                "impact": "Inconsistent rich snippet eligibility across landing pages.",
                "recommendation": "Standardize JSON-LD templates across all page layouts.",
                "affected_urls": [
                    p.get("url", "")
                    for p in indexable_pages
                    if p.get("url") not in pages_with_schema
                ][:10],
                "evidence": {"schema_coverage_percent": round(coverage_ratio * 100, 1)},
            }
        )

    # 2. Check for Essential Base Schemas
    essential_types = {"Organization", "WebSite", "Corporation", "LocalBusiness"}
    if pages_with_schema and not (schema_types_found & essential_types):
        deductions += 10
        findings.append(
            {
                "category": "Schema",
                "severity": "low",
                "title": "Missing Brand / Organization Schema",
                "description": "No Organization or WebSite schema was detected on the root pages.",
                "impact": "Limits Google Knowledge Graph and official brand entity association.",
                "recommendation": "Add Organization schema on the homepage detailing company name, logo, social profiles, and contact points.",
                "affected_urls": pages_with_schema[:5],
                "evidence": {"detected_types": list(schema_types_found)},
            }
        )

    score = max(0, 100 - deductions)
    status = "passed" if score >= 85 else ("warning" if score >= 60 else "failed")
    summary = f"Schema audit identified {len(schema_types_found)} schema types across {len(pages_with_schema)} pages. Score: {score}/100."

    return {
        "category": "Structured Data",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "pages_with_schema": len(pages_with_schema),
            "schema_coverage_percent": round(coverage_ratio * 100, 1),
            "schema_types_found": list(schema_types_found),
        },
    }
