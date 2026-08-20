"""
Content Quality & Depth Analyzer
Evaluates word counts, thin content, duplicate page titles, and topic depth.
"""

from typing import Dict, Any, List
from collections import defaultdict
from ..state import CategoryAuditResult, AuditFinding


from . import is_html_page


def run_content_audit(pages: List[Dict[str, Any]]) -> CategoryAuditResult:
    """Perform content quality and depth audit."""
    findings: List[AuditFinding] = []
    deductions = 0

    indexable_pages = [p for p in pages if p.get('status_code') == 200 and is_html_page(p)]
    total_pages = len(indexable_pages) or 1


    # 1. Thin Content Analysis (< 300 words)
    thin_pages = [p for p in indexable_pages if p.get('word_count', 0) < 300]
    if thin_pages:
        deductions += min(25, len(thin_pages) * 5)
        findings.append({
            "category": "Content",
            "severity": "medium",
            "title": "Thin Content Pages (< 300 words)",
            "description": f"{len(thin_pages)} page(s) have under 300 words of body copy.",
            "impact": "Low-value thin pages struggle to rank for competitive terms and may be devalued by search engines.",
            "recommendation": "Expand thin pages with comprehensive content, FAQs, and multimedia, or consolidate into pillar pages.",
            "affected_urls": [p.get('url', '') for p in thin_pages[:10]],
            "evidence": {"thin_pages_count": len(thin_pages)}
        })

    # 2. Duplicate Titles (Potential Cannibalization)
    title_map = defaultdict(list)
    for p in indexable_pages:
        title = (p.get('title') or '').strip()
        if title:
            title_map[title].append(p.get('url', ''))

    duplicate_titles = {t: urls for t, urls in title_map.items() if len(urls) > 1}
    if duplicate_titles:
        dup_url_count = sum(len(urls) for urls in duplicate_titles.values())
        deductions += min(20, dup_url_count * 4)
        findings.append({
            "category": "Content",
            "severity": "high",
            "title": "Duplicate Page Titles Detected",
            "description": f"{len(duplicate_titles)} title(s) are shared across {dup_url_count} distinct URLs.",
            "impact": "Causes keyword cannibalization and confuses search bots regarding which page to index.",
            "recommendation": "Assign distinct, specific titles reflecting the unique value proposition of each URL.",
            "affected_urls": [url for urls in duplicate_titles.values() for url in urls][:10],
            "evidence": {"duplicate_title_groups": len(duplicate_titles)}
        })

    # 3. Average Word Count Statistics
    word_counts = [p.get('word_count', 0) for p in indexable_pages]
    avg_words = round(sum(word_counts) / max(len(word_counts), 1), 1)

    score = max(0, 100 - deductions)
    status = "passed" if score >= 85 else ("warning" if score >= 60 else "failed")
    summary = f"Content audit evaluated {len(indexable_pages)} pages (Average: {avg_words} words/page). Score: {score}/100."

    return {
        "category": "Content Quality",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "average_word_count": avg_words,
            "thin_pages_count": len(thin_pages),
            "duplicate_title_groups": len(duplicate_titles)
        }
    }
