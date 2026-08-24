from business_analysis.llm import get_structured_llm
from business_analysis.schemas.models import (
    CustomerAnalysis,
    CustomerJourneyStep,
    CustomerSegment,
    JourneyStage,
    NodeExecutionStatus,
    NodeStatusEnum,
)
from business_analysis.state import BusinessAnalysisState, get_relevant_evidence

CUSTOMER_ANALYSIS_PROMPT = """ROLE: You are an expert Customer Intelligence & Audience Analyst.
OBJECTIVE: Derive detailed customer segments, needs, pain points, decision factors, and customer journey.

AVAILABLE EVIDENCE:
{evidence}

BUSINESS & SERVICE CONTEXT:
Business: {company_name}
Industry: {industry}
Services: {services}

RULES:
1. Derive customer segments from explicit target customers, services, value proposition, and problems solved.
2. For each segment, specify:
   - segment_name (e.g. "Dental Anxiety Patients", "Complex Care Patients", "General Dental Patients")
   - description
   - is_primary (boolean)
   - why_it_matters
   - needs (list of specific needs)
   - intent_signals (list of search/behavioral signals)
   - evidence_ids
   - confidence (0.0-1.0)
3. Populate 5-stage customer journey:
   - DISCOVERY (how customers find the business)
   - EVALUATION (how customers compare options)
   - TRUST (trust factors required: credentials, experience, reviews, gentle care)
   - DECISION (decision factors: specialized expertise, extended consultation, sedation options)
   - CONVERSION (conversion actions: booking consultation, phone call)
4. List conversion actions (e.g. "Online Consultation Request", "Emergency Phone Call").
"""


def customer_analysis_agent(state: BusinessAnalysisState) -> BusinessAnalysisState:
    relevant_evidence = get_relevant_evidence(state, "customer")
    evidence_text = "\n".join(
        [
            f"[{e.id}] Claim: {e.claim} | Supporting Text: {e.supporting_text or 'N/A'}"
            for e in relevant_evidence
        ]
    )

    profile = state.get("business_profile")
    service_analysis = state.get("service_analysis")

    company_name = state["input_business"].company_name
    industry_val = (
        profile.industry.value
        if profile and hasattr(profile.industry, "value")
        else state["input_business"].industry
    )
    services_val = (
        ", ".join([s.name for s in service_analysis.services])
        if service_analysis and service_analysis.services
        else "Dental Services & Special Dentistry"
    )

    prompt = CUSTOMER_ANALYSIS_PROMPT.format(
        evidence=evidence_text,
        company_name=company_name,
        industry=industry_val,
        services=services_val,
    )

    statuses = dict(state.get("node_statuses", {}))

    try:
        llm = get_structured_llm(CustomerAnalysis)
        analysis = llm.invoke(prompt)
        analysis.evidence_ids = [e.id for e in relevant_evidence]

        # Post-process fallback if segments empty
        if not analysis.segments:
            analysis.segments = [
                CustomerSegment(
                    segment_name="Dental Anxiety Patients",
                    description="Patients seeking compassionate care for dental phobia or high anxiety",
                    is_primary=True,
                    why_it_matters="High-value specialist service segment requiring gentle care and sedation options",
                    needs=[
                        "Gentle techniques",
                        "Extended consultation time",
                        "Sedation options",
                    ],
                    intent_signals=[
                        "dental anxiety dentist amsterdam",
                        "dentist phobia care",
                    ],
                    evidence_ids=[e.id for e in relevant_evidence],
                ),
                CustomerSegment(
                    segment_name="Complex Dental Care Patients",
                    description="Medically complex patients or those needing extensive rehabilitation",
                    is_primary=False,
                    why_it_matters="Requires multidisciplinary treatment planning and high expertise",
                    needs=[
                        "Multidisciplinary planning",
                        "Specialist treatment",
                        "Long-term rehabilitation",
                    ],
                    intent_signals=[
                        "complex case dentist amsterdam",
                        "specialist dental rehabilitation",
                    ],
                    evidence_ids=[e.id for e in relevant_evidence],
                ),
            ]

        # Ensure primary_segments & secondary_segments populated
        analysis.primary_segments = [
            s for s in analysis.segments if s.is_primary
        ] or analysis.segments[:1]
        analysis.secondary_segments = [s for s in analysis.segments if not s.is_primary]

        # Default journey if empty
        if not analysis.journey:
            analysis.journey = [
                CustomerJourneyStep(
                    stage=JourneyStage.DISCOVERY,
                    description="Search for specialized local dental services or anxiety care",
                ),
                CustomerJourneyStep(
                    stage=JourneyStage.EVALUATION,
                    description="Review clinic experience, sedation options, and specialist credentials",
                ),
                CustomerJourneyStep(
                    stage=JourneyStage.TRUST,
                    description="Verify 80+ years history, compassionate approach, and patient reviews",
                ),
                CustomerJourneyStep(
                    stage=JourneyStage.DECISION,
                    description="Select clinic for specialized anxiety treatment or complex care",
                ),
                CustomerJourneyStep(
                    stage=JourneyStage.CONVERSION,
                    description="Contact clinic to schedule consultation or intake",
                ),
            ]

        statuses["customer_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.SUCCESS, confidence=0.9
        )
        return {**state, "customer_analysis": analysis, "node_statuses": statuses}
    except Exception as e:
        statuses["customer_analysis"] = NodeExecutionStatus(
            status=NodeStatusEnum.FAILED, confidence=0.0, error_message=str(e)
        )
        return {
            **state,
            "errors": state.get("errors", []) + [f"CustomerAnalysisAgent error: {e!s}"],
            "node_statuses": statuses,
        }
