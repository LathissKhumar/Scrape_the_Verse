import json
from leadfinder.healing.fingerprint import DOMFingerprinter
from leadfinder.healing.freshness import RepairFreshnessLifecycle
from leadfinder.healing.schemas import (
    RepairConfidenceLevel,
    RepairFreshnessStatus,
    RepairMemoryRecord,
    RepairType,
)


def test_dom_fingerprinter_drift_detection():
    fingerprinter = DOMFingerprinter()
    html1 = "<html><body><main><article class='card'><h2>Title</h2><p>Price</p></article></main></body></html>"
    html2 = "<html><body><main><article class='card'><h2>Title</h2><p>Price</p></article></main></body></html>"
    html_mutated = "<html><body><table><thead><tr><th>Col</th></tr></thead><tbody><tr><td>Data</td></tr></tbody></table></body></html>"

    fp1 = fingerprinter.generate_fingerprint(html1)
    fp2 = fingerprinter.generate_fingerprint(html2)
    fp_mutated = fingerprinter.generate_fingerprint(html_mutated)

    # Identical pages have 0.0 drift
    assert fingerprinter.compute_drift_score(fp1, fp2) == 0.0
    assert fingerprinter.is_significant_drift(fp1, fp2) is False

    # Mutated page has significant drift
    drift = fingerprinter.compute_drift_score(fp1, fp_mutated)
    assert drift > 0.35
    assert fingerprinter.is_significant_drift(fp1, fp_mutated) is True


def test_repair_freshness_lifecycle():
    freshness = RepairFreshnessLifecycle()
    fingerprinter = DOMFingerprinter()
    html_base = "<html><body><div class='product-card'><h3>Item</h3></div></body></html>"
    fp_base = fingerprinter.generate_fingerprint(html_base)

    rec = RepairMemoryRecord(
        domain="shop.com",
        signature="sig_1",
        root_cause="SELECTOR_DRIFT",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        successful_patch={},
        health_before=0.0,
        health_after=1.0,
        strategy="css",
        status=RepairFreshnessStatus.ACTIVE,
        success_count=5,
        failure_count=0,
        structural_fingerprint=json.dumps(fp_base),
    )

    # 1. Fresh status when matching DOM
    status = freshness.evaluate_freshness(rec, current_fingerprint=fp_base)
    assert status == RepairFreshnessStatus.ACTIVE

    # 2. Mutated DOM -> transitions to STALE
    html_mut = "<html><body><table><tr><td>Table Item</td></tr></table></body></html>"
    fp_mut = fingerprinter.generate_fingerprint(html_mut)
    status_mut = freshness.evaluate_freshness(rec, current_fingerprint=fp_mut)
    assert status_mut == RepairFreshnessStatus.STALE

    # 3. Excessive failures -> transitions to DISABLED
    rec.failure_count = 4
    status_dis = freshness.evaluate_freshness(rec, current_fingerprint=fp_base)
    assert status_dis == RepairFreshnessStatus.DISABLED
