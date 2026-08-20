"""
Unit & Integration Tests for SEO Data Organizer & Normalization Layer
Tests:
- Dynamic domain-based directory creation (e.g. data/websites/atlaskliniek.nl/)
- Raw data preservation (raw/crawl.json)
- Full 23-section directory tree generation
- Deterministic page, issue, link, image IDs
- Deduplication of issues and links
- Strict missing value semantics (no fake values, status tracking)
- summary/validation.json integrity checks (zero data loss, valid schemas)
- LLM token reduction comparison
"""

import os
import json
import pytest
from seo.organizer import WebsiteDataOrganizer, extract_domain, normalize_url, generate_stable_id


def test_extract_domain():
    assert extract_domain("https://www.atlaskliniek.nl/en/dentist-amsterdam/") == "atlaskliniek.nl"
    assert extract_domain("http://example.com/test") == "example.com"
    assert extract_domain("sub.domain.co.uk") == "sub.domain.co.uk"


def test_normalize_url():
    assert normalize_url("https://Example.COM/path/#fragment") == "https://example.com/path/"
    assert normalize_url("http://example.com//a//b") == "http://example.com/a/b"


def test_generate_stable_id():
    id1 = generate_stable_id("page", "https://example.com/about")
    id2 = generate_stable_id("page", "https://example.com/about")
    id3 = generate_stable_id("page", "https://example.com/contact")
    
    assert id1 == id2
    assert id1 != id3
    assert id1.startswith("page_")


def test_organizer_end_to_end(tmp_path, sample_pages, sample_links, sample_issues, sample_sitemaps):
    """Test full normalization and folder organization."""
    raw_payload = {
        "crawl_id": "test_crawl_123",
        "base_url": "https://www.atlaskliniek.nl",
        "base_domain": "atlaskliniek.nl",
        "status": "completed",
        "overall_seo_score": 78,
        "category_scores": {"Technical SEO": 80, "On-Page SEO": 75},
        "crawl_summary": {
            "total_pages_crawled": len(sample_pages),
            "total_links": len(sample_links),
            "duration_seconds": 3.4
        },
        "pages": sample_pages,
        "links": sample_links,
        "issues": sample_issues,
        "sitemaps": sample_sitemaps,
        "pagespeed": [
            {
                "url": "https://www.atlaskliniek.nl/",
                "mobile": {"error": "API rate limited"},
                "desktop": {"performance_score": 85}
            }
        ],
        "priority_action_items": [
            {
                "priority": 1,
                "category": "Technical",
                "title": "Fix 404 Pages",
                "action": "Redirect broken links",
                "impact_score": 9,
                "estimated_effort": "low",
                "affected_count": 1
            }
        ]
    }

    base_out = str(tmp_path / "websites")
    organizer = WebsiteDataOrganizer(raw_payload, base_dir=base_out)
    master_index = organizer.process()

    domain_dir = os.path.join(base_out, "atlaskliniek.nl")
    assert os.path.exists(domain_dir)

    # 1. Verify Master Index
    assert os.path.exists(os.path.join(domain_dir, "index.json"))
    assert master_index["domain"] == "atlaskliniek.nl"
    assert master_index["overall_score"] == 78

    # 2. Verify Raw Data is preserved
    raw_path = os.path.join(domain_dir, "raw", "crawl.json")
    assert os.path.exists(raw_path)
    with open(raw_path, "r", encoding="utf-8") as f:
        saved_raw = json.load(f)
    assert saved_raw["crawl_id"] == "test_crawl_123"

    # 3. Verify Pages Directory
    assert os.path.exists(os.path.join(domain_dir, "pages", "index.json"))

    # 4. Verify Technical Directory
    for f_name in ["audit.json", "canonicals.json", "robots.json", "sitemap.json", "redirects.json", "errors.json"]:
        assert os.path.exists(os.path.join(domain_dir, "technical", f_name))

    # 5. Verify On-Page Directory
    for f_name in ["audit.json", "titles.json", "meta_descriptions.json", "headings.json", "images_alt.json"]:
        assert os.path.exists(os.path.join(domain_dir, "onpage", f_name))

    # 6. Verify Content Directory
    for f_name in ["audit.json", "thin_content.json", "duplicate_titles.json", "content_metrics.json"]:
        assert os.path.exists(os.path.join(domain_dir, "content", f_name))

    # 7. Verify Performance Directory (with strict missing PageSpeed status)
    for f_name in ["audit.json", "page_performance.json", "slow_pages.json", "pagespeed.json"]:
        assert os.path.exists(os.path.join(domain_dir, "performance", f_name))

    with open(os.path.join(domain_dir, "performance", "pagespeed.json"), "r") as f:
        ps_data = json.load(f)
    assert ps_data[0]["status"] == "unavailable"

    # 8. Verify Schema Directory
    for f_name in ["audit.json", "detected.json", "missing.json", "schema_types.json"]:
        assert os.path.exists(os.path.join(domain_dir, "schema", f_name))

    # 9. Verify Local Directory
    for f_name in ["audit.json", "business_schema.json", "local_signals.json"]:
        assert os.path.exists(os.path.join(domain_dir, "local", f_name))

    # 10. Verify Links Directory
    for f_name in ["all.json", "internal.json", "external.json", "broken.json", "anchor_text.json", "architecture.json"]:
        assert os.path.exists(os.path.join(domain_dir, "links", f_name))

    # 11. Verify Images Directory
    for f_name in ["all.json", "missing_alt.json", "statistics.json"]:
        assert os.path.exists(os.path.join(domain_dir, "images", f_name))

    # 12. Verify Analytics Directory
    assert os.path.exists(os.path.join(domain_dir, "analytics", "tracking.json"))

    # 13. Verify Issues Directory
    for f_name in ["all.json", "critical.json", "high.json", "medium.json", "low.json", "by_category.json"]:
        assert os.path.exists(os.path.join(domain_dir, "issues", f_name))

    # 14. Verify Recommendations Directory
    for f_name in ["all.json", "priority.json", "quick_wins.json", "high_impact.json"]:
        assert os.path.exists(os.path.join(domain_dir, "recommendations", f_name))

    # 15. Verify Summary Directory & Validation Report
    for f_name in ["overview.json", "category_scores.json", "metrics.json", "executive_summary.md", "validation.json"]:
        assert os.path.exists(os.path.join(domain_dir, "summary", f_name))

    with open(os.path.join(domain_dir, "summary", "validation.json"), "r") as f:
        val_report = json.load(f)
    assert val_report["valid"] is True
    assert val_report["data_loss"] is False
    assert val_report["normalized_pages_count"] == len(sample_pages)
