"""
Crawled Pages Analysis Tool
"""

from typing import List, Dict, Any
from collections import defaultdict


def get_pages_by_status_tool(pages: List[Dict[str, Any]], status_code: int) -> List[Dict[str, Any]]:
    """Return all pages matching a specific HTTP status code."""
    return [p for p in pages if p.get('status_code') == status_code]


def find_meta_issues_tool(pages: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Identify pages with missing or improper title tags and meta descriptions."""
    missing_title = []
    short_title = []
    long_title = []
    missing_desc = []
    short_desc = []
    long_desc = []
    missing_h1 = []

    for p in pages:
        url = p.get('url', '')
        title = (p.get('title') or '').strip()
        desc = (p.get('meta_description') or '').strip()
        h1 = (p.get('h1') or '').strip()

        if not title:
            missing_title.append(url)
        elif len(title) < 30:
            short_title.append(url)
        elif len(title) > 60:
            long_title.append(url)

        if not desc:
            missing_desc.append(url)
        elif len(desc) < 120:
            short_desc.append(url)
        elif len(desc) > 160:
            long_desc.append(url)

        if not h1:
            missing_h1.append(url)

    return {
        "missing_title": missing_title,
        "short_title": short_title,
        "long_title": long_title,
        "missing_description": missing_desc,
        "short_description": short_desc,
        "long_description": long_desc,
        "missing_h1": missing_h1
    }


def find_duplicate_titles_tool(pages: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Identify duplicate title tags across multiple pages."""
    title_to_urls = defaultdict(list)
    for p in pages:
        title = (p.get('title') or '').strip()
        if title:
            title_to_urls[title].append(p.get('url', ''))
    
    return {title: urls for title, urls in title_to_urls.items() if len(urls) > 1}
