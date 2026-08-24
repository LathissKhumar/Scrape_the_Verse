"""
Dual Data Models (Phase 3)
Provides distinct, strictly validated data structures:
- PageRecord: Strictly for HTML documents (contains title, meta, headings, canonical, schema, etc.)
- ResourceRecord: For non-HTML assets (images, PDFs, CSS, JS, fonts, videos, audio)

Ensures image-like or asset documents are NEVER represented as HTML pages.
"""

from typing import Any

from .resource_classifier import ResourceClassifier


def create_page_record(
    url: str,
    status_code: int = 200,
    content_type: str = "text/html",
    depth: int = 0,
    response_time_ms: float = 0.0,
    title: str = "",
    meta_description: str = "",
    h1: str = "",
    h2: list[str] | None = None,
    h3: list[str] | None = None,
    word_count: int = 0,
    canonical_url: str = "",
    robots: str = "",
    lang: str = "",
    charset: str = "",
    viewport: str = "",
    og_tags: dict[str, Any] | None = None,
    twitter_tags: dict[str, Any] | None = None,
    json_ld: list[dict[str, Any]] | None = None,
    analytics: dict[str, Any] | None = None,
    images: list[dict[str, Any]] | None = None,
    redirects: list[dict[str, Any]] | None = None,
    linked_from: list[str] | None = None,
    **extra_kwargs,
) -> dict[str, Any]:
    """
    Constructs a normalized PageRecord dictionary for HTML pages.
    """
    classification = ResourceClassifier.classify_resource(
        url, content_type, is_html_parsed=True
    )

    record = {
        "url": url,
        "resource_type": "html",
        "is_html_document": True,
        "is_indexable_document": True,
        "is_seo_page": True,
        "status_code": status_code,
        "content_type": content_type or "text/html",
        "depth": depth,
        "response_time_ms": response_time_ms,
        "title": title or "",
        "meta_description": meta_description or "",
        "h1": h1 or "",
        "h2": h2 if isinstance(h2, list) else [],
        "h3": h3 if isinstance(h3, list) else [],
        "word_count": word_count or 0,
        "canonical_url": canonical_url or "",
        "robots": robots or "",
        "lang": lang or "",
        "charset": charset or "",
        "viewport": viewport or "",
        "og_tags": og_tags if isinstance(og_tags, dict) else {},
        "twitter_tags": twitter_tags if isinstance(twitter_tags, dict) else {},
        "json_ld": json_ld if isinstance(json_ld, list) else [],
        "analytics": analytics if isinstance(analytics, dict) else {},
        "images": images if isinstance(images, list) else [],
        "redirects": redirects if isinstance(redirects, list) else [],
        "linked_from": linked_from if isinstance(linked_from, list) else [],
    }

    # Add extra metadata without overwriting standard fields
    for k, v in extra_kwargs.items():
        if k not in record:
            record[k] = v

    return record


def create_resource_record(
    url: str,
    status_code: int = 200,
    content_type: str = "",
    size_bytes: int = 0,
    response_time_ms: float = 0.0,
    depth: int = 0,
    linked_from: list[str] | None = None,
    **extra_kwargs,
) -> dict[str, Any]:
    """
    Constructs a normalized ResourceRecord dictionary for non-HTML assets (images, PDFs, CSS, JS, etc.).
    Note: Does NOT contain title, meta_description, h1, canonical, schema, etc.
    """
    classification = ResourceClassifier.classify_resource(url, content_type)

    record = {
        "url": url,
        "resource_type": classification["resource_type"],
        "is_html_document": False,
        "is_indexable_document": classification["is_indexable_document"],
        "is_seo_page": False,
        "status_code": status_code,
        "content_type": content_type or classification["content_type"],
        "size_bytes": size_bytes or 0,
        "response_time_ms": response_time_ms,
        "depth": depth,
        "linked_from": linked_from if isinstance(linked_from, list) else [],
    }

    for k, v in extra_kwargs.items():
        if k not in record:
            record[k] = v

    return record
