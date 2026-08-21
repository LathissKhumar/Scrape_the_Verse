from enum import Enum
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

ValidationStatus = Literal["healthy", "degraded", "unstable", "broken"]


class FailureTaxonomy(str, Enum):
    EMPTY_RESULTS = "EMPTY_RESULTS"
    SCRAPER_OUTPUT_MISSING = "SCRAPER_OUTPUT_MISSING"
    EXTRACTION_DEGRADATION = "EXTRACTION_DEGRADATION"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    LOW_FIELD_COVERAGE = "LOW_FIELD_COVERAGE"
    HIGH_DUPLICATE_RATE = "HIGH_DUPLICATE_RATE"
    INVALID_URLS = "INVALID_URLS"
    INVALID_FIELD_TYPES = "INVALID_FIELD_TYPES"
    LOW_RECORD_COUNT = "LOW_RECORD_COUNT"
    UNEXPECTED_STRUCTURE = "UNEXPECTED_STRUCTURE"


class FailureItem(BaseModel):
    """Structured failure diagnosis item for future phases."""

    failure_type: FailureTaxonomy
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class FieldMetric(BaseModel):
    """Coverage and validity metrics for a specific requested field."""

    coverage: float = Field(default=0.0, description="Ratio of non-empty, valid values to total records.")
    valid_count: int = Field(default=0, description="Count of valid, non-empty, non-placeholder values.")
    empty_count: int = Field(default=0, description="Count of null, empty string, or whitespace values.")
    invalid_type_count: int = Field(default=0, description="Count of values failing type validation.")
    placeholder_count: int = Field(default=0, description="Count of placeholder values (e.g. N/A, unknown).")


class DuplicateMetric(BaseModel):
    """Metrics assessing duplicate records in the extraction output."""

    total_records: int = 0
    unique_records: int = 0
    duplicate_records: int = 0
    duplicate_rate: float = 0.0


class UrlMetric(BaseModel):
    """Metrics assessing URL syntax and validity across URL-typed fields."""

    total_urls: int = 0
    valid_urls: int = 0
    invalid_urls: int = 0
    valid_rate: float = 1.0


class SchemaMetric(BaseModel):
    """Metrics assessing conformance to the expected output schema."""

    valid_records: int = 0
    invalid_records: int = 0
    valid_rate: float = 1.0
    missing_required_fields: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Comprehensive diagnostic container produced by ValidationEngine."""

    status: ValidationStatus = "healthy"
    health_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Operational pipeline health score.")
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Intrinsic source data quality score.")
    record_count: int = 0
    expected_record_count: Optional[int] = None
    field_metrics: dict[str, FieldMetric] = Field(default_factory=dict)
    duplicate_metrics: DuplicateMetric = Field(default_factory=DuplicateMetric)
    url_metrics: UrlMetric = Field(default_factory=UrlMetric)
    schema_metrics: SchemaMetric = Field(default_factory=SchemaMetric)
    anomalies: list[str] = Field(default_factory=list)
    failures: list[FailureItem] = Field(default_factory=list)
    recommendation: str = "healthy"
    metadata: dict[str, Any] = Field(default_factory=dict)
