from typing import Any, Optional
from app.diagnosis.schemas import (
    AffectedStage,
    DiagnosisResult,
    RecommendedAction,
    RepairStrategy,
    RootCause,
)
from app.validation.schemas import FailureTaxonomy, ValidationResult


class RuleBasedClassifier:
    """Deterministically classifies clear-cut failure modes based on validation and transport evidence."""

    def classify(
        self,
        evidence: dict[str, Any],
        validation_result: ValidationResult,
    ) -> Optional[DiagnosisResult]:
        """Attempt deterministic rule-based classification. Returns None if ambiguous."""
        raw_available = evidence.get("raw_content_available", False)
        record_count = evidence.get("record_count", 0)
        failures = validation_result.failures
        failure_types = [f.failure_type for f in failures]
        scraper_meta = evidence.get("scraper_metadata", {}) or {}
        sample_html = str(evidence.get("sample_html", "")).lower()
        status_code = scraper_meta.get("status_code", 200)
        blocked_flag = scraper_meta.get("blocked", False)

        # Case 0: Bot Block, CAPTCHA, or 503 Challenge
        is_bot_blocked = (
            status_code in (403, 429, 503)
            or blocked_flag
            or any(sig in sample_html for sig in ["cs_503_link", "dogsofamazon", "validatecaptcha", "cf-browser-verification", "captcha", "cloudflare", "access denied"])
        )
        if is_bot_blocked:
            return DiagnosisResult(
                diagnosis_status="diagnosed",
                root_cause=RootCause.BOT_BLOCKED if status_code != 429 else RootCause.RATE_LIMITED,
                confidence=0.99,
                failure_category="BOT_BLOCKED",
                affected_stage=AffectedStage.SCRAPER_EXECUTION,
                affected_fields=evidence.get("requested_fields", []),
                evidence=[f"Anti-bot WAF, CAPTCHA challenge, or 503 block detected (HTTP {status_code}, blocked={blocked_flag})."],
                repair_strategy=RepairStrategy.SWITCH_COLLECTOR_PROVIDER,
                repair_targets=["scraper_transport", "proxy_configuration", "dca_cloud_scraper"],
                recommended_action=RecommendedAction.SWITCH_PROXIES,
            )

        # Case 1: Scraper returned zero/empty content
        if not raw_available or FailureTaxonomy.SCRAPER_OUTPUT_MISSING in failure_types:
            return DiagnosisResult(
                diagnosis_status="diagnosed",
                root_cause=RootCause.SCRAPER_OUTPUT_MISSING,
                confidence=0.98,
                failure_category=FailureTaxonomy.SCRAPER_OUTPUT_MISSING.value,
                affected_stage=AffectedStage.SCRAPER_EXECUTION,
                affected_fields=evidence.get("requested_fields", []),
                evidence=["Scraper returned empty raw content or encountered transport blocking/timeout."],
                repair_strategy=RepairStrategy.RETRY_SAME_CONFIGURATION,
                repair_targets=["scraper_transport", "proxy_configuration"],
                recommended_action=RecommendedAction.RETRY_SCRAPER,
            )

        # Case 2: Raw content exists, but extraction yielded 0 records
        if raw_available and record_count == 0:
            return DiagnosisResult(
                diagnosis_status="diagnosed",
                root_cause=RootCause.EXTRACTION_DEGRADATION,
                confidence=0.92,
                failure_category=FailureTaxonomy.EXTRACTION_DEGRADATION.value,
                affected_stage=AffectedStage.CSS_EXTRACTION,
                affected_fields=evidence.get("requested_fields", []),
                evidence=["Raw page content was successfully fetched, but the extraction engine produced 0 records."],
                repair_strategy=RepairStrategy.SWITCH_EXTRACTION_STRATEGY,
                repair_targets=["extraction_selectors", "extraction_strategy"],
                recommended_action=RecommendedAction.FALLBACK_TO_LLM_EXTRACTION,
            )

        # Case 3: Schema Mismatch (critical required fields missing entirely)
        if FailureTaxonomy.SCHEMA_MISMATCH in failure_types:
            missing = validation_result.schema_metrics.missing_required_fields
            return DiagnosisResult(
                diagnosis_status="diagnosed",
                root_cause=RootCause.SCHEMA_MISMATCH,
                confidence=0.95,
                failure_category=FailureTaxonomy.SCHEMA_MISMATCH.value,
                affected_stage=AffectedStage.SCHEMA_VALIDATION,
                affected_fields=missing,
                evidence=[f"Missing mandatory fields in extraction schema: {', '.join(missing)}"],
                repair_strategy=RepairStrategy.REPAIR_EXTRACTION_SCHEMA,
                repair_targets=missing,
                recommended_action=RecommendedAction.REPAIR_EXTRACTION_SCHEMA,
            )

        # Case 4: High Duplicates Explosion
        if FailureTaxonomy.HIGH_DUPLICATE_RATE in failure_types:
            return DiagnosisResult(
                diagnosis_status="diagnosed",
                root_cause=RootCause.PAGINATION_FAILURE,
                confidence=0.88,
                failure_category=FailureTaxonomy.HIGH_DUPLICATE_RATE.value,
                affected_stage=AffectedStage.SCRAPER_EXECUTION,
                affected_fields=[],
                evidence=[f"High duplicate rate ({evidence.get('duplicate_rate', 0.0) * 100:.1f}%) suggests pagination loop or repeated content."],
                repair_strategy=RepairStrategy.ADJUST_CONTENT_CHUNKING,
                repair_targets=["pagination_parameters", "deduplication_keys"],
                recommended_action=RecommendedAction.RETRY_SCRAPER,
            )

        # If not cleanly matched by simple deterministic rules, return None to invoke LLM
        return None
