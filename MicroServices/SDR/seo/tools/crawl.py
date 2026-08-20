"""
LibreCrawl Execution Tool for LangGraph Agent
"""

import os
import sys
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from LibreCrawl.engine import crawl_website, validate_url, format_error_result


def crawl_target_tool(
    url: str,
    max_depth: int = 3,
    max_pages: int = 100,
    javascript: bool = False,
    pagespeed: bool = False,
    respect_robots: bool = True,
    discover_sitemaps: bool = True,
    crawl_external: bool = False,
    crawl_images: bool = False,
    delay: float = 0.05,
    concurrency: int = 5,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Executes a headless crawl using LibreCrawl and returns the normalized JSON result.
    """
    is_valid, msg = validate_url(url)
    if not is_valid:
        return format_error_result("INVALID_URL", msg, {"url": url})

    return crawl_website(
        url=url,
        max_depth=max_depth,
        max_pages=max_pages,
        javascript=javascript,
        pagespeed=pagespeed,
        respect_robots=respect_robots,
        discover_sitemaps=discover_sitemaps,
        crawl_external=crawl_external,
        crawl_images=crawl_images,
        delay=delay,
        concurrency=concurrency,
        timeout=timeout
    )
