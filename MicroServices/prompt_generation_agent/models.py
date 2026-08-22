from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


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
    evidence: Dict[str, Any] = {}


class PageFinding(BaseModel):
    url: str
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    word_count: int = 0
    status_code: int = 0
    issues: List[IssueFinding] = []


class WebsiteIntelligence(BaseModel):
    website_url: str
    website_exists: bool
    crawl_status: str
    pages_analyzed: int
    overall_score: int
    category_scores: Dict[str, int] = {}
    technical_findings: List[IssueFinding] = []
    seo_findings: List[IssueFinding] = []
    content_findings: List[IssueFinding] = []
    ux_findings: List[IssueFinding] = []
    conversion_findings: List[IssueFinding] = []
    page_findings: List[PageFinding] = []
    service_page_findings: List[PageFinding] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    critical_findings: List[IssueFinding] = []
    high_findings: List[IssueFinding] = []
    medium_findings: List[IssueFinding] = []
    low_findings: List[IssueFinding] = []
    important_pages: List[PageFinding] = []


class BusinessProfile(BaseModel):
    business_name: Optional[str] = None
    official_name: Optional[str] = None
    business_type: Optional[str] = None
    business_model: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    geographic_market: Optional[str] = None
    primary_location: Optional[str] = None
    service_area: Optional[str] = None
    primary_offerings: List[str] = []
    secondary_offerings: List[str] = []
    positioning: Optional[str] = None
    value_proposition: Optional[str] = None
    target_market: Optional[str] = None
    company_scale: Optional[str] = None
    business_age: Optional[str] = None
    specializations: List[str] = []
    evidence_ids: List[str] = []


class CustomerSegment(BaseModel):
    segment_name: str
    description: str
    is_primary: bool
    why_it_matters: str
    needs: List[str] = []
    intent_signals: List[str] = []
    evidence_ids: List[str] = []
    confidence: float = 0.0


class CustomerAnalysis(BaseModel):
    segments: List[CustomerSegment] = []
    primary_segments: List[CustomerSegment] = []
    secondary_segments: List[CustomerSegment] = []
    journey: List[Dict[str, Any]] = []
    evidence_ids: List[str] = []


class Service(BaseModel):
    name: str
    description: str
    category: Optional[str] = None
    importance: Optional[str] = None
    target_customer: Optional[str] = None
    customer_problem_solved: Optional[str] = None
    visibility: Optional[str] = None
    discoverability: Optional[str] = None
    has_dedicated_page: bool = False
    cta_present: bool = False
    confidence: float = 0.0
    evidence_ids: List[str] = []


class ServiceAnalysis(BaseModel):
    services: List[Service] = []
    overall_visibility: Optional[str] = None
    key_gaps: List[str] = []
    evidence_ids: List[str] = []


class BusinessProblem(BaseModel):
    id: str
    title: str
    problem: str
    description: str
    type: str
    status: str
    evidence_ids: List[str] = []
    business_impact: int = 0
    urgency: int = 0
    confidence: float = 0.0
    reasoning: str = ""
    severity: str = ""
    affected_customer_segment: Optional[str] = None
    affected_service: Optional[str] = None


class Opportunity(BaseModel):
    problem_reference: str
    opportunity: str
    recommended_services: List[str] = []
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
    market_analysis: Dict[str, Any] = {}
    customer_analysis: CustomerAnalysis
    competitor_analysis: Dict[str, Any] = {}
    service_analysis: ServiceAnalysis
    business_problems: List[BusinessProblem] = []
    opportunities: List[Opportunity] = []
    business_score: Dict[str, Any] = {}
    evidence: List[Evidence] = []
    quality_gate: Dict[str, Any] = {}
    warnings: List[str] = []
    errors: List[str] = []


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
    seo: List[str] = []
    ux: List[str] = []
    content: List[str] = []
    conversion: List[str] = []
    design: List[str] = []
    technical: List[str] = []


class StructuredOutput(BaseModel):
    company_name: str
    website: str
    prompt_type: str
    source_files: Dict[str, str]
    website_summary: Dict[str, Any] = {}
    business_summary: Dict[str, Any] = {}
    identified_problems: List[Dict[str, Any]] = []
    business_opportunities: List[Dict[str, Any]] = []
    recommended_changes: RecommendedChanges
    page_plan: List[PagePlan] = []
    preservation_rules: List[str] = []
    success_criteria: List[str] = []
    evidence_ids: List[str] = []
    confidence: float = 0.0
    generated_prompt: str = ""