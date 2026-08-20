"""
SEO Agent State Schema
Defines typed state for LangGraph nodes and audit analyzers.
"""

from typing import TypedDict, List, Dict, Any, Optional


class AuditFinding(TypedDict, total=False):
    category: str
    severity: str          # critical, high, medium, low, info
    title: str
    description: str
    impact: str
    recommendation: str
    affected_urls: List[str]
    evidence: Dict[str, Any]


class ActionItem(TypedDict, total=False):
    priority: int          # 1 (highest) to 5 (lowest)
    category: str
    title: str
    action: str
    estimated_effort: str  # low, medium, high
    impact_score: int      # 1 to 10
    affected_count: int


class CategoryAuditResult(TypedDict, total=False):
    category: str
    score: int             # 0 to 100
    status: str            # passed, warning, failed
    summary: str
    findings: List[AuditFinding]
    metrics: Dict[str, Any]


class SEOState(TypedDict, total=False):
    # Crawl input & configuration
    url: str
    crawl_config: Dict[str, Any]
    job_id: str
    status: str            # initialized, crawling, analyzing, completed, failed
    
    # Raw & Normalized Crawl Evidence
    raw_crawl_data: Dict[str, Any]
    pages: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    sitemaps: Dict[str, Any]
    pagespeed: List[Dict[str, Any]]
    crawl_summary: Dict[str, Any]
    
    # Domain Audits
    technical_audit: CategoryAuditResult
    onpage_audit: CategoryAuditResult
    content_audit: CategoryAuditResult
    schema_audit: CategoryAuditResult
    local_audit: CategoryAuditResult
    performance_audit: CategoryAuditResult
    
    # Synthesis & Strategy
    overall_seo_score: int # 0 to 100
    category_scores: Dict[str, int]
    priority_action_items: List[ActionItem]
    executive_summary: str
    detailed_report_markdown: str
    
    # Error tracking & logs
    errors: List[str]
    messages: List[Dict[str, str]]
