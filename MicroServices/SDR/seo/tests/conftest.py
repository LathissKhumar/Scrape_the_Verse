"""
Pytest Fixtures for SEO Agent Tests
Provides standard sample crawl payloads, pages, links, and issues for testing.
"""

import os
import sys

# Ensure workspace root (for LibreCrawl) and WebAuditAgent (for seo) are importable
_tests_dir = os.path.dirname(os.path.abspath(__file__))         # .../WebAuditAgent/seo/tests
_seo_dir = os.path.dirname(_tests_dir)                          # .../WebAuditAgent/seo
_webaudit_dir = os.path.dirname(_seo_dir)                       # .../WebAuditAgent
_workspace_root = os.path.dirname(_webaudit_dir)                # .../Scrape_the_Verse
for _p in (_webaudit_dir, _workspace_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from typing import List, Dict, Any



@pytest.fixture
def sample_pages() -> List[Dict[str, Any]]:
    """Returns a list of crawled pages representing both healthy and problematic SEO states."""
    return [
        {
            "url": "https://example.com/",
            "status_code": 200,
            "content_type": "text/html",
            "depth": 0,
            "response_time_ms": 150.0,
            "render_time_ms": None,
            "title": "Example Brand - Enterprise Data Solutions",
            "meta_description": "Discover high-performance enterprise data extraction and analytics software built for scaling digital operations.",
            "h1": "Enterprise Data Solutions",
            "h2": ["Why Choose Us", "Key Capabilities", "Customer Success Stories"],
            "h3": ["Scalability", "Security"],
            "word_count": 850,
            "canonical": "https://example.com/",
            "robots": "index, follow",
            "lang": "en",
            "charset": "utf-8",
            "viewport": "width=device-width, initial-scale=1",
            "og_tags": {"title": "Example Brand", "type": "website"},
            "twitter_tags": {"card": "summary_large_image"},
            "json_ld": [{"@type": "Organization", "name": "Example Corp", "url": "https://example.com"}],
            "analytics": {"ga4_id": "G-12345"},
            "images": [{"src": "/logo.png", "alt": "Example Corp Logo"}],
            "redirects": [],
            "linked_from": []
        },
        {
            "url": "https://example.com/about",
            "status_code": 200,
            "content_type": "text/html",
            "depth": 1,
            "response_time_ms": 220.0,
            "render_time_ms": None,
            "title": "About Us",  # Short title (<30)
            "meta_description": "",  # Missing meta description
            "h1": "",  # Missing H1
            "h2": ["Our Team"],
            "h3": [],
            "word_count": 120,  # Thin content (<300)
            "canonical": "",  # Missing canonical
            "robots": "index, follow",
            "lang": "en",
            "charset": "utf-8",
            "viewport": "width=device-width, initial-scale=1",
            "og_tags": {},
            "twitter_tags": {},
            "json_ld": [],
            "analytics": {},
            "images": [{"src": "/team.jpg", "alt": ""}],  # Missing alt
            "redirects": [],
            "linked_from": ["https://example.com/"]
        },
        {
            "url": "https://example.com/products/very-deeply-nested-item",
            "status_code": 200,
            "content_type": "text/html",
            "depth": 4,  # Deep crawl depth (>3)
            "response_time_ms": 1800.0,  # Severe slow page (>1500ms)
            "render_time_ms": None,
            "title": "Product Title That Exceeds The Recommended Character Limit For Search Engine Result Snippets",  # Long title (>60)
            "meta_description": "A very short description",  # Short meta description (<120)
            "h1": "Product Specification",
            "h2": ["Features"],
            "h3": [],
            "word_count": 600,
            "canonical": "https://example.com/products/very-deeply-nested-item",
            "robots": "noindex, follow",  # Noindex directive
            "lang": "en",
            "charset": "utf-8",
            "viewport": "",
            "og_tags": {},
            "twitter_tags": {},
            "json_ld": [],
            "analytics": {},
            "images": [],
            "redirects": [],
            "linked_from": ["https://example.com/about"]
        },
        {
            "url": "https://example.com/old-page",
            "status_code": 404,  # Client error
            "content_type": "text/html",
            "depth": 1,
            "response_time_ms": 90.0,
            "render_time_ms": None,
            "title": "404 Not Found",
            "meta_description": "",
            "h1": "Page Not Found",
            "h2": [],
            "h3": [],
            "word_count": 20,
            "canonical": "",
            "robots": "noindex, nofollow",
            "lang": "en",
            "charset": "utf-8",
            "viewport": "width=device-width, initial-scale=1",
            "og_tags": {},
            "twitter_tags": {},
            "json_ld": [],
            "analytics": {},
            "images": [],
            "redirects": [],
            "linked_from": ["https://example.com/"]
        }
    ]


@pytest.fixture
def sample_links() -> List[Dict[str, Any]]:
    """Returns sample link graph records."""
    return [
        {
            "source_url": "https://example.com/",
            "target_url": "https://example.com/about",
            "anchor_text": "About Us",
            "internal": True,
            "status_code": 200,
            "target_domain": "example.com",
            "placement": "header"
        },
        {
            "source_url": "https://example.com/",
            "target_url": "https://example.com/old-page",
            "anchor_text": "Legacy Documentation",
            "internal": True,
            "status_code": 404,
            "target_domain": "example.com",
            "placement": "footer"
        },
        {
            "source_url": "https://example.com/about",
            "target_url": "https://example.com/products/very-deeply-nested-item",
            "anchor_text": "View Product",
            "internal": True,
            "status_code": 200,
            "target_domain": "example.com",
            "placement": "body"
        },
        {
            "source_url": "https://example.com/",
            "target_url": "https://twitter.com/example",
            "anchor_text": "Twitter",
            "internal": False,
            "status_code": 200,
            "target_domain": "twitter.com",
            "placement": "footer"
        }
    ]


@pytest.fixture
def sample_issues() -> List[Dict[str, Any]]:
    """Returns sample issue evidence list."""
    return [
        {
            "type": "missing_meta_description",
            "category": "SEO",
            "severity": "medium",
            "url": "https://example.com/about",
            "issue": "Missing Meta Description",
            "details": "Page has no meta description",
            "evidence": {"meta_description": None}
        },
        {
            "type": "missing_h1",
            "category": "SEO",
            "severity": "high",
            "url": "https://example.com/about",
            "issue": "Missing H1 Tag",
            "details": "Page has no H1 heading",
            "evidence": {"h1": None}
        },
        {
            "type": "broken_link",
            "category": "Technical",
            "severity": "high",
            "url": "https://example.com/old-page",
            "issue": "404 Page Not Found",
            "details": "URL returned HTTP 404 status",
            "evidence": {"status_code": 404}
        },
        {
            "type": "slow_response_time",
            "category": "Performance",
            "severity": "critical",
            "url": "https://example.com/products/very-deeply-nested-item",
            "issue": "Slow Server Response",
            "details": "Response time 1800ms exceeds threshold",
            "evidence": {"response_time_ms": 1800.0}
        }
    ]


@pytest.fixture
def sample_sitemaps() -> Dict[str, Any]:
    """Returns sample sitemap metadata."""
    return {
        "discovered": ["https://example.com/sitemap.xml"],
        "urls_found": 3
    }
