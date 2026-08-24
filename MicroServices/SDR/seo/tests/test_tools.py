"""
Unit Tests for SEO Agent Tools
Tests issue filtering, page analysis, link graph analysis, and performance tools.
"""

from seo.tools.issues import filter_issues_tool, get_issue_summary_tool
from seo.tools.links import analyze_link_graph_tool, find_broken_links_tool
from seo.tools.pages import (
    find_duplicate_titles_tool,
    find_meta_issues_tool,
    get_pages_by_status_tool,
)
from seo.tools.performance import analyze_performance_tool


def test_issues_tools(sample_issues):
    """Test issue filtering by category/severity and issue summary metrics."""
    high_issues = filter_issues_tool(sample_issues, severity="high")
    assert len(high_issues) == 2

    seo_issues = filter_issues_tool(sample_issues, category="SEO")
    assert len(seo_issues) == 2

    summary = get_issue_summary_tool(sample_issues)
    assert summary["total_issues"] == len(sample_issues)
    assert "by_severity" in summary
    assert summary["by_severity"]["critical"] == 1


def test_pages_tools(sample_pages):
    """Test page status filtering, meta issue detection, and duplicate title finder."""
    p_200 = get_pages_by_status_tool(sample_pages, 200)
    assert len(p_200) == 3

    p_404 = get_pages_by_status_tool(sample_pages, 404)
    assert len(p_404) == 1

    meta_issues = find_meta_issues_tool(sample_pages)
    assert len(meta_issues["short_title"]) >= 1
    assert len(meta_issues["missing_description"]) >= 1
    assert len(meta_issues["missing_h1"]) >= 1

    dup_titles = find_duplicate_titles_tool(sample_pages)
    assert isinstance(dup_titles, dict)


def test_links_tools(sample_pages, sample_links):
    """Test broken link detection and link graph distribution."""
    broken = find_broken_links_tool(sample_links)
    assert len(broken) == 1
    assert broken[0]["status_code"] == 404

    graph = analyze_link_graph_tool(sample_pages, sample_links)
    assert graph["total_links"] == len(sample_links)
    assert graph["internal_links"] == 3
    assert graph["external_links"] == 1


def test_performance_tools(sample_pages):
    """Test response time calculation and slow page detection."""
    perf = analyze_performance_tool(sample_pages, slow_threshold_ms=1000.0)
    assert perf["total_analyzed_pages"] == len(sample_pages)
    assert perf["slow_pages_count"] == 1
    assert perf["max_response_time_ms"] >= 1800.0
