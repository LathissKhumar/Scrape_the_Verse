from enum import Enum
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
import uuid


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
    supporting_text: Optional[str] = None
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
    evidence_ids: List[str] = []

    def __eq__(self, other: Any) -> bool:
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
    def wrap(cls, val: Any, status: FieldStatusEnum = FieldStatusEnum.KNOWN, confidence: float = 1.0, evidence_ids: List[str] = None):
        if isinstance(val, FieldStatus):
            return val
        if val is None or val == "Not specified" or val == "unknown":
            return cls(value="Not specified", status=FieldStatusEnum.UNKNOWN, confidence=0.0, evidence_ids=evidence_ids or [])
        return cls(value=val, status=status, confidence=confidence, evidence_ids=evidence_ids or [])



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
    business_name: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    official_name: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    business_type: FieldStatus = Field(default_factory=lambda: FieldStatus(value=BusinessType.OTHER.value, status=FieldStatusEnum.KNOWN, confidence=0.8))
    business_model: FieldStatus = Field(default_factory=lambda: FieldStatus(value=BusinessModel.B2C.value, status=FieldStatusEnum.KNOWN, confidence=0.8))
    industry: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    sub_industry: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    geographic_market: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    primary_location: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    service_area: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    primary_offerings: FieldStatus = Field(default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN))
    secondary_offerings: FieldStatus = Field(default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN))
    positioning: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    value_proposition: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    target_market: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    company_scale: FieldStatus = Field(default_factory=lambda: FieldStatus(value=CompanyScale.UNKNOWN.value, status=FieldStatusEnum.UNKNOWN))
    business_age: FieldStatus = Field(default_factory=lambda: FieldStatus(value="Not specified", status=FieldStatusEnum.UNKNOWN))
    specializations: FieldStatus = Field(default_factory=lambda: FieldStatus(value=[], status=FieldStatusEnum.UNKNOWN))
    evidence_ids: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def wrap_raw_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key in ["business_name", "official_name", "business_type", "business_model", "industry", 
                        "sub_industry", "geographic_market", "primary_location", "service_area", 
                        "primary_offerings", "secondary_offerings", "positioning", "value_proposition", 
                        "target_market", "company_scale", "business_age", "specializations"]:
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
    evidence_ids: List[str] = []


class MarketAnalysis(BaseModel):
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    local_market: Optional[str] = None
    industry_overview: Optional[str] = None
    local_market_conditions: Optional[str] = None
    market_condition: MarketCondition = MarketCondition.UNKNOWN
    customer_acquisition_environment: Optional[str] = None
    digital_adoption: DigitalAdoptionLevel = DigitalAdoptionLevel.UNKNOWN
    search_discovery_behavior: Optional[str] = None
    market_demand_signals: List[str] = []
    competitive_intensity: Optional[str] = None
    digital_trends: List[str] = []
    local_opportunity: Optional[str] = None
    content_opportunities: List[str] = []
    SEO_opportunities: List[str] = []
    search_intent_opportunities: List[SearchIntentOpportunity] = []
    digital_opportunities: List[str] = []
    evidence_ids: List[str] = []


class CustomerSegment(BaseModel):
    segment_name: str
    description: str = ""
    is_primary: bool = False
    why_it_matters: Optional[str] = None
    needs: List[str] = []
    intent_signals: List[str] = []
    evidence_ids: List[str] = []
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
    touchpoints: List[str] = []
    friction_points: List[str] = []


class ConversionAction(BaseModel):
    action: str
    description: str
    stage: JourneyStage = JourneyStage.CONVERSION


class CustomerAnalysis(BaseModel):
    segments: List[CustomerSegment] = []
    primary_segments: List[CustomerSegment] = []
    secondary_segments: List[CustomerSegment] = []
    primary_customers: List[str] = []
    secondary_customers: List[str] = []
    customer_needs: List[str] = []
    customer_pain_points: List[str] = []
    customer_intent: List[str] = []
    customer_intents: List[str] = []
    decision_factors: List[str] = []
    trust_factors: List[str] = []
    journey: List[CustomerJourneyStep] = []
    conversion_actions: List[ConversionAction] = []
    evidence_ids: List[str] = []


class CandidateCompetitor(BaseModel):
    name: str
    location: Optional[str] = None
    service_match: List[str] = []
    is_validated: bool = False
    validation_reason: Optional[str] = None


class Competitor(BaseModel):
    name: str
    website: Optional[str] = None
    location: Optional[str] = None
    services: List[str] = []
    positioning: Optional[str] = None
    specializations: List[str] = []
    offerings: List[str] = []
    digital_presence: Optional[str] = None
    website_quality: Optional[str] = None
    seo_presence: Optional[str] = None
    content_strategy: Optional[str] = None
    cta_effectiveness: Optional[str] = None
    customer_journey: Optional[str] = None
    trust_signals: List[str] = []
    local_presence: Optional[str] = None
    digital_strengths: List[str] = []
    digital_weaknesses: List[str] = []
    competitive_gaps: List[str] = []


