"""
SEO Agent State Schema
Defines typed state for LangGraph nodes and audit analyzers.
"""

from typing import Any, TypedDict


class AuditFinding(TypedDict, total=False):
    category: str
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    impact: str
    recommendation: str
    affected_urls: list[str]
    evidence: dict[str, Any]


class ActionItem(TypedDict, total=False):
    priority: int  # 1 (highest) to 5 (lowest)
    category: str
    title: str
    action: str
    estimated_effort: str  # low, medium, high
    impact_score: int  # 1 to 10
    affected_count: int


class CategoryAuditResult(TypedDict, total=False):
    category: str
    score: int  # 0 to 100
    status: str  # passed, warning, failed
    summary: str
    findings: list[AuditFinding]
    metrics: dict[str, Any]


class SEOState(TypedDict, total=False):
    # Crawl input & configuration
    url: str
    crawl_config: dict[str, Any]
    job_id: str
    status: str  # initialized, crawling, analyzing, completed, failed

    # Raw & Normalized Crawl Evidence
    raw_crawl_data: dict[str, Any]
    pages: list[dict[str, Any]]
    links: list[dict[str, Any]]
    issues: list[dict[str, Any]]
    sitemaps: dict[str, Any]
    pagespeed: list[dict[str, Any]]
    crawl_summary: dict[str, Any]

    # Domain Audits
    technical_audit: CategoryAuditResult
    onpage_audit: CategoryAuditResult
    content_audit: CategoryAuditResult
    schema_audit: CategoryAuditResult
    local_audit: CategoryAuditResult
    performance_audit: CategoryAuditResult

    # Synthesis & Strategy
    overall_seo_score: int  # 0 to 100
    category_scores: dict[str, int]
    priority_action_items: list[ActionItem]
    executive_summary: str
    detailed_report_markdown: str

    # Error tracking & logs
    errors: list[str]
    messages: list[dict[str, str]]
