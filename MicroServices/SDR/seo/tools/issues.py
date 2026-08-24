"""
SEO Issue Query and Filtering Tool
"""

from collections import defaultdict
from typing import Any


def filter_issues_tool(
    issues: list[dict[str, Any]],
    category: str | None = None,
    severity: str | None = None,
    issue_type: str | None = None,
    url_substring: str | None = None,
) -> list[dict[str, Any]]:
    """Filter issues by category, severity, type or URL substring."""
    filtered = issues
    if category:
        filtered = [
            i for i in filtered if (i.get("category") or "").lower() == category.lower()
        ]
    if severity:
        filtered = [
            i for i in filtered if (i.get("severity") or "").lower() == severity.lower()
        ]
    if issue_type:
        filtered = [
            i for i in filtered if (i.get("type") or "").lower() == issue_type.lower()
        ]
    if url_substring:
        filtered = [
            i for i in filtered if url_substring.lower() in (i.get("url") or "").lower()
        ]
    return filtered


def get_issue_summary_tool(issues: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a high-level statistical summary of detected issues."""
    by_severity = defaultdict(int)
    by_category = defaultdict(int)
    by_type = defaultdict(int)
    urls_with_issues = set()

    for issue in issues:
        by_severity[issue.get("severity", "medium")] += 1
        by_category[issue.get("category", "SEO")] += 1
        by_type[issue.get("type", "general")] += 1
        if issue.get("url"):
            urls_with_issues.add(issue.get("url"))

    return {
        "total_issues": len(issues),
        "total_urls_affected": len(urls_with_issues),
        "by_severity": dict(by_severity),
        "by_category": dict(by_category),
        "top_issue_types": sorted(by_type.items(), key=lambda x: x[1], reverse=True)[
            :10
        ],
    }