class CompetitorAnalysis(BaseModel):
    candidates: List[CandidateCompetitor] = []
    competitors: List[Competitor] = []
    competitive_landscape_summary: Optional[str] = None
    comparison_matrix: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    identified_gaps: List[str] = []
    evidence_ids: List[str] = []


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
    category: Optional[str] = None
    importance: ServiceImportance = ServiceImportance.SECONDARY
    target_customer: Optional[str] = None
    customer_problem_solved: Optional[str] = None
    visibility: ServiceVisibility = ServiceVisibility.MODERATE
    discoverability: ServiceVisibility = ServiceVisibility.MODERATE
    digital_representation: Optional[str] = None
    dedicated_page: str = "unknown"
    CTA: str = "unknown"
    content_quality: str = "unknown"
    search_intent: Optional[str] = None
    potential_gap: Optional[str] = None
    has_dedicated_page: bool = False
    cta_present: bool = False
    customer_friction: List[str] = []
    content_gaps: List[str] = []
    confidence: float = 0.8
    evidence_ids: List[str] = []

    @field_validator("name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError(f"Service name too short: {v!r}")
        # Reject obvious malformed names from LLM hallucinations
        bad_patterns = ["=", "\\", '"', "{", "}", "target_customers", "products_services",
                        "additional_info", "description", "schema", "json", "null", "true", "false"]
        v_lower = v.lower().strip()
        for pat in bad_patterns:
            if pat in v:
                raise ValueError(f"Service name appears malformed (contains '{pat}'): {v!r}")
        return v.strip()


class ServiceAnalysis(BaseModel):
    services: List[Service] = []
    overall_visibility: ServiceVisibility = ServiceVisibility.MODERATE
    key_gaps: List[str] = []
    evidence_ids: List[str] = []


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
    description: Optional[str] = None
    type: ProblemType = ProblemType.SERVICE_VISIBILITY
    status: ProblemStatus = ProblemStatus.POTENTIAL
    evidence_ids: List[str] = []
    observations: List[str] = []
    business_impact: int = Field(ge=1, le=10, default=5)
    urgency: int = Field(ge=1, le=10, default=5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    reasoning: str = ""
    severity: ProblemSeverity = ProblemSeverity.MEDIUM
    affected_customer_segment: Optional[str] = None
    affected_service: Optional[str] = None

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
    recommended_services: List[AgencyService] = []
    expected_business_outcome: Optional[str] = None
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
    score_explanation: Union[str, Dict[str, str]]


class NodeStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class NodeExecutionStatus(BaseModel):
    status: NodeStatusEnum = NodeStatusEnum.SUCCESS
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    error_message: Optional[str] = None


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
    quality_status: Literal["PASSED", "PASSED_WITH_WARNINGS", "NEEDS_REVIEW", "FAILED"] = "PASSED"
    passed_checks: List[str] = []
    failed_checks: List[str] = []
    warnings: List[str] = []
    notes: List[str] = []


class WebsiteAnalysisResult(BaseModel):
    seo_score: Optional[int] = None
    technical_score: Optional[int] = None
    ux_score: Optional[int] = None
    content_score: Optional[int] = None
    conversion_score: Optional[int] = None
    crawl_status: Literal["COMPLETE", "PARTIAL", "FAILED", "UNAVAILABLE"] = "UNAVAILABLE"
    pages_analyzed: int = 0
    pages: List[str] = []
    findings: List[str] = []
    broken_links: List[str] = []
    missing_titles: List[str] = []
    missing_meta: List[str] = []
    performance: Optional[str] = None
    structured_data: Optional[str] = None
    mobile_issues: List[str] = []
    service_page_findings: List[str] = []
    confidence: float = 0.0


class FinalBusinessAnalysis(BaseModel):
    company_name: str
    website: Optional[str] = None
    industry: str
    location: str
    business_profile: BusinessProfile
    market_analysis: MarketAnalysis
    customer_analysis: CustomerAnalysis
    competitor_analysis: CompetitorAnalysis
    service_analysis: ServiceAnalysis
    business_problems: List[BusinessProblem] = []
    opportunities: List[Opportunity] = []
    business_score: BusinessScore
    evidence: List[Evidence] = []
    node_statuses: Dict[str, NodeExecutionStatus] = Field(default_factory=dict)
    completeness: Optional[AnalysisCompleteness] = None
    quality_gate: Optional[QualityGateResult] = None
    website_analysis: Optional[WebsiteAnalysisResult] = None
    sdr_opportunity_brief: Optional[Dict[str, Any]] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    errors: List[str] = []
    warnings: List[str] = []


class BusinessInput(BaseModel):
    company_name: str
    website: Optional[str] = None
    industry: str
    location: str
    description: Optional[str] = None
    products_services: Optional[str] = None
    target_customers: Optional[str] = None
    additional_info: Optional[str] = None