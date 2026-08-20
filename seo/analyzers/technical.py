"""
Technical SEO Analyzer
Evaluates crawlability, indexability, status codes, canonicals, and redirects.
"""

from typing import Dict, Any, List
from ..state import CategoryAuditResult, AuditFinding
from . import is_html_page



def run_technical_audit(
    pages: List[Dict[str, Any]],
    links: List[Dict[str, Any]],
    issues: List[Dict[str, Any]],
    sitemaps: Dict[str, Any]
) -> CategoryAuditResult:
    """Perform deterministic technical SEO audit based on collected evidence."""
    findings: List[AuditFinding] = []
    deductions = 0

    # 1. Check HTTP Status Codes (4xx, 5xx)
    server_errors = [p for p in pages if p.get('status_code', 200) >= 500]
    client_errors = [p for p in pages if 400 <= p.get('status_code', 200) < 500]

    if server_errors:
        deductions += min(30, len(server_errors) * 15)
        findings.append({
            "category": "Technical",
            "severity": "critical",
            "title": "5xx Server Errors Detected",
            "description": f"Found {len(server_errors)} page(s) returning 5xx server errors.",
            "impact": "Search engine crawlers cannot index these pages; severe loss of crawl budget and user trust.",
            "recommendation": "Investigate web server error logs, database connections, and application crashes immediately.",
            "affected_urls": [p.get('url', '') for p in server_errors[:10]],
            "evidence": {"server_error_count": len(server_errors)}
        })

    if client_errors:
        deductions += min(20, len(client_errors) * 5)
        findings.append({
            "category": "Technical",
            "severity": "high",
            "title": "4xx Client Errors (Broken Pages)",
            "description": f"Found {len(client_errors)} page(s) returning 4xx status codes.",
            "impact": "Dead links create poor user experience and waste crawl equity.",
            "recommendation": "Update incoming internal links or implement 301 redirects to the relevant destination.",
            "affected_urls": [p.get('url', '') for p in client_errors[:10]],
            "evidence": {"client_error_count": len(client_errors)}
        })

    # 2. Canonical Tag Analysis
    missing_canonicals = [p for p in pages if p.get('status_code') == 200 and is_html_page(p) and not (p.get('canonical') or p.get('canonical_url'))]

    if missing_canonicals:
        deductions += min(15, len(missing_canonicals) * 2)
        findings.append({
            "category": "Technical",
            "severity": "medium",
            "title": "Missing Canonical Tags",
            "description": f"{len(missing_canonicals)} indexable page(s) lack a canonical URL tag.",
            "impact": "Vulnerability to duplicate content penalties if URLs are accessible with query parameters or trailing slashes.",
            "recommendation": "Add a self-referential `<link rel='canonical' href='...' />` tag in the `<head>` of each page.",
            "affected_urls": [p.get('url', '') for p in missing_canonicals[:10]],
            "evidence": {"missing_count": len(missing_canonicals)}
        })

    # 3. Noindex Directive Inspection
    noindex_pages = [p for p in pages if 'noindex' in (p.get('robots') or '').lower()]
    if noindex_pages:
        findings.append({
            "category": "Technical",
            "severity": "info",
            "title": "Noindex Directives Present",
            "description": f"{len(noindex_pages)} page(s) have a 'noindex' directive.",
            "impact": "These pages will be deliberately omitted from search engine result pages.",
            "recommendation": "Verify that no crucial landing pages or revenue-generating content are blocked by noindex tags.",
            "affected_urls": [p.get('url', '') for p in noindex_pages[:10]],
            "evidence": {"noindex_count": len(noindex_pages)}
        })

    # 4. Deep Crawl Depth (>3 clicks)
    deep_pages = [p for p in pages if p.get('depth', 0) > 3]
    if deep_pages:
        deductions += min(10, len(deep_pages) * 2)
        findings.append({
            "category": "Technical",
            "severity": "medium",
            "title": "Excessive Crawl Depth",
            "description": f"{len(deep_pages)} page(s) require more than 3 clicks to reach from the homepage.",
            "impact": "Search crawlers may de-prioritize or fail to discover deeply nested pages regularly.",
            "recommendation": "Improve internal link architecture, add category hub pages, or link directly from navigation.",
            "affected_urls": [p.get('url', '') for p in deep_pages[:10]],
            "evidence": {"deep_pages_count": len(deep_pages)}
        })

    # 5. XML Sitemap Discovery
    discovered_sitemaps = sitemaps.get('discovered', []) if isinstance(sitemaps, dict) else []
    if not discovered_sitemaps:
        deductions += 10
        findings.append({
            "category": "Technical",
            "severity": "medium",
            "title": "No XML Sitemap Discovered",
            "description": "Crawler did not discover a standard sitemap at /sitemap.xml or referenced in robots.txt.",
            "impact": "Search engines may take longer to discover and index new or updated URLs.",
            "recommendation": "Generate an XML sitemap, place it in the root directory, and specify its URL in robots.txt.",
            "affected_urls": [],
            "evidence": {"sitemaps_found": 0}
        })

    score = max(0, 100 - deductions)
    status = "passed" if score >= 85 else ("warning" if score >= 60 else "failed")
    summary = f"Technical audit analyzed {len(pages)} pages and {len(links)} links. Identified {len(findings)} key findings with score {score}/100."

    return {
        "category": "Technical SEO",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "total_pages": len(pages),
            "server_errors": len(server_errors),
            "client_errors": len(client_errors),
            "missing_canonicals": len(missing_canonicals),
            "deep_pages": len(deep_pages),
            "sitemaps_discovered": len(discovered_sitemaps)
        }
    }
