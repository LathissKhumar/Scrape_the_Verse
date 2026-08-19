from typing import Any, Optional
from langgraph.graph import END, START, StateGraph

from app.agents.diagnosis import DiagnosisAgent
from app.agents.extraction import ExtractionAgent
from app.agents.planner import ScrapingPlannerAgent
from app.agents.scraper import ScraperAgent
from app.agents.validation import ValidationAgent
from app.brightdata.client import BrightDataClient
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.diagnosis.schemas import DiagnosisResult
from app.extraction.schema import ExtractionResult
from app.graph.state import ScrapingGraphState
from app.llm.ollama_client import OllamaClient
from app.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask
from app.validation.schemas import ValidationResult

logger = get_logger("GRAPH")


def create_scraping_workflow(
    planner_agent: Optional[ScrapingPlannerAgent] = None,
    scraper_agent: Optional[ScraperAgent] = None,
    extraction_agent: Optional[ExtractionAgent] = None,
    validation_agent: Optional[ValidationAgent] = None,
    diagnosis_agent: Optional[DiagnosisAgent] = None,
):
    """Build and compile the Phase 4 LangGraph scraping state machine:

    START -> planner -> scraper -> extraction -> validation -> [conditionally] diagnosis -> END
    """
    settings = get_settings()
    llm = OllamaClient(settings=settings)
    planner = planner_agent or ScrapingPlannerAgent(llm_client=llm)
    scraper = scraper_agent or ScraperAgent(brightdata_client=BrightDataClient(settings=settings))
    extractor = extraction_agent or ExtractionAgent(llm_client=llm)
    validator = validation_agent or ValidationAgent()
    diagnostician = diagnosis_agent or DiagnosisAgent(llm_client=llm)

    async def planner_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        query = state.get("original_user_query", "")
        supplied_urls = state.get("target_urls", [])

        logger.info(f"task_id={task_id} [GRAPH:planner_node] Running planner agent")

        request = ScrapingRequest(
            query=query,
            target_urls=supplied_urls,
        )

        task: ScrapingTask = await planner.plan_async(request=request, task_id=task_id)

        return {
            "scraping_task": task,
            "target_urls": task.target_urls,
        }

    async def scraper_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")

        logger.info(f"task_id={task_id} [GRAPH:scraper_node] Running scraper agent")

        if not task or not task.target_urls:
            err_msg = "No target URL was supplied. URL discovery is not implemented."
            logger.error(f"task_id={task_id} {err_msg}")
            failure_info = {
                "failure_type": "MISSING_TARGET_URL",
                "message": err_msg,
            }
            final_res = ScrapingResult(
                task_id=task_id,
                status="failed",
                records=[],
                metadata={"task_id": task_id, "record_count": 0},
                error=err_msg,
            )
            return {
                "failure": failure_info,
                "final_output": final_res,
            }

        try:
            raw_records = await scraper.execute(task=task)
            return {"raw_results": raw_records}
        except Exception as e:
            logger.error(f"task_id={task_id} Scraper execution failure: {e}")
            failure_info = {
                "failure_type": "SCRAPER_EXECUTION_FAILURE",
                "message": str(e),
            }
            final_res = ScrapingResult(
                task_id=task_id,
                status="failed",
                records=[],
                metadata={"task_id": task_id, "record_count": 0},
                error=str(e),
            )
            return {
                "failure": failure_info,
                "final_output": final_res,
            }

    async def extraction_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")
        raw_results = state.get("raw_results")

        if state.get("final_output") and state["final_output"].status == "failed":
            return {}

        logger.info(f"task_id={task_id} [GRAPH:extraction_node] Running extraction agent")

        if not raw_results:
            empty_msg = "No raw content retrieved for extraction."
            logger.warning(f"task_id={task_id} {empty_msg}")
            return {
                "extracted_results": [],
            }

        try:
            extraction_result: ExtractionResult = await extractor.extract(
                raw_results=raw_results,
                task=task,
            )
            return {
                "extracted_results": extraction_result.records,
            }
        except Exception as e:
            logger.error(f"task_id={task_id} Extraction failure: {e}")
            failure_info = {
                "failure_type": "EXTRACTION_FAILURE",
                "message": str(e),
            }
            return {
                "extracted_results": [],
                "failure": failure_info,
            }

    async def validation_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")
        raw_results = state.get("raw_results")
        extracted_results = state.get("extracted_results") or []

        if state.get("final_output") and state["final_output"].status == "failed":
            return {}

        logger.info(f"task_id={task_id} [GRAPH:validation_node] Running validation agent")

        validation_result: ValidationResult = await validator.validate(
            extracted_results=extracted_results,
            task=task or ScrapingTask(task_id=task_id, objective="", target_urls=[]),
            raw_results=raw_results,
        )

        if validation_result.status == "healthy":
            final_status = "success"
            err_str = None
        elif validation_result.status in ("degraded", "unstable"):
            final_status = "partial" if extracted_results else "failed"
            err_str = (
                f"Validation detected quality degradation: health_score={validation_result.health_score}"
            )
        else:  # broken
            final_status = "failed" if not extracted_results else "partial"
            err_str = "Validation detected severe extraction degradation or broken output"

        final_res = ScrapingResult(
            task_id=task_id,
            status=final_status,
            records=extracted_results,
            metadata={
                "task_id": task_id,
                "record_count": len(extracted_results),
                "health_score": validation_result.health_score,
                "quality_score": validation_result.quality_score,
                "validation_status": validation_result.status,
                "anomalies": validation_result.anomalies,
                "validation": {
                    "field_coverage": {
                        k: v.coverage for k, v in validation_result.field_metrics.items()
                    },
                    "duplicate_rate": validation_result.duplicate_metrics.duplicate_rate,
                    "url_valid_rate": validation_result.url_metrics.valid_rate,
                    "schema_valid_rate": validation_result.schema_metrics.valid_rate,
                },
            },
            error=err_str,
        )

        return {
            "validation_result": validation_result.model_dump(),
            "failure": [f.model_dump() for f in validation_result.failures] if validation_result.failures else state.get("failure"),
            "final_output": final_res,
        }

    async def diagnosis_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")
        raw_results = state.get("raw_results")
        extracted_results = state.get("extracted_results") or []
        val_dict = state.get("validation_result") or {}

        logger.info(f"task_id={task_id} [GRAPH:diagnosis_node] Running diagnosis agent")

        # Parse validation result
        val_result = ValidationResult(**val_dict) if val_dict else ValidationResult(status="broken", health_score=0.0)

        diagnosis: DiagnosisResult = await diagnostician.diagnose(
            task=task or ScrapingTask(task_id=task_id, objective="", target_urls=[]),
            validation_result=val_result,
            raw_results=raw_results,
            extracted_results=extracted_results,
        )

        # Attach diagnosis to final_output metadata
        final_output = state.get("final_output")
        if final_output:
            updated_meta = dict(final_output.metadata)
            updated_meta["diagnosis"] = diagnosis.model_dump()
            final_output.metadata = updated_meta
            if diagnosis.root_cause.value != "UNKNOWN":
                final_output.error = f"Degradation diagnosed: {diagnosis.root_cause.value} -> {diagnosis.repair_strategy.value}"

        return {
            "diagnosis_result": diagnosis.model_dump(),
            "final_output": final_output,
        }

    def should_diagnose(state: ScrapingGraphState) -> str:
        """Route to diagnosis node if validation reveals actionable degradation or failure."""
        val_dict = state.get("validation_result")
        if not val_dict:
            # If failed before validation
            if state.get("final_output") and state["final_output"].status == "failed":
                return "diagnose"
            return "end"

        status = val_dict.get("status", "healthy")
        failures = val_dict.get("failures", [])

        if status in ("broken", "unstable"):
            return "diagnose"
        if status == "degraded" and failures:
            return "diagnose"

        return "end"

    graph = StateGraph(ScrapingGraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("scraper", scraper_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("validation", validation_node)
    graph.add_node("diagnosis", diagnosis_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "scraper")
    graph.add_edge("scraper", "extraction")
    graph.add_edge("extraction", "validation")

    graph.add_conditional_edges(
        "validation",
        should_diagnose,
        {
            "diagnose": "diagnosis",
            "end": END,
        },
    )

    graph.add_edge("diagnosis", END)

    return graph.compile()
