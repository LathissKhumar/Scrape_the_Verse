"""
Link Graph Analysis Tool
"""

from typing import List, Dict, Any, Set
from collections import defaultdict


def find_broken_links_tool(links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return all links that returned 4xx or 5xx HTTP status codes."""
    broken = []
    for link in links:
        status = link.get('status_code')
        if status and isinstance(status, int) and status >= 400:
            broken.append(link)
    return broken


def analyze_link_graph_tool(pages: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate link distribution metrics, orphan pages, and in-degree counts."""
    crawled_urls: Set[str] = {p.get('url') for p in pages if p.get('url')}
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    internal_count = 0
    external_count = 0

    for link in links:
        src = link.get('source_url', '')
        tgt = link.get('target_url', '')
        is_int = link.get('internal', True)

        if is_int:
            internal_count += 1
            in_degree[tgt] += 1
            out_degree[src] += 1
        else:
            external_count += 1

    # Orphan pages: internal pages that have 0 incoming internal links (excluding root/homepage)
    orphan_pages = []
    for p in pages:
        url = p.get('url', '')
        depth = p.get('depth', 0)
        if depth > 0 and in_degree[url] == 0:
            orphan_pages.append(url)

    return {
        "total_links": len(links),
        "internal_links": internal_count,
        "external_links": external_count,
        "orphan_pages_count": len(orphan_pages),
        "orphan_pages": orphan_pages[:20],
        "top_linked_pages": sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:10]
    }
