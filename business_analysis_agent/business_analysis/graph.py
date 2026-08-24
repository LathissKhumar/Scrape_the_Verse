from datetime import datetime

from langgraph.graph import END, START, StateGraph

from business_analysis.agents.business_problem import business_problem_agent
from business_analysis.agents.business_profile import business_profile_agent
from business_analysis.agents.business_scoring import business_scoring_agent
from business_analysis.agents.competitor_analysis import competitor_analysis_agent
from business_analysis.agents.customer_analysis import customer_analysis_agent
from business_analysis.agents.market_analysis import market_analysis_agent
from business_analysis.agents.opportunity import opportunity_agent
from business_analysis.agents.quality_gate import quality_gate_agent
from business_analysis.agents.service_analysis import service_analysis_agent
from business_analysis.schemas.models import FinalBusinessAnalysis
from business_analysis.state import BusinessAnalysisState


def collect_initial_evidence(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[1/7] Structuring initial evidence context...")
    return state


def run_business_profile_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[2/7] Running Business Profile Agent...")
    return business_profile_agent(state)


def run_parallel_analysis(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[3/7] Running Market, Customer, Competitor & Service analyses...")
    # Process sequentially (max_workers=1) for local Ollama to avoid VRAM thrashing on 4GB GPUs
    market_result = market_analysis_agent(state)
    customer_result = customer_analysis_agent(state)
    competitor_result = competitor_analysis_agent(state)
    service_result = service_analysis_agent(state)

    merged_statuses = dict(state.get("node_statuses", {}))
    merged_statuses.update(market_result.get("node_statuses", {}))
    merged_statuses.update(customer_result.get("node_statuses", {}))
    merged_statuses.update(competitor_result.get("node_statuses", {}))
    merged_statuses.update(service_result.get("node_statuses", {}))

    return {
        **state,
        "market_analysis": market_result.get("market_analysis"),
        "customer_analysis": customer_result.get("customer_analysis"),
        "competitor_analysis": competitor_result.get("competitor_analysis"),
        "service_analysis": service_result.get("service_analysis"),
        "node_statuses": merged_statuses,
        "errors": state.get("errors", [])
        + market_result.get("errors", [])
        + customer_result.get("errors", [])
        + competitor_result.get("errors", [])
        + service_result.get("errors", []),
    }


def run_business_problem_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[4/7] Synthesizing Business Problems...")
    return business_problem_agent(state)


def run_opportunity_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[5/7] Mapping Agency Service Opportunities...")
    return opportunity_agent(state)


def run_business_scoring_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[6/7] Computing Opportunity Score & Completeness...")
    return business_scoring_agent(state)


def run_quality_gate_node(state: BusinessAnalysisState) -> BusinessAnalysisState:
    print("[7/7] Validating Quality Gate & Evidence Grounding...")
    return quality_gate_agent(state)


def generate_final_report(state: BusinessAnalysisState) -> BusinessAnalysisState:
    required = [
        "business_profile",
        "market_analysis",
        "customer_analysis",
        "competitor_analysis",
        "service_analysis",
        "business_score",
    ]

    for key in required:
        if not state.get(key):
            return {
                **state,
                "errors": state.get("errors", [])
                + [f"{key} not available for final report"],
            }

    input_business = state["input_business"]
    all_errors = state.get("errors", [])

    # Separate genuine errors from warnings
    hard_errors = [
        e
        for e in all_errors
        if not e.startswith(("[WARNING]", "[QG]", "[ServiceAnalysis]"))
    ]
    warn_entries = [
        e
        for e in all_errors
        if e.startswith(("[WARNING]", "[QG]", "[ServiceAnalysis]"))
    ]

    report = FinalBusinessAnalysis(
        company_name=input_business.company_name,
        website=input_business.website,
        industry=input_business.industry,
        location=input_business.location,
        business_profile=state["business_profile"],
        market_analysis=state["market_analysis"],
        customer_analysis=state["customer_analysis"],
        competitor_analysis=state["competitor_analysis"],
        service_analysis=state["service_analysis"],
        business_problems=state.get("business_problems", []),
        opportunities=state.get("opportunities", []),
        business_score=state["business_score"],
        evidence=state.get("evidence", []),
        node_statuses=state.get("node_statuses", {}),
        completeness=state.get("completeness"),
        quality_gate=state.get("quality_gate"),
        website_analysis=state.get("website_analysis"),
        generated_at=datetime.now(),
        errors=hard_errors,
        warnings=warn_entries,
    )

    return {**state, "final_report": report}


def build_business_analysis_graph():
    graph = StateGraph(BusinessAnalysisState)

    graph.add_node("collect_initial_evidence", collect_initial_evidence)
    graph.add_node("business_profile", run_business_profile_node)
    graph.add_node("parallel_analysis", run_parallel_analysis)
    graph.add_node("business_problem", run_business_problem_node)
    graph.add_node("opportunity", run_opportunity_node)
    graph.add_node("business_scoring", run_business_scoring_node)
    graph.add_node("quality_gate", run_quality_gate_node)
    graph.add_node("generate_final_report", generate_final_report)

    graph.add_edge(START, "collect_initial_evidence")
    graph.add_edge("collect_initial_evidence", "business_profile")
    graph.add_edge("business_profile", "parallel_analysis")
    graph.add_edge("parallel_analysis", "business_problem")
    graph.add_edge("business_problem", "opportunity")
    graph.add_edge("opportunity", "business_scoring")
    graph.add_edge("business_scoring", "quality_gate")
    graph.add_edge("quality_gate", "generate_final_report")
    graph.add_edge("generate_final_report", END)

    return graph.compile()
