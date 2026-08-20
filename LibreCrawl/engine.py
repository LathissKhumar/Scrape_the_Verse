"""
LibreCrawl Engine - Programmatic API, Job Management, and Normalization Layer.
Designed for headless execution, LangGraph agent tool integration, and CLI usage.
"""

import os
import sys
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Callable

# Support both package and module level execution
try:
    from src.crawler import WebCrawler
except ImportError:
    try:
        from LibreCrawl.src.crawler import WebCrawler
    except ImportError:
        # If running from a subfolder, add LibreCrawl dir to sys.path
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if cur_dir not in sys.path:
            sys.path.insert(0, cur_dir)
        from src.crawler import WebCrawler


def validate_url(url: str) -> tuple[bool, str]:
    """Validate that the URL has a valid scheme and host."""
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty"
    
    url = url.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "URL must start with http:// or https://"
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "URL must contain a valid domain (e.g. example.com)"
        return True, ""
    except Exception as e:
        return False, f"Malformed URL: {str(e)}"


def format_error_result(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized machine-readable error JSON response."""
    return {
        "status": "failed",
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }


def _derive_issue_type_and_severity(issue_text: str, raw_type: str) -> tuple[str, str]:
    """Map human-readable issue descriptions into normalized machine type keys and severities."""
    text = (issue_text or '').lower()
    raw = (raw_type or '').lower()
    
    # Severity mapping
    severity = "medium"
    if raw in ('error', 'critical') or 'broken' in text or '404' in text or '500' in text:
        severity = "critical" if '500' in text or 'dns' in text else "high"
    elif raw == 'warning' or 'too long' in text or 'too short' in text or 'missing' in text:
        severity = "medium"
    elif raw in ('notice', 'info') or 'schema' in text:
        severity = "low"
    
    # Type key mapping
    if 'missing title' in text:
        return 'missing_title', severity
    elif 'title too long' in text:
        return 'title_too_long', severity
    elif 'title too short' in text:
        return 'title_too_short', severity
    elif 'duplicate title' in text:
        return 'duplicate_title', severity
    elif 'missing meta description' in text:
        return 'missing_meta_description', severity
    elif 'meta description too long' in text:
        return 'meta_description_too_long', severity
    elif 'meta description too short' in text:
        return 'meta_description_too_short', severity
    elif 'duplicate meta description' in text:
        return 'duplicate_meta_description', severity
    elif 'missing h1' in text:
        return 'missing_h1', severity
    elif 'multiple h1' in text:
        return 'multiple_h1', severity
    elif 'duplicate h1' in text:
        return 'duplicate_h1', severity
    elif 'broken image' in text:
        return 'broken_image', 'high'
    elif 'image missing alt' in text or 'missing alt' in text:
        return 'missing_image_alt', severity
    elif 'broken link' in text or '404' in text:
        return 'broken_link', 'high'
    elif 'redirect' in text:
        return 'redirect_detected', severity
    elif 'slow' in text or 'response time' in text:
        return 'slow_response_time', severity
    elif 'canonical' in text:
        return 'canonical_issue', severity
    elif 'noindex' in text or 'robots' in text:
        return 'indexing_restriction', severity
    elif 'mixed content' in text or 'http' in text:
        return 'mixed_content', 'high'
    elif 'viewport' in text or 'mobile' in text:
        return 'missing_viewport', severity
    elif 'thin content' in text or 'low word' in text:
        return 'thin_content', severity
    
    # Generic fallback key
    sanitized = ''.join(c if c.isalnum() else '_' for c in text).strip('_')
    return sanitized or 'general_issue', severity


def normalize_issue(issue_raw: Dict[str, Any], pages_by_url: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Normalize a single issue with evidence."""
    url = issue_raw.get('url', '')
    raw_issue = issue_raw.get('issue', '')
    raw_details = issue_raw.get('details', '')
    raw_type = issue_raw.get('type', 'warning')
    category = issue_raw.get('category', 'SEO')
    
    type_key, severity = _derive_issue_type_and_severity(raw_issue, raw_type)
    
    # Find matching page metadata for evidence
    evidence = {}
    if pages_by_url and url in pages_by_url:
        page = pages_by_url[url]
        if 'title' in type_key:
            evidence = {'title': page.get('title'), 'length': len(page.get('title') or '')}
        elif 'meta_description' in type_key:
            evidence = {'meta_description': page.get('meta_description'), 'length': len(page.get('meta_description') or '')}
        elif 'h1' in type_key:
            evidence = {'h1': page.get('h1')}
        elif 'canonical' in type_key:
            evidence = {'canonical_url': page.get('canonical_url'), 'url': page.get('url')}
        elif 'slow' in type_key:
            evidence = {'response_time_ms': page.get('response_time'), 'render_time_ms': page.get('render_time')}
        elif 'thin' in type_key:
            evidence = {'word_count': page.get('word_count')}
        else:
            evidence = {'status_code': page.get('status_code')}
    
    if not evidence and raw_details:
        evidence = {'details': raw_details}

    return {
        "type": type_key,
        "category": category,
        "severity": severity,
        "url": url,
        "issue": raw_issue,
        "details": raw_details,
        "evidence": evidence
    }


def normalize_page(page_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize crawled page structure into standard JSON schema."""
    h2_list = page_raw.get('h2') or []
    if isinstance(h2_list, str):
        h2_list = [h2_list]
    
    h3_list = page_raw.get('h3') or []
    if isinstance(h3_list, str):
        h3_list = [h3_list]

    return {
        "url": page_raw.get('url', ''),
        "status_code": page_raw.get('status_code', 0),
        "content_type": page_raw.get('content_type', 'text/html'),
        "depth": page_raw.get('depth', 0),
        "response_time_ms": round(float(page_raw.get('response_time') or 0), 2),
        "render_time_ms": round(float(page_raw.get('render_time') or 0), 2) if page_raw.get('render_time') is not None else None,
        "title": page_raw.get('title', '') or '',
        "meta_description": page_raw.get('meta_description', '') or '',
        "h1": page_raw.get('h1', '') or '',
        "h2": h2_list,
        "h3": h3_list,
        "word_count": int(page_raw.get('word_count') or 0),
        "canonical": page_raw.get('canonical_url', '') or '',
        "robots": page_raw.get('robots', '') or '',
        "lang": page_raw.get('lang', '') or '',
        "charset": page_raw.get('charset', '') or '',
        "viewport": page_raw.get('viewport', '') or '',
        "og_tags": page_raw.get('og_tags') or {},
        "twitter_tags": page_raw.get('twitter_tags') or {},
        "json_ld": page_raw.get('json_ld') or [],
        "analytics": page_raw.get('analytics') or {},
        "images": page_raw.get('images') or [],
        "redirects": page_raw.get('redirects') or [],
        "linked_from": page_raw.get('linked_from') or []
    }


def normalize_link(link_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a link structure."""
    return {
        "source_url": link_raw.get('source_url', ''),
        "target_url": link_raw.get('target_url', ''),
        "anchor_text": link_raw.get('anchor_text', '') or '',
        "internal": bool(link_raw.get('is_internal', True)),
        "status_code": link_raw.get('target_status'),
        "target_domain": link_raw.get('target_domain', ''),
        "placement": link_raw.get('placement', 'body')
    }


def normalize_crawl_result(crawler: WebCrawler, duration: float = 0.0, started_at: Optional[str] = None) -> Dict[str, Any]:
    """Produce the complete standardized machine JSON output from a WebCrawler instance."""
    status_data = crawler.get_status()
    raw_urls = status_data.get('urls', [])
    raw_links = status_data.get('links', [])
    raw_issues = status_data.get('issues', [])
    raw_stats = status_data.get('stats', {})

    # Create page lookup map for issue evidence mapping
    pages_by_url = {p.get('url'): p for p in raw_urls if p.get('url')}

    normalized_pages = [normalize_page(p) for p in raw_urls]
    normalized_links = [normalize_link(l) for l in raw_links]
    normalized_issues = [normalize_issue(i, pages_by_url) for i in raw_issues]

    # Sitemap information
    sitemaps_discovered = []
    if hasattr(crawler, 'sitemap_urls') and crawler.sitemap_urls:
        sitemaps_discovered = list(crawler.sitemap_urls)
    elif hasattr(crawler, 'sitemaps') and crawler.sitemaps:
        sitemaps_discovered = list(crawler.sitemaps)
    elif hasattr(crawler, 'sitemap_parser') and crawler.sitemap_parser:
        sitemaps_discovered = list(getattr(crawler.sitemap_parser, 'discovered_sitemaps', []))

    pagespeed_results = raw_stats.get('pagespeed_results') or []

    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "crawl_id": crawler.crawl_id or str(uuid.uuid4()),
        "base_url": crawler.base_url or "",
        "base_domain": crawler.base_domain or (urlparse(crawler.base_url).netloc if crawler.base_url else ""),
        "status": "completed" if not crawler.is_running else "running",
        "summary": {
            "total_pages_crawled": len(normalized_pages),
            "total_pages_discovered": raw_stats.get('discovered', len(normalized_pages)),
            "total_links": len(normalized_links),
            "total_issues": len(normalized_issues),
            "duration_seconds": round(duration, 2),
            "started_at": started_at or now_iso,
            "completed_at": now_iso
        },
        "pages": normalized_pages,
        "links": normalized_links,
        "issues": normalized_issues,
        "sitemaps": {
            "discovered": sitemaps_discovered,
            "urls_found": len(sitemaps_discovered)
        },
        "pagespeed": pagespeed_results
    }


def crawl_website(
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
    timeout: int = 30,
    config_overrides: Optional[Dict[str, Any]] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    poll_interval: float = 0.2
) -> Dict[str, Any]:
    """
    Programmatic entry point to crawl a website in headless mode.
    Returns normalized structured JSON dictionary.
    """
    is_valid, err_msg = validate_url(url)
    if not is_valid:
        return format_error_result("INVALID_URL", err_msg, {"url": url})

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.time()

    try:
        crawler = WebCrawler()
        crawler.config.update({
            'delay': delay,
            'concurrency': concurrency,
            'max_depth': max_depth,
            'max_urls': max_pages,
            'follow_redirects': True,
            'crawl_external': crawl_external,
            'crawl_images': crawl_images,
            'respect_robots': respect_robots,
            'discover_sitemaps': discover_sitemaps,
            'enable_pagespeed': pagespeed,
            'enable_javascript': javascript,
            'timeout': timeout,
            'user_agent': 'LibreCrawl/1.0 (Headless SEO Engine)'
        })

        if config_overrides:
            crawler.config.update(config_overrides)

        ok, message = crawler.start_crawl(url)
        if not ok:
            return format_error_result("CRAWL_START_FAILED", f"Failed to start crawl: {message}", {"url": url})

        # Poll until crawl completes
        while crawler.is_running:
            if progress_callback:
                status_light = crawler.get_status_light()
                progress_callback(status_light)
            time.sleep(poll_interval)

        duration = time.time() - start_time
        result = normalize_crawl_result(crawler, duration=duration, started_at=started_at)
        return result

    except Exception as e:
        return format_error_result(
            "CRAWL_EXECUTION_ERROR",
            f"An unhandled error occurred during crawl execution: {str(e)}",
            {"url": url, "exception_type": type(e).__name__}
        )


class CrawlJob:
    """
    Manages an asynchronous crawl job in the background.
    Useful for long-running crawls or LangGraph tools that query status periodically.
    """

    def __init__(self, job_id: Optional[str] = None):
        self.job_id = job_id or f"crawl_{uuid.uuid4().hex[:10]}"
        self.crawler = WebCrawler(crawl_id=self.job_id)
        self.start_time: Optional[float] = None
        self.started_at: Optional[str] = None
        self.base_url: Optional[str] = None

    def start(
        self,
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
        timeout: int = 30,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str]:
        """Start the crawl in the background."""
        is_valid, err_msg = validate_url(url)
        if not is_valid:
            return False, err_msg

        self.base_url = url
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.start_time = time.time()

        self.crawler.config.update({
            'delay': delay,
            'concurrency': concurrency,
            'max_depth': max_depth,
            'max_urls': max_pages,
            'follow_redirects': True,
            'crawl_external': crawl_external,
            'crawl_images': crawl_images,
            'respect_robots': respect_robots,
            'discover_sitemaps': discover_sitemaps,
            'enable_pagespeed': pagespeed,
            'enable_javascript': javascript,
            'timeout': timeout,
            'user_agent': 'LibreCrawl/1.0 (Headless SEO Engine)'
        })

        if config_overrides:
            self.crawler.config.update(config_overrides)

        ok, msg = self.crawler.start_crawl(url)
        return ok, msg

    def get_status(self) -> Dict[str, Any]:
        """Get the current status and light metrics."""
        status_light = self.crawler.get_status_light()
        elapsed = time.time() - self.start_time if self.start_time else 0.0
        return {
            "job_id": self.job_id,
            "base_url": self.base_url,
            "status": "running" if self.crawler.is_running else ("completed" if self.crawler.stats.get('crawled', 0) > 0 else "idle"),
            "crawled": self.crawler.stats.get('crawled', 0),
            "discovered": status_light.get('stats', {}).get('discovered', 0),
            "progress": status_light.get('progress', 0.0),
            "elapsed_seconds": round(elapsed, 2)
        }

    def get_results(self) -> Dict[str, Any]:
        """Retrieve full normalized JSON results."""
        duration = time.time() - self.start_time if self.start_time else 0.0
        return normalize_crawl_result(self.crawler, duration=duration, started_at=self.started_at)

    def stop(self) -> tuple[bool, str]:
        """Stop the running crawl."""
        return self.crawler.stop_crawl()
