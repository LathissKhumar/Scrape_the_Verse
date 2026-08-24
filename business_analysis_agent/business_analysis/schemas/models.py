import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class SourceType(str, Enum):
    MANUAL_INPUT = "manual_input"
    OFFICIAL_WEBSITE = "official_website"
    SEARCH_RESULT = "search_result"
    PUBLIC_BUSINESS_LISTING = "public_business_listing"
    OTHER = "other"


class ClaimType(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    claim: str
    source: str
    source_type: SourceType = SourceType.MANUAL_INPUT
    supporting_text: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    relevance: float = Field(ge=0.0, le=1.0, default=1.0)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class FieldStatusEnum(str, Enum):
    KNOWN = "KNOWN"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class FieldStatus(BaseModel):
    value: Any = "Not specified"
    status: FieldStatusEnum = FieldStatusEnum.UNKNOWN
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    evidence_ids: list[str] = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FieldStatus):
            return self.value == other.value and self.status == other.status
        if hasattr(self.value, "value"):
            return self.value.value == other or self.value == other
        return self.value == other

    def __len__(self) -> int:
        if isinstance(self.value, (list, tuple, str, dict)):
            return len(self.value)
        return 0

    def __iter__(self):
        if isinstance(self.value, (list, tuple, dict)):
            return iter(self.value)
        return iter([])

    def __str__(self) -> str:
        if hasattr(self.value, "value"):
            return str(self.value.value)
        return str(self.value)

    @classmethod
    def wrap(
        cls,
        val: Any,
        status: FieldStatusEnum = FieldStatusEnum.KNOWN,
        confidence: float = 1.0,
        evidence_ids: list[str] = None,
    ):
        if isinstance(val, FieldStatus):
            return val
        if val is None or val == "Not specified" or val == "unknown":
            return cls(
                value="Not specified",
                status=FieldStatusEnum.UNKNOWN,
                confidence=0.0,
                evidence_ids=evidence_ids or [],
            )
        return cls(
            value=val,
            status=status,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
        )


class BusinessType(str, Enum):
    LOCAL_SERVICE = "local_service"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    B2B_SERVICE = "b2b_service"
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    PROFESSIONAL_SERVICES = "professional_services"
    MANUFACTURING = "manufacturing"
    OTHER = "other"


class BusinessModel(str, Enum):
    B2C = "b2c"
    B2B = "b2b"
    B2B2C = "b2b2c"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION = "subscription"
    TRANSACTIONAL = "transactional"
    HYBRID = "hybrid"


class CompanyScale(str, Enum):
    SOLO = "solo"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"
    UNKNOWN = "unknown"


class BusinessProfile(BaseModel):
    business_name: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    official_name: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    business_type: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value=BusinessType.OTHER.value, status=FieldStatusEnum.KNOWN, confidence=0.8
        )
    )
    business_model: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value=BusinessModel.B2C.value, status=FieldStatusEnum.KNOWN, confidence=0.8
        )
    )
    industry: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    sub_industry: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    geographic_market: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    primary_location: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    service_area: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    primary_offerings: FieldStatus = Field(
        default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN)
    )
    secondary_offerings: FieldStatus = Field(
        default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN)
    )
    positioning: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    value_proposition: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    target_market: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    company_scale: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value=CompanyScale.UNKNOWN.value, status=FieldStatusEnum.UNKNOWN
        )
    )
    business_age: FieldStatus = Field(
        default_factory=lambda: FieldStatus(
            value="Not specified", status=FieldStatusEnum.UNKNOWN
        )
    )
    specializations: FieldStatus = Field(
        default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN)
    )
    evidence_ids: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def wrap_raw_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key in [
                "business_name",
                "official_name",
                "business_type",
                "business_model",
                "industry",
                "sub_industry",
                "geographic_market",
                "primary_location",
                "service_area",
                "primary_offerings",
                "secondary_offerings",
                "positioning",
                "value_proposition",
                "target_market",
                "company_scale",
                "business_age",
                "specializations",
            ]:
                if key in data and not isinstance(data[key], (dict, FieldStatus)):
                    data[key] = FieldStatus.wrap(data[key])
        return data


