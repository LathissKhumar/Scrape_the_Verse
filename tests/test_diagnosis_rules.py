from app.diagnosis.classifier import RuleBasedClassifier
from app.diagnosis.schemas import RepairStrategy, RootCause
from app.validation.schemas import (
    DuplicateMetric,
    FailureItem,
    FailureTaxonomy,
    SchemaMetric,
    ValidationResult,
)


def test_rule_classifier_empty_scraper_output():
    classifier = RuleBasedClassifier()
    evidence = {
        "raw_content_available": False,
        "record_count": 0,
        "requested_fields": ["title"],
    }
    val_result = ValidationResult(
        status="broken",
        health_score=0.0,
        failures=[
            FailureItem(
                failure_type=FailureTaxonomy.SCRAPER_OUTPUT_MISSING,
                severity="critical",
                message="Transport error",
            )
        ],
    )

    diag = classifier.classify(evidence, val_result)
    assert diag is not None
    assert diag.root_cause == RootCause.SCRAPER_OUTPUT_MISSING
    assert diag.repair_strategy == RepairStrategy.RETRY_SAME_CONFIGURATION


def test_rule_classifier_extraction_degradation():
    classifier = RuleBasedClassifier()
    evidence = {
        "raw_content_available": True,
        "record_count": 0,
        "requested_fields": ["title", "price"],
    }
    val_result = ValidationResult(
        status="broken",
        health_score=0.0,
        failures=[
            FailureItem(
                failure_type=FailureTaxonomy.EXTRACTION_DEGRADATION,
                severity="critical",
                message="Zero records extracted",
            )
        ],
    )

    diag = classifier.classify(evidence, val_result)
    assert diag is not None
    assert diag.root_cause == RootCause.EXTRACTION_DEGRADATION
    assert diag.repair_strategy == RepairStrategy.SWITCH_EXTRACTION_STRATEGY


def test_rule_classifier_schema_mismatch():
    classifier = RuleBasedClassifier()
    evidence = {
        "raw_content_available": True,
        "record_count": 10,
        "requested_fields": ["product", "sku"],
    }
    val_result = ValidationResult(
        status="unstable",
        health_score=0.5,
        schema_metrics=SchemaMetric(missing_required_fields=["sku"]),
        failures=[
            FailureItem(
                failure_type=FailureTaxonomy.SCHEMA_MISMATCH,
                severity="critical",
                message="Missing sku",
            )
        ],
    )

    diag = classifier.classify(evidence, val_result)
    assert diag is not None
    assert diag.root_cause == RootCause.SCHEMA_MISMATCH
    assert diag.repair_strategy == RepairStrategy.REPAIR_EXTRACTION_SCHEMA
