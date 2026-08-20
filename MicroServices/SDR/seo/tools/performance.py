"""
Performance & Core Web Vitals Analysis Tool
"""

from typing import List, Dict, Any, Optional


def analyze_performance_tool(
    pages: List[Dict[str, Any]],
    pagespeed_data: Optional[List[Dict[str, Any]]] = None,
    slow_threshold_ms: float = 1000.0
) -> Dict[str, Any]:
    """Analyze server response times, render delays, and PageSpeed metrics."""
    response_times = [p.get('response_time_ms', 0) for p in pages if p.get('response_time_ms')]
    avg_response_time = round(sum(response_times) / max(len(response_times), 1), 2)
    max_response_time = max(response_times) if response_times else 0.0

    slow_pages = [
        {"url": p.get('url'), "response_time_ms": p.get('response_time_ms')}
        for p in pages
        if p.get('response_time_ms', 0) > slow_threshold_ms
    ]

    js_rendered_pages = [
        {
            "url": p.get('url'),
            "response_time_ms": p.get('response_time_ms'),
            "render_time_ms": p.get('render_time_ms')
        }
        for p in pages
        if p.get('render_time_ms') is not None
    ]

    return {
        "total_analyzed_pages": len(pages),
        "average_response_time_ms": avg_response_time,
        "max_response_time_ms": max_response_time,
        "slow_pages_count": len(slow_pages),
        "slow_pages": slow_pages[:10],
        "js_rendered_pages_count": len(js_rendered_pages),
        "pagespeed_insights": pagespeed_data or []
    }
