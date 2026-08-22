from typing import TypedDict, List, Optional, Dict, Any
from business_analysis.schemas.models import (
    BusinessInput,
    Evidence,
    BusinessProfile,
    MarketAnalysis,
    CustomerAnalysis,
    CompetitorAnalysis,
    ServiceAnalysis,
    BusinessProblem,
    Opportunity,
    BusinessScore,
    FinalBusinessAnalysis,
    NodeExecutionStatus,
    NodeStatusEnum,
    AnalysisCompleteness,
    QualityGateResult,
    WebsiteAnalysisResult,
    SourceType,
)


class BusinessAnalysisState(TypedDict):
    input_business: BusinessInput
    evidence: List[Evidence]
    business_profile: Optional[BusinessProfile]
    market_analysis: Optional[MarketAnalysis]
    customer_analysis: Optional[CustomerAnalysis]
    competitor_analysis: Optional[CompetitorAnalysis]
    service_analysis: Optional[ServiceAnalysis]
    business_problems: List[BusinessProblem]
    opportunities: List[Opportunity]
    business_score: Optional[BusinessScore]
    final_report: Optional[FinalBusinessAnalysis]
    website_analysis: Optional[WebsiteAnalysisResult]
    node_statuses: Dict[str, NodeExecutionStatus]
    completeness: Optional[AnalysisCompleteness]
    quality_gate: Optional[QualityGateResult]
    errors: List[str]


def get_relevant_evidence(state: BusinessAnalysisState, category: str) -> List[Evidence]:
    evidence_list = state.get("evidence", [])
    if not evidence_list:
        return []

    category_keywords = {
        "business": ["company", "name", "location", "industry", "description", "established", "clinic", "practice", "headquartered", "official"],
        "market": ["industry", "market", "location", "area", "city", "digital", "adoption", "competition", "trends"],
        "customer": ["customer", "client", "patient", "target", "phobia", "anxiety", "problem", "rehabilitation", "care", "need"],
        "competitor": ["location", "city", "industry", "competitor", "clinic", "practice", "dentist", "services"],
        "service": ["service", "product", "care", "treatment", "dentistry", "anxiety", "case", "management", "offerings"],
        "problem": ["description", "service", "customer", "anxiety", "problem", "additional", "gaps", "friction"],
        "opportunity": ["service", "problem", "digital", "seo", "content", "website", "opportunity"],
    }

    keywords = category_keywords.get(category.lower(), [])
    relevant = []
    seen_ids = set()

    for e in evidence_list:
        if e.id in seen_ids:
            continue
        text = f"{e.claim} {e.supporting_text or ''}".lower()
        if any(kw in text for kw in keywords) or category == "business":
            relevant.append(e)
            seen_ids.add(e.id)

    if not relevant:
        return evidence_list[:5]

    return relevant


def create_initial_state(business_input: BusinessInput) -> BusinessAnalysisState:
    initial_evidence = [
        Evidence(
            claim=f"Company name is '{business_input.company_name}'",
            source="user_input",
            source_type=SourceType.MANUAL_INPUT,
            supporting_text=f"Company: {business_input.company_name}",
            confidence=1.0,
            relevance=1.0,
        ),
        Evidence(
            claim=f"Operates in industry '{business_input.industry}'",
            source="user_input",
            source_type=SourceType.MANUAL_INPUT,
            supporting_text=f"Industry: {business_input.industry}",
            confidence=1.0,
            relevance=1.0,
        ),
        Evidence(
            claim=f"Located in '{business_input.location}'",
            source="user_input",
            source_type=SourceType.MANUAL_INPUT,
            supporting_text=f"Location: {business_input.location}",
            confidence=1.0,
            relevance=1.0,
        ),
    ]

    if business_input.website:
        initial_evidence.append(
            Evidence(
                claim=f"Official website URL is '{business_input.website}'",
                source="user_input",
                source_type=SourceType.MANUAL_INPUT,
                supporting_text=f"Website: {business_input.website}",
                confidence=1.0,
                relevance=1.0,
            )
        )

    if business_input.description:
        initial_evidence.append(
            Evidence(
                claim=f"Business description: {business_input.description}",
                source="user_input",
                source_type=SourceType.MANUAL_INPUT,
                supporting_text=business_input.description,
                confidence=0.95,
                relevance=1.0,
            )
        )

    if business_input.products_services:
        initial_evidence.append(
            Evidence(
                claim=f"Products/services: {business_input.products_services}",
                source="user_input",
                source_type=SourceType.MANUAL_INPUT,
                supporting_text=business_input.products_services,
                confidence=0.95,
                relevance=1.0,
            )
        )

    if business_input.target_customers:
        initial_evidence.append(
            Evidence(
                claim=f"Target customers: {business_input.target_customers}",
                source="user_input",
                source_type=SourceType.MANUAL_INPUT,
                supporting_text=business_input.target_customers,
                confidence=0.9,
                relevance=1.0,
            )
        )


    if business_input.additional_info:
        initial_evidence.append(
            Evidence(
                claim=f"Additional business info: {business_input.additional_info}",
                source="user_input",
                source_type=SourceType.MANUAL_INPUT,
                supporting_text=business_input.additional_info,
                confidence=0.9,
                relevance=1.0,
            )
        )

    initial_statuses = {
        "collect_initial_evidence": NodeExecutionStatus(status=NodeStatusEnum.SUCCESS, confidence=1.0),
        "business_profile": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "market_analysis": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "customer_analysis": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "competitor_analysis": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "service_analysis": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "business_problem": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "opportunity": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "business_scoring": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
        "quality_gate": NodeExecutionStatus(status=NodeStatusEnum.SKIPPED, confidence=0.0),
    }

    return BusinessAnalysisState(
        input_business=business_input,
        evidence=initial_evidence,
        business_profile=None,
        market_analysis=None,
        customer_analysis=None,
        competitor_analysis=None,
        service_analysis=None,
        business_problems=[],
        opportunities=[],
        business_score=None,
        final_report=None,
        website_analysis=None,
        node_statuses=initial_statuses,
        completeness=None,
        quality_gate=None,
        errors=[],
    )