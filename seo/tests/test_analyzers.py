"""
Unit Tests for SEO Domain Analyzers
Tests technical, on-page, content, schema, local, and performance analyzers.
"""

import pytest
from seo.analyzers.technical import run_technical_audit
from seo.analyzers.onpage import run_onpage_audit
from seo.analyzers.content import run_content_audit
from seo.analyzers.schema import run_schema_audit
from seo.analyzers.local import run_local_audit
from seo.analyzers.performance import run_performance_audit


def test_technical_audit(sample_pages, sample_links, sample_issues, sample_sitemaps):
    """Verify technical audit detects 4xx errors, missing canonicals, deep crawl depth, and sitemaps."""
    result = run_technical_audit(sample_pages, sample_links, sample_issues, sample_sitemaps)

    assert result["category"] == "Technical SEO"
    assert 0 <= result["score"] <= 100
    assert result["status"] in ("passed", "warning", "failed")
    assert len(result["findings"]) > 0

    finding_titles = [f["title"] for f in result["findings"]]
    # Should detect 4xx error on old-page
    assert any("4xx Client Errors" in t for t in finding_titles)
    # Should detect missing canonical on about page
    assert any("Missing Canonical Tags" in t for t in finding_titles)
    # Should detect deep crawl depth on nested product page
    assert any("Excessive Crawl Depth" in t for t in finding_titles)


def test_onpage_audit(sample_pages, sample_issues):
    """Verify on-page audit identifies short titles, long titles, missing H1, and missing alt text."""
    result = run_onpage_audit(sample_pages, sample_issues)

    assert result["category"] == "On-Page SEO"
    assert 0 <= result["score"] <= 100

    finding_titles = [f["title"] for f in result["findings"]]
    assert any("Title Tags Too Short" in t for t in finding_titles)
    assert any("Title Tags Truncated" in t for t in finding_titles)
    assert any("Missing H1 Headings" in t for t in finding_titles)
    assert any("Images Missing Alt Text" in t for t in finding_titles)


def test_content_audit(sample_pages):
    """Verify content audit detects thin content pages and calculates average word count."""
    result = run_content_audit(sample_pages)

    assert result["category"] == "Content Quality"
    assert result["metrics"]["thin_pages_count"] >= 1
    assert result["metrics"]["average_word_count"] > 0

    finding_titles = [f["title"] for f in result["findings"]]
    assert any("Thin Content" in t for t in finding_titles)


def test_schema_audit(sample_pages):
    """Verify schema audit identifies Organization markup and reports coverage ratio."""
    result = run_schema_audit(sample_pages)

    assert result["category"] == "Structured Data"
    assert result["metrics"]["pages_with_schema"] >= 1
    assert "Organization" in result["metrics"]["schema_types_found"]


def test_local_audit(sample_pages):
    """Verify local SEO audit executes and evaluates LocalBusiness schema."""
    result = run_local_audit(sample_pages)

    assert result["category"] == "Local SEO"
    assert "has_local_schema" in result["metrics"]


def test_performance_audit(sample_pages):
    """Verify performance audit flags pages exceeding the 1.5s response threshold."""
    result = run_performance_audit(sample_pages, pagespeed=[])

    assert result["category"] == "Performance"
    assert result["metrics"]["slow_pages_count"] >= 1

    finding_titles = [f["title"] for f in result["findings"]]
    assert any("Severe Server Response Delay" in t for t in finding_titles)