class MarketCondition(str, Enum):
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class DigitalAdoptionLevel(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNKNOWN = "unknown"


class SearchIntentCategory(str, Enum):
    BRANDED = "BRANDED"
    LOCAL = "LOCAL"
    SERVICE = "SERVICE"
    PROBLEM = "PROBLEM"
    COMMERCIAL = "COMMERCIAL"
    TRANSACTIONAL = "TRANSACTIONAL"
    INFORMATIONAL = "INFORMATIONAL"


class SearchIntentOpportunity(BaseModel):
    search_intent: SearchIntentCategory
    query_theme: str
    business_service: str
    customer_need: str
    priority: int = Field(ge=1, le=10, default=5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    evidence_ids: list[str] = []


class MarketAnalysis(BaseModel):
    industry: str | None = None
    sub_industry: str | None = None
    local_market: str | None = None
    industry_overview: str | None = None
    local_market_conditions: str | None = None
    market_condition: MarketCondition = MarketCondition.UNKNOWN
    customer_acquisition_environment: str | None = None
    digital_adoption: DigitalAdoptionLevel = DigitalAdoptionLevel.UNKNOWN
    search_discovery_behavior: str | None = None
    market_demand_signals: list[str] = []
    competitive_intensity: str | None = None
    digital_trends: list[str] = []
    local_opportunity: str | None = None
    content_opportunities: list[str] = []
    SEO_opportunities: list[str] = []
    search_intent_opportunities: list[SearchIntentOpportunity] = []
    digital_opportunities: list[str] = []
    evidence_ids: list[str] = []


class CustomerSegment(BaseModel):
    segment_name: str
    description: str = ""
    is_primary: bool = False
    why_it_matters: str | None = None
    needs: list[str] = []
    intent_signals: list[str] = []
    evidence_ids: list[str] = []
    confidence: float = 0.8


class JourneyStage(str, Enum):
    DISCOVERY = "discovery"
    EVALUATION = "evaluation"
    TRUST = "trust"
    DECISION = "decision"
    CONVERSION = "conversion"


class CustomerJourneyStep(BaseModel):
    stage: JourneyStage
    description: str
    touchpoints: list[str] = []
    friction_points: list[str] = []


class ConversionAction(BaseModel):
    action: str
    description: str
    stage: JourneyStage = JourneyStage.CONVERSION


class CustomerAnalysis(BaseModel):
    segments: list[CustomerSegment] = []
    primary_segments: list[CustomerSegment] = []
    secondary_segments: list[CustomerSegment] = []
    primary_customers: list[str] = []
    secondary_customers: list[str] = []
    customer_needs: list[str] = []
    customer_pain_points: list[str] = []
    customer_intent: list[str] = []
    customer_intents: list[str] = []
    decision_factors: list[str] = []
    trust_factors: list[str] = []
    journey: list[CustomerJourneyStep] = []
    conversion_actions: list[ConversionAction] = []
    evidence_ids: list[str] = []


class CandidateCompetitor(BaseModel):
    name: str
    location: str | None = None
    service_match: list[str] = []
    is_validated: bool = False
    validation_reason: str | None = None


class Competitor(BaseModel):
    name: str
    website: str | None = None
    location: str | None = None
    services: list[str] = []
    positioning: str | None = None
    specializations: list[str] = []
    offerings: list[str] = []
    digital_presence: str | None = None
    website_quality: str | None = None
    seo_presence: str | None = None
    content_strategy: str | None = None
    cta_effectiveness: str | None = None
    customer_journey: str | None = None
    trust_signals: list[str] = []
    local_presence: str | None = None
    digital_strengths: list[str] = []
    digital_weaknesses: list[str] = []
    competitive_gaps: list[str] = []


class CompetitorAnalysis(BaseModel):
    candidates: list[CandidateCompetitor] = []
    competitors: list[Competitor] = []
    competitive_landscape_summary: str | None = None
    comparison_matrix: dict[str, dict[str, str]] = Field(default_factory=dict)
    identified_gaps: list[str] = []
    evidence_ids: list[str] = []


class ServiceImportance(str, Enum):
    CORE = "core"
    SECONDARY = "secondary"
    PERIPHERAL = "peripheral"


class ServiceVisibility(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NONE = "none"


class Service(BaseModel):
    name: str
    description: str = ""
    category: str | None = None
    importance: ServiceImportance = ServiceImportance.SECONDARY
    target_customer: str | None = None
    customer_problem_solved: str | None = None
    visibility: ServiceVisibility = ServiceVisibility.MODERATE
    discoverability: ServiceVisibility = ServiceVisibility.MODERATE
    digital_representation: str | None = None
    dedicated_page: str = "unknown"
    CTA: str = "unknown"
    content_quality: str = "unknown"
    search_intent: str | None = None
    potential_gap: str | None = None
    has_dedicated_page: bool = False
    cta_present: bool = False
    customer_friction: list[str] = []
    content_gaps: list[str] = []
    confidence: float = 0.8
    evidence_ids: list[str] = []

    @field_validator("name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError(f"Service name too short: {v!r}")
        # Reject obvious malformed names from LLM hallucinations
        bad_patterns = [
            "=",
            "\\",
            '"',
            "{",
            "}",
            "target_customers",
            "products_services",
            "additional_info",
            "description",
            "schema",
            "json",
            "null",
            "true",
            "false",
        ]
        v_lower = v.lower().strip()
        for pat in bad_patterns:
            if pat in v:
                raise ValueError(
                    f"Service name appears malformed (contains '{pat}'): {v!r}"
                )
        return v.strip()


class ServiceAnalysis(BaseModel):
    services: list[Service] = []
    overall_visibility: ServiceVisibility = ServiceVisibility.MODERATE
    key_gaps: list[str] = []
    evidence_ids: list[str] = []


class ProblemSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProblemStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    POTENTIAL = "POTENTIAL"


class ProblemType(str, Enum):
    DISCOVERY = "DISCOVERY"
    SEO = "SEO"
    CONVERSION = "CONVERSION"
    UX = "UX"
    CONTENT = "CONTENT"
    TRUST = "TRUST"
    POSITIONING = "POSITIONING"
    SERVICE_VISIBILITY = "SERVICE_VISIBILITY"
    CUSTOMER_ACQUISITION = "CUSTOMER_ACQUISITION"
    DIGITAL_PRESENCE = "DIGITAL_PRESENCE"
    COMPETITIVE_GAP = "COMPETITIVE_GAP"


class BusinessProblem(BaseModel):
    id: str = Field(default_factory=lambda: f"prob_{str(uuid.uuid4())[:6]}")
    title: str = ""
    problem: str = ""
    description: str | None = None
    type: ProblemType = ProblemType.SERVICE_VISIBILITY
    status: ProblemStatus = ProblemStatus.POTENTIAL
    evidence_ids: list[str] = []
    observations: list[str] = []
    business_impact: int = Field(ge=1, le=10, default=5)
    urgency: int = Field(ge=1, le=10, default=5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    reasoning: str = ""
    severity: ProblemSeverity = ProblemSeverity.MEDIUM
    affected_customer_segment: str | None = None
    affected_service: str | None = None

    @model_validator(mode="before")
    @classmethod
    def sync_title_problem(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "problem" in data and not data.get("title"):
                data["title"] = data["problem"]
            elif "title" in data and not data.get("problem"):
                data["problem"] = data["title"]
        return data


class AgencyService(str, Enum):
    NEW_WEBSITE = "NEW_WEBSITE"
    WEBSITE_REDESIGN = "WEBSITE_REDESIGN"
    SEO = "SEO"
    LOCAL_SEO = "LOCAL_SEO"
    TECHNICAL_SEO = "TECHNICAL_SEO"
    CONTENT = "CONTENT"
    CONVERSION_OPTIMIZATION = "CONVERSION_OPTIMIZATION"
    LANDING_PAGE = "LANDING_PAGE"
    WEBSITE_PERFORMANCE = "WEBSITE_PERFORMANCE"
    DIGITAL_PRESENCE = "DIGITAL_PRESENCE"
    SERVICE_LANDING_PAGES = "SERVICE_LANDING_PAGES"


class Opportunity(BaseModel):
    problem_reference: str = ""
    opportunity: str
    recommended_services: list[AgencyService] = []
    expected_business_outcome: str | None = None
    priority: int = Field(ge=1, le=10, default=5)
    impact: int = Field(ge=1, le=10, default=5)
    urgency: int = Field(ge=1, le=10, default=5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    effort: int = Field(ge=1, le=10, default=5)
    business_value: int = Field(ge=1, le=10, default=5)
    service_fit: int = Field(ge=1, le=10, default=5)
    rationale: str = ""
    estimated_impact: str = ""


class ScoreCategory(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class BusinessScore(BaseModel):
    business_fit: int = Field(ge=0, le=100)
    digital_need: int = Field(ge=0, le=100)
    opportunity_value: int = Field(ge=0, le=100)
    evidence_confidence: int = Field(ge=0, le=100)
    serviceability: int = Field(ge=0, le=100)
    analysis_completeness: int = Field(ge=0, le=100, default=100)
    overall_score: int = Field(ge=0, le=100)
    priority: ScoreCategory
    score_explanation: str | dict[str, str]


class NodeStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class NodeExecutionStatus(BaseModel):
    status: NodeStatusEnum = NodeStatusEnum.SUCCESS
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    error_message: str | None = None


class AnalysisCompleteness(BaseModel):
    profile_completeness: float = 0.0
    market_completeness: float = 0.0
    customer_completeness: float = 0.0
    competitor_completeness: float = 0.0
    service_completeness: float = 0.0
    problem_completeness: float = 0.0
    opportunity_completeness: float = 0.0
    overall_analysis_completeness: float = 0.0


class QualityGateResult(BaseModel):
    quality_status: Literal[
        "PASSED", "PASSED_WITH_WARNINGS", "NEEDS_REVIEW", "FAILED"
    ] = "PASSED"
    passed_checks: list[str] = []
    failed_checks: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []


class WebsiteAnalysisResult(BaseModel):
    seo_score: int | None = None
    technical_score: int | None = None
    ux_score: int | None = None
    content_score: int | None = None
    conversion_score: int | None = None
    crawl_status: Literal["COMPLETE", "PARTIAL", "FAILED", "UNAVAILABLE"] = (
        "UNAVAILABLE"
    )
    pages_analyzed: int = 0
    pages: list[str] = []
    findings: list[str] = []
    broken_links: list[str] = []
    missing_titles: list[str] = []
    missing_meta: list[str] = []
    performance: str | None = None
    structured_data: str | None = None
    mobile_issues: list[str] = []
    service_page_findings: list[str] = []
    confidence: float = 0.0


class FinalBusinessAnalysis(BaseModel):
    company_name: str
    website: str | None = None
    industry: str
    location: str
    business_profile: BusinessProfile
    market_analysis: MarketAnalysis
    customer_analysis: CustomerAnalysis
    competitor_analysis: CompetitorAnalysis
    service_analysis: ServiceAnalysis
    business_problems: list[BusinessProblem] = []
    opportunities: list[Opportunity] = []
    business_score: BusinessScore
    evidence: list[Evidence] = []
    node_statuses: dict[str, NodeExecutionStatus] = Field(default_factory=dict)
    completeness: AnalysisCompleteness | None = None
    quality_gate: QualityGateResult | None = None
    website_analysis: WebsiteAnalysisResult | None = None
    sdr_opportunity_brief: dict[str, Any] | None = None
    generated_at: datetime = Field(default_factory=datetime.now)
    errors: list[str] = []
    warnings: list[str] = []


class BusinessInput(BaseModel):
    company_name: str
    website: str | None = None
    industry: str
    location: str
    description: str | None = None
    products_services: str | None = None
    target_customers: str | None = None
    additional_info: str | None = None
