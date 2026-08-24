from enum import Enum
from typing import Any

from pydantic import BaseModel


class PromptType(str, Enum):
    WEBSITE_REDESIGN = "WEBSITE_REDESIGN"
    SEO_OPTIMIZATION = "SEO_OPTIMIZATION"
    UX_CONVERSION_OPTIMIZATION = "UX_CONVERSION_OPTIMIZATION"
    COMBINED_WEBSITE_OPTIMIZATION = "COMBINED_WEBSITE_OPTIMIZATION"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueFinding(BaseModel):
    id: str
    category: str
    type: str
    severity: str
    url: str
    title: str
    description: str
    evidence: dict[str, Any] = {}


class PageFinding(BaseModel):
    url: str
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    word_count: int = 0
    status_code: int = 0
    issues: list[IssueFinding] = []


class WebsiteIntelligence(BaseModel):
    website_url: str
    website_exists: bool
    crawl_status: str
    pages_analyzed: int
    overall_score: int
    category_scores: dict[str, int] = {}
    technical_findings: list[IssueFinding] = []
    seo_findings: list[IssueFinding] = []
    content_findings: list[IssueFinding] = []
    ux_findings: list[IssueFinding] = []
    conversion_findings: list[IssueFinding] = []
    page_findings: list[PageFinding] = []
    service_page_findings: list[PageFinding] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    critical_findings: list[IssueFinding] = []
    high_findings: list[IssueFinding] = []
    medium_findings: list[IssueFinding] = []
    low_findings: list[IssueFinding] = []
    important_pages: list[PageFinding] = []


class BusinessProfile(BaseModel):
    business_name: str | None = None
    official_name: str | None = None
    business_type: str | None = None
    business_model: str | None = None
    industry: str | None = None
    sub_industry: str | None = None
    geographic_market: str | None = None
    primary_location: str | None = None
    service_area: str | None = None
    primary_offerings: list[str] = []
    secondary_offerings: list[str] = []
    positioning: str | None = None
    value_proposition: str | None = None
    target_market: str | None = None
    company_scale: str | None = None
    business_age: str | None = None
    specializations: list[str] = []
    evidence_ids: list[str] = []


class CustomerSegment(BaseModel):
    segment_name: str
    description: str
    is_primary: bool
    why_it_matters: str
    needs: list[str] = []
    intent_signals: list[str] = []
    evidence_ids: list[str] = []
    confidence: float = 0.0


class CustomerAnalysis(BaseModel):
    segments: list[CustomerSegment] = []
    primary_segments: list[CustomerSegment] = []
    secondary_segments: list[CustomerSegment] = []
    journey: list[dict[str, Any]] = []
    evidence_ids: list[str] = []


class Service(BaseModel):
    name: str
    description: str
    category: str | None = None
    importance: str | None = None
    target_customer: str | None = None
    customer_problem_solved: str | None = None
    visibility: str | None = None
    discoverability: str | None = None
    has_dedicated_page: bool = False
    cta_present: bool = False
    confidence: float = 0.0
    evidence_ids: list[str] = []


class ServiceAnalysis(BaseModel):
    services: list[Service] = []
    overall_visibility: str | None = None
    key_gaps: list[str] = []
    evidence_ids: list[str] = []


class BusinessProblem(BaseModel):
    id: str
    title: str
    problem: str
    description: str
    type: str
    status: str
    evidence_ids: list[str] = []
    business_impact: int = 0
    urgency: int = 0
    confidence: float = 0.0
    reasoning: str = ""
    severity: str = ""
    affected_customer_segment: str | None = None
    affected_service: str | None = None


class Opportunity(BaseModel):
    problem_reference: str
    opportunity: str
    recommended_services: list[str] = []
    expected_business_outcome: str = ""
    priority: int = 0
    impact: int = 0
    urgency: int = 0
    confidence: float = 0.0
    effort: int = 0
    business_value: int = 0
    service_fit: int = 0
    rationale: str = ""


class Evidence(BaseModel):
    id: str
    claim: str
    source: str
    source_type: str
    supporting_text: str
    confidence: float
    relevance: float
    timestamp: str


class BusinessIntelligence(BaseModel):
    company_name: str
    website: str
    industry: str
    location: str
    business_profile: BusinessProfile
    market_analysis: dict[str, Any] = {}
    customer_analysis: CustomerAnalysis
    competitor_analysis: dict[str, Any] = {}
    service_analysis: ServiceAnalysis
    business_problems: list[BusinessProblem] = []
    opportunities: list[Opportunity] = []
    business_score: dict[str, Any] = {}
    evidence: list[Evidence] = []
    quality_gate: dict[str, Any] = {}
    warnings: list[str] = []
    errors: list[str] = []


class PagePlan(BaseModel):
    page_url: str
    page_name: str
    current_problem: str
    required_improvement: str
    business_reason: str
    seo_reason: str
    ux_reason: str
    conversion_reason: str


class RecommendedChanges(BaseModel):
    seo: list[str] = []
    ux: list[str] = []
    content: list[str] = []
    conversion: list[str] = []
    design: list[str] = []
    technical: list[str] = []


class StructuredOutput(BaseModel):
    company_name: str
    website: str
    prompt_type: str
    source_files: dict[str, str]
    website_summary: dict[str, Any] = {}
    business_summary: dict[str, Any] = {}
    identified_problems: list[dict[str, Any]] = []
    business_opportunities: list[dict[str, Any]] = []
    recommended_changes: RecommendedChanges
    page_plan: list[PagePlan] = []
    preservation_rules: list[str] = []
    success_criteria: list[str] = []
    evidence_ids: list[str] = []
    confidence: float = 0.0
    generated_prompt: str = ""
