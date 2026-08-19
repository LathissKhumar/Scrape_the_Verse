from enum import Enum
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

DiagnosisStatus = Literal["diagnosed", "inconclusive", "not_needed", "escalated"]


class RootCause(str, Enum):
    SELECTOR_DRIFT = "SELECTOR_DRIFT"
    DOM_STRUCTURE_CHANGE = "DOM_STRUCTURE_CHANGE"
    SCRAPER_OUTPUT_MISSING = "SCRAPER_OUTPUT_MISSING"
    EXTRACTION_DEGRADATION = "EXTRACTION_DEGRADATION"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    PAGINATION_FAILURE = "PAGINATION_FAILURE"
    RENDERING_FAILURE = "RENDERING_FAILURE"
    CONTENT_FILTER_FAILURE = "CONTENT_FILTER_FAILURE"
    REGEX_PATTERN_FAILURE = "REGEX_PATTERN_FAILURE"
    TABLE_STRUCTURE_CHANGE = "TABLE_STRUCTURE_CHANGE"
    LLM_EXTRACTION_FAILURE = "LLM_EXTRACTION_FAILURE"
    SCHEMA_GENERATION_FAILURE = "SCHEMA_GENERATION_FAILURE"
    SOURCE_DATA_QUALITY = "SOURCE_DATA_QUALITY"
    UNKNOWN = "UNKNOWN"


class AffectedStage(str, Enum):
    SCRAPER_EXECUTION = "scraper_execution"
    CSS_EXTRACTION = "css_extraction"
    XPATH_EXTRACTION = "xpath_extraction"
    REGEX_EXTRACTION = "regex_extraction"
    TABLE_EXTRACTION = "table_extraction"
    LLM_EXTRACTION = "llm_extraction"
    SCHEMA_VALIDATION = "schema_validation"
    SOURCE_PAGE = "source_page"
    UNKNOWN = "unknown"


class RepairStrategy(str, Enum):
    RETRY_SAME_CONFIGURATION = "RETRY_SAME_CONFIGURATION"
    REPAIR_CSS_SELECTORS = "REPAIR_CSS_SELECTORS"
    REPAIR_XPATH_SELECTORS = "REPAIR_XPATH_SELECTORS"
    REPAIR_REGEX_PATTERN = "REPAIR_REGEX_PATTERN"
    REPAIR_TABLE_SCHEMA = "REPAIR_TABLE_SCHEMA"
    REPAIR_EXTRACTION_SCHEMA = "REPAIR_EXTRACTION_SCHEMA"
    SWITCH_EXTRACTION_STRATEGY = "SWITCH_EXTRACTION_STRATEGY"
    REGENERATE_LLM_EXTRACTION_SCHEMA = "REGENERATE_LLM_EXTRACTION_SCHEMA"
    ADJUST_CONTENT_CHUNKING = "ADJUST_CONTENT_CHUNKING"
    ADJUST_SEMANTIC_FILTERING = "ADJUST_SEMANTIC_FILTERING"
    RECHECK_RAW_CONTENT = "RECHECK_RAW_CONTENT"
    ESCALATE = "ESCALATE"


class RecommendedAction(str, Enum):
    REPAIR_EXTRACTION_SCHEMA = "REPAIR_EXTRACTION_SCHEMA"
    RETRY_SCRAPER = "RETRY_SCRAPER"
    FALLBACK_TO_LLM_EXTRACTION = "FALLBACK_TO_LLM_EXTRACTION"
    FALLBACK_TO_TABLE_EXTRACTION = "FALLBACK_TO_TABLE_EXTRACTION"
    UPDATE_SOURCE_EXPECTATIONS = "UPDATE_SOURCE_EXPECTATIONS"
    MANUAL_INSPECTION = "MANUAL_INSPECTION"
    NONE = "NONE"


class DiagnosisResult(BaseModel):
    """Structured diagnosis report detailing what failed, why, and the recommended repair strategy."""

    diagnosis_status: DiagnosisStatus = "diagnosed"
    root_cause: RootCause = RootCause.UNKNOWN
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Diagnostic confidence score.")
    failure_category: str = Field(default="UNKNOWN", description="Associated high-level failure category.")
    affected_stage: AffectedStage = AffectedStage.UNKNOWN
    affected_fields: list[str] = Field(default_factory=list, description="Fields failing extraction or validation.")
    evidence: list[str] = Field(default_factory=list, description="Evidence items supporting this diagnosis.")
    repair_strategy: RepairStrategy = RepairStrategy.ESCALATE
    repair_targets: list[str] = Field(default_factory=list, description="Target selectors, fields, or parameters.")
    recommended_action: RecommendedAction = RecommendedAction.MANUAL_INSPECTION
    metadata: dict[str, Any] = Field(default_factory=dict)
