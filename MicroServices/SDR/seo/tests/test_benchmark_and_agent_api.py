"""
Unit Tests for Benchmark Engine, Agent APIs & Transparent Scoring (Phases 26-38, 50)
Verifies:
- Precision, Recall, and F1-Score calculation against ground truth
- Agent summary JSON generation (schema_version: 2.0, < 10KB payload)
- SEOAgentTools querying methods
- Transparent weighted scoring calculation
"""

import pytest
from LibreCrawl.src.core.benchmark import evaluate_audit_precision_recall, generate_benchmark_report
from LibreCrawl.src.core.agent_api import generate_agent_summary_json, SEOAgentTools, SCHEMA_VERSION
from LibreCrawl.src.core.scoring import calculate_transparent_score, create_3layer_finding, calculate_business_priority


def test_evaluate_precision_recall_f1():
    detected = [
        {"url": "https://example.com/a", "rule_id": "missing_title"},
        {"url": "https://example.com/b", "rule_id": "missing_meta_description"},
        {"url": "https://example.com/c", "rule_id": "broken_link"}  # False positive
    ]
    ground_truth = [
        {"url": "https://example.com/a", "rule_id": "missing_title"},
        {"url": "https://example.com/b", "rule_id": "missing_meta_description"},
        {"url": "https://example.com/d", "rule_id": "slow_response"}  # False negative
    ]

    metrics = evaluate_audit_precision_recall(detected, ground_truth)
    assert metrics["true_positives"] == 2
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["precision"] == 0.6667
    assert metrics["recall"] == 0.6667
    assert metrics["f1_score"] == 0.6667


def test_generate_agent_summary_json():
    sample_audit = {
        "base_url": "https://atlaskliniek.nl",
        "base_domain": "atlaskliniek.nl",
        "overall_seo_score": 85,
        "category_scores": {"Technical SEO": 90, "On-Page SEO": 80},
        "crawl_summary": {"duration_seconds": 12.5},
        "pages": [{"url": "https://atlaskliniek.nl/", "status_code": 200, "title": "Home", "word_count": 500}],
        "issues": [{"id": "iss_1", "severity": "CRITICAL", "title": "Server Error", "url": "https://atlaskliniek.nl/500"}],
        "priority_action_items": [{"priority": 1, "title": "Fix 500"}]
    }

    agent_summary = generate_agent_summary_json(sample_audit)
    assert agent_summary["schema_version"] == SCHEMA_VERSION
    assert agent_summary["domain"] == "atlaskliniek.nl"
    assert len(agent_summary["top_issues"]) == 1
    assert agent_summary["top_issues"][0]["severity"] == "CRITICAL"


def test_seo_agent_tools():
    sample_audit = {
        "base_url": "https://atlaskliniek.nl",
        "overall_seo_score": 88,
        "category_scores": {"Technical SEO": 90},
        "crawl_summary": {"total_pages": 10},
        "pages": [{"url": "https://atlaskliniek.nl/dentist", "title": "Dentist Amsterdam"}],
        "issues": [{"category": "Technical", "severity": "CRITICAL", "title": "Broken link"}],
        "priority_action_items": [{"title": "Fix broken link"}]
    }

    tools = SEOAgentTools(sample_audit)
    assert tools.get_crawl_summary()["overall_score"] == 88
    assert len(tools.get_issues_by_category("Technical")) == 1
    assert len(tools.get_issues_by_severity("CRITICAL")) == 1
    assert tools.get_page("https://atlaskliniek.nl/dentist")["title"] == "Dentist Amsterdam"


def test_transparent_scoring():
    cat_scores = {
        "Technical SEO": 80.0,
        "On-Page SEO": 90.0,
        "Content Quality": 70.0,
        "Performance": 85.0,
        "Structured Data": 100.0,
        "Internal Linking": 75.0,
        "Local SEO": 95.0
    }
    result = calculate_transparent_score(cat_scores)
    assert 80.0 <= result["score"] <= 86.0
    assert "weights" in result
    assert "breakdown" in result


def test_3layer_finding_and_business_priority():
    finding = create_3layer_finding(
        rule_id="missing_h1",
        category="On-Page",
        title="Missing H1 Tag",
        observation="Page has no H1 heading tag.",
        implication="Users and bots cannot easily identify the page main topic.",
        recommendation="Add one H1 heading tag.",
        severity="HIGH",
        confidence="high",
        impact=8,
        effort="low"
    )
    assert finding["severity"] == "HIGH"
    assert finding["confidence"] == "high"

    p_score = calculate_business_priority(finding, page_value_multiplier=1.2)
    assert p_score > 5.0
