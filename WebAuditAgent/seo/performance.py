"""
Performance & Speed SEO Analyzer
Evaluates server response times, render latency, and PageSpeed metrics.
"""

from typing import Dict, Any, List
from ..state import CategoryAuditResult, AuditFinding


def run_performance_audit(pages: List[Dict[str, Any]], pagespeed: List[Dict[str, Any]]) -> CategoryAuditResult:
    """Perform performance and speed SEO audit."""
    findings: List[AuditFinding] = []
    deductions = 0

    response_times = [p.get('response_time_ms', 0) for p in pages if p.get('response_time_ms')]
    avg_response = round(sum(response_times) / max(len(response_times), 1), 1)

    # 1. Critical Slow Pages (> 1500ms)
    very_slow_pages = [p for p in pages if (p.get('response_time_ms') or 0) > 1500]
    if very_slow_pages:
        deductions += min(30, len(very_slow_pages) * 10)
        findings.append({
            "category": "Performance",
            "severity": "critical",
            "title": "Severe Server Response Delay (> 1.5s)",
            "description": f"{len(very_slow_pages)} page(s) took longer than 1500ms to respond.",
            "impact": "Drastically increases bounce rate and fails Google Core Web Vitals thresholds.",
            "recommendation": "Optimize database queries, enable server-side caching (Redis/Varnish), and use a CDN.",
            "affected_urls": [p.get('url', '') for p in very_slow_pages[:10]],
            "evidence": {"slow_page_count": len(very_slow_pages), "max_response_ms": max(response_times)}
        })

    # 2. Moderate Slow Pages (500ms - 1500ms)
    moderate_slow = [p for p in pages if 500 < (p.get('response_time_ms') or 0) <= 1500]
    if moderate_slow and not very_slow_pages:
        deductions += min(15, len(moderate_slow) * 3)
        findings.append({
            "category": "Performance",
            "severity": "medium",
            "title": "Sub-optimal Server Response Time (500ms - 1500ms)",
            "description": f"{len(moderate_slow)} page(s) have response times between 500ms and 1500ms.",
            "impact": "Delays Time to First Byte (TTFB), degrading user engagement.",
            "recommendation": "Enable HTTP/2 or HTTP/3, gzip/Brotli compression, and optimize backend API latency.",
            "affected_urls": [p.get('url', '') for p in moderate_slow[:10]],
            "evidence": {"moderate_slow_count": len(moderate_slow)}
        })

    # 3. PageSpeed Insights Scores (if available)
    if pagespeed:
        for ps in pagespeed:
            url = ps.get('url', '')
            mobile = ps.get('mobile', {})
            m_score = mobile.get('performance_score')
            if m_score is not None and m_score < 50:
                deductions += 15
                findings.append({
                    "category": "Performance",
                    "severity": "high",
                    "title": f"Poor PageSpeed Mobile Score ({m_score}/100)",
                    "description": f"Google PageSpeed Insights reported a mobile performance score of {m_score}/100 for {url}.",
                    "impact": "Negative ranking signal for mobile-first indexing and poor mobile conversions.",
                    "recommendation": "Eliminate render-blocking resources, defer non-critical JS/CSS, and compress media.",
                    "affected_urls": [url],
                    "evidence": {"mobile_score": m_score, "desktop_score": ps.get('desktop', {}).get('performance_score')}
                })

    score = max(0, 100 - deductions)
    status = "passed" if score >= 85 else ("warning" if score >= 60 else "failed")
    summary = f"Performance audit analyzed {len(pages)} pages (Average TTFB: {avg_response}ms). Score: {score}/100."

    return {
        "category": "Performance",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "average_response_time_ms": avg_response,
            "slow_pages_count": len(very_slow_pages) + len(moderate_slow)
        }
    }
