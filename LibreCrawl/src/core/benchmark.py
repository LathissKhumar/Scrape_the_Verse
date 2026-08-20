"""
Screaming Frog Benchmark Engine & Precision / Recall / F1 Calculator (Phases 35 & 36)
Evaluates LibreCrawl accuracy against ground-truth Screaming Frog benchmark audits.

Calculates:
- Precision: True Positives / (True Positives + False Positives)
- Recall: True Positives / (True Positives + False Negatives)
- F1-Score: 2 * (Precision * Recall) / (Precision + Recall)
"""

from typing import Dict, Any, List


def evaluate_audit_precision_recall(
    detected_issues: List[Dict[str, Any]],
    ground_truth_issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes Precision, Recall, and F1-Score comparing LibreCrawl findings against benchmark ground truth.
    """
    detected_keys = set(
        (str(i.get("url", "")).lower(), str(i.get("rule_id") or i.get("type") or i.get("issue", "")).lower())
        for i in detected_issues
    )
    ground_truth_keys = set(
        (str(i.get("url", "")).lower(), str(i.get("rule_id") or i.get("type") or i.get("issue", "")).lower())
        for i in ground_truth_issues
    )

    true_positives = len(detected_keys.intersection(ground_truth_keys))
    false_positives = len(detected_keys.difference(ground_truth_keys))
    false_negatives = len(ground_truth_keys.difference(detected_keys))

    precision = true_positives / max(1, true_positives + false_positives)
    recall = true_positives / max(1, true_positives + false_negatives)
    
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "target_met": (precision >= 0.90 and recall >= 0.85)
    }


def generate_benchmark_report(
    librecrawl_issues: List[Dict[str, Any]],
    screaming_frog_issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates benchmark_report.json matching Phase 50 criteria.
    """
    metrics = evaluate_audit_precision_recall(librecrawl_issues, screaming_frog_issues)

    benchmark_rules = []
    # Compare rule by rule
    sf_rule_set = set(str(i.get("rule_id") or i.get("issue", "")).lower() for i in screaming_frog_issues)
    lc_rule_set = set(str(i.get("rule_id") or i.get("issue", "")).lower() for i in librecrawl_issues)

    all_rules = sorted(list(sf_rule_set.union(lc_rule_set)))

    for rule in all_rules:
        in_sf = rule in sf_rule_set
        in_lc = rule in lc_rule_set
        agreement = (in_sf == in_lc)
        is_fp = (in_lc and not in_sf)

        benchmark_rules.append({
            "rule": rule,
            "screaming_frog": in_sf,
            "librecrawl": in_lc,
            "agreement": agreement,
            "false_positive": is_fp,
            "notes": "Matched benchmark" if agreement else ("False positive avoided/detected" if is_fp else "Missed in benchmark")
        })

    return {
        "metrics": metrics,
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "benchmark_rules": benchmark_rules
    }
