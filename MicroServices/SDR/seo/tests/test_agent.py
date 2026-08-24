"""
Integration Tests for SEO Agent Pipeline
Tests LangGraph StateGraph compilation, node synthesis, and full workflow.
"""

import os

from seo.seo_agent import create_seo_agent, synthesis_node
from seo.state import SEOState


def test_agent_graph_compilation():
    """Verify that the LangGraph StateGraph compiles cleanly without schema errors."""
    agent = create_seo_agent()
    assert agent is not None
    assert hasattr(agent, "invoke")


def test_synthesis_node(sample_pages, sample_links, sample_issues, sample_sitemaps):
    """Verify synthesis node accurately calculates overall score and ranks priority action items."""
    from seo.analyzers.content import run_content_audit
    from seo.analyzers.local import run_local_audit
    from seo.analyzers.onpage import run_onpage_audit
    from seo.analyzers.performance import run_performance_audit
    from seo.analyzers.schema import run_schema_audit
    from seo.analyzers.technical import run_technical_audit

    # Populate state with analyzer results
    state: SEOState = {
        "url": "https://example.com",
        "status": "analyzing",
        "pages": sample_pages,
        "links": sample_links,
        "issues": sample_issues,
        "sitemaps": sample_sitemaps,
        "crawl_summary": {
            "total_pages_crawled": len(sample_pages),
            "total_links": len(sample_links),
            "duration_seconds": 2.5,
        },
        "technical_audit": run_technical_audit(
            sample_pages, sample_links, sample_issues, sample_sitemaps
        ),
        "onpage_audit": run_onpage_audit(sample_pages, sample_issues),
        "content_audit": run_content_audit(sample_pages),
        "schema_audit": run_schema_audit(sample_pages),
        "local_audit": run_local_audit(sample_pages),
        "performance_audit": run_performance_audit(sample_pages, pagespeed=[]),
    }

    final_state = synthesis_node(state)

    assert final_state["status"] == "completed"
    assert "overall_seo_score" in final_state
    assert 0 <= final_state["overall_seo_score"] <= 100
    assert len(final_state["priority_action_items"]) > 0

    # Ensure action items are properly sorted by priority (Priority 1 first)
    priorities = [item["priority"] for item in final_state["priority_action_items"]]
    assert priorities == sorted(priorities)

    # Verify Markdown report generation
    assert "# SEO Audit Report" in final_state["detailed_report_markdown"]
    assert "Category Scores" in final_state["detailed_report_markdown"]
    assert "Top Priority Action Items" in final_state["detailed_report_markdown"]


def test_exporter(tmp_path, sample_pages, sample_links, sample_issues, sample_sitemaps):
    """Test exporting full state to JSON and multi-tab Excel."""
    from seo.exporter import export_to_excel, export_to_json

    state: SEOState = {
        "url": "https://example.com",
        "status": "completed",
        "overall_seo_score": 85,
        "pages": sample_pages,
        "links": sample_links,
        "issues": sample_issues,
        "sitemaps": sample_sitemaps,
        "priority_action_items": [
            {
                "priority": 1,
                "category": "Technical",
                "title": "Fix 404",
                "action": "Redirect",
                "impact_score": 9,
                "estimated_effort": "low",
                "affected_count": 1,
            }
        ],
    }

    json_path = str(tmp_path / "test_out.json")
    xlsx_path = str(tmp_path / "test_out.xlsx")

    export_to_json(state, json_path)
    assert os.path.exists(json_path)

    ok = export_to_excel(state, xlsx_path)
    assert ok is True
    assert os.path.exists(xlsx_path)
    assert os.path.getsize(xlsx_path) > 1000
