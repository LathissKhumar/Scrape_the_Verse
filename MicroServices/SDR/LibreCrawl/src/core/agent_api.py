"""
Agent-Optimized Data Layer & Tool-Friendly Data Access APIs (Phases 37 & 38)
Provides schema-versioned (schema_version: "2.0"), token-efficient JSON outputs for SalesShortcut LangGraph SEO Agents:
- Full Audit JSON (audit/full.json)
- Compact Agent Summary JSON (audit/agent_summary.json)
- Programmatic Tool APIs (get_issue_summary, get_page, get_recommendations...)
"""

from typing import Dict, Any, List, Optional
import os
import json


SCHEMA_VERSION = "2.0"


def generate_agent_summary_json(full_audit_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a compact (< 10 KB, ~1000 tokens) JSON payload tailored for LLM agents.
    Excludes massive raw page dumps while retaining critical findings, high-confidence issues,
    category scores, performance metrics, and priority action items.
    """
    base_url = full_audit_state.get("base_url") or full_audit_state.get("url", "")
    domain = full_audit_state.get("base_domain") or ""
    
    pages = full_audit_state.get("pages", [])
    issues = full_audit_state.get("issues", [])
    recs = full_audit_state.get("priority_action_items", [])
    cat_scores = full_audit_state.get("category_scores", {})

    # Top critical & high severity issues only
    high_priority_issues = [
        {
            "id": i.get("id") or i.get("rule_id"),
            "category": i.get("category"),
            "title": i.get("title") or i.get("issue"),
            "severity": i.get("severity"),
            "confidence": i.get("confidence", "high"),
            "url": i.get("url"),
            "observation": i.get("observation") or i.get("details"),
            "recommendation": i.get("recommendation")
        }
        for i in issues
        if str(i.get("severity")).lower() in ("critical", "high", "error")
    ][:15]

    # Compact page index (URL, status, title, word_count)
    page_index = [
        {
            "url": p.get("url"),
            "status_code": p.get("status_code"),
            "title": (p.get("title") or "")[:50],
            "word_count": p.get("word_count", 0),
            "resource_type": p.get("resource_type", "html")
        }
        for p in pages[:20]
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": domain,
        "base_url": base_url,
        "overall_score": full_audit_state.get("overall_seo_score", 0),
        "category_scores": cat_scores,
        "summary_metrics": {
            "total_pages_crawled": len(pages),
            "total_issues_detected": len(issues),
            "total_recommendations": len(recs),
            "duration_seconds": full_audit_state.get("crawl_summary", {}).get("duration_seconds", 0)
        },
        "top_issues": high_priority_issues,
        "priority_recommendations": recs[:10],
        "sampled_page_index": page_index
    }


class SEOAgentTools:
    """
    Tool-friendly data access class for LangGraph SEO agents.
    """

    def __init__(self, audit_state: Dict[str, Any]):
        self.state = audit_state
        self.schema_version = SCHEMA_VERSION

    def get_crawl_summary(self) -> Dict[str, Any]:
        """Returns compact crawl summary and scores."""
        return {
            "schema_version": self.schema_version,
            "url": self.state.get("base_url"),
            "overall_score": self.state.get("overall_seo_score"),
            "category_scores": self.state.get("category_scores"),
            "summary": self.state.get("crawl_summary")
        }

    def get_issues_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Returns issues filtered by category."""
        category_lower = category.lower()
        return [
            i for i in self.state.get("issues", [])
            if str(i.get("category", "")).lower() == category_lower
        ]

    def get_issues_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Returns issues filtered by severity."""
        sev_lower = severity.lower()
        return [
            i for i in self.state.get("issues", [])
            if str(i.get("severity", "")).lower() == sev_lower
        ]

    def get_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Returns detailed PageRecord for a specific URL."""
        url_lower = url.lower().split("#")[0]
        for p in self.state.get("pages", []):
            if p.get("url", "").lower() == url_lower:
                return p
        return None

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Returns priority action items."""
        return self.state.get("priority_action_items", [])
