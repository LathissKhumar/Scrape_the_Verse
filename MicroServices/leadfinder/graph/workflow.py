from typing import Any, Optional
from langgraph.graph import END, START, StateGraph

from leadfinder.agents.diagnosis import DiagnosisAgent
from leadfinder.agents.extraction import ExtractionAgent
from leadfinder.agents.healing import HealingAgent
from leadfinder.agents.planner import ScrapingPlannerAgent
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.agents.validation import ValidationAgent
from leadfinder.brightdata.client import BrightDataClient
from leadfinder.config.logging import get_logger
from leadfinder.config.settings import get_settings
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import ExtractionResult, ExtractionSchema
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.healing.schemas import RepairEvaluation, RepairPlan, RepairType
from leadfinder.llm.ollama_client import OllamaClient
from leadfinder.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("GRAPH")


def create_scraping_workflow(
    planner_agent: Optional[ScrapingPlannerAgent] = None,
    scraper_agent: Optional[ScraperAgent] = None,
    extraction_agent: Optional[ExtractionAgent] = None,
    validation_agent: Optional[ValidationAgent] = None,
    diagnosis_agent: Optional[DiagnosisAgent] = None,
    healing_agent: Optional[HealingAgent] = None,
):
    """Build and compile the Phase 5 LangGraph scraping state machine with autonomous self-healing feedback loop:

    START -> planner -> scraper -> extraction -> validation
                                                    |
                                            [should_repair?]
                                            /              \
                                          NO (healthy)     YES (broken/degraded)
                                          |                 |
                                         END            diagnosis
                                                            |
                                                    [should_heal?]
                                                    /            \
                                          NO (escalate/source)   YES (confident)
                                          |                       |
                                       escalate                healing
                                          |                       |
                                         END              [accepted?]
                                                         /           \
                                                      YES             NO (escalate/exhausted)
                                                      |                |
                                                     END            escalate -> END
    """
    settings = get_settings()
    llm = OllamaClient(settings=settings)
    planner = planner_agent or ScrapingPlannerAgent(llm_client=llm)
    brightdata = BrightDataClient(settings=settings)
    scraper = scraper_agent or ScraperAgent(brightdata_client=brightdata)
    extractor = extraction_agent or ExtractionAgent(llm_client=llm)
    validator = validation_agent or ValidationAgent()
    diagnostician = diagnosis_agent or DiagnosisAgent(llm_client=llm)
    healer = healing_agent or HealingAgent(
        llm_client=llm,
        scraper_agent=scraper,
        extraction_engine=extractor,
        validation_engine=validator,
    )

    async def planner_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        query = state.get("original_user_query", "")
        supplied_urls = state.get("target_urls", [])

        logger.debug(f"task_id={task_id} [GRAPH:planner_node] Running planner agent")

        request = ScrapingRequest(
            query=query,
            target_urls=supplied_urls,
        )

        task: ScrapingTask = await planner.plan_async(request=request, task_id=task_id)

        # Scraper provider tag
        provider = "brightdata" if getattr(scraper, "is_brightdata", False) else "local"

        return {
            "scraping_task": task,
            "target_urls": task.target_urls,
            "scraper_provider": provider,
        }

    async def scraper_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")

        logger.debug(f"task_id={task_id} [GRAPH:scraper_node] Running scraper agent")

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
                metadata={"task_id": task_id, "record_count": 0, "scraper_provider": state.get("scraper_provider", "local")},
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
                metadata={"task_id": task_id, "record_count": 0, "scraper_provider": state.get("scraper_provider", "local")},
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

        logger.debug(f"task_id={task_id} [GRAPH:extraction_node] Running extraction agent")

        if not raw_results:
            empty_msg = "No raw content retrieved for extraction."
            logger.warning(f"task_id={task_id} {empty_msg}")
            return {
                "extracted_results": [],
            }

        try:
            # Check if an updated candidate extraction schema is in state
            schema_dict = state.get("extraction_schema")
            schema_obj = ExtractionSchema(**schema_dict) if schema_dict else None

            extraction_result: ExtractionResult = await extractor.extract(
                raw_results=raw_results,
                task=task,
                schema=schema_obj,
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

        logger.debug(f"task_id={task_id} [GRAPH:validation_node] Running validation agent")

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
            err_str = f"Validation detected quality degradation: health_score={validation_result.health_score:.2f}"
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
                "scraper_provider": state.get("scraper_provider", "local"),
                "anomalies": validation_result.anomalies,
                "validation": {
                    "field_coverage": {
                        k: v.coverage for k, v in validation_result.field_metrics.items()
                    },
                    "duplicate_rate": validation_result.duplicate_metrics.duplicate_rate if validation_result.duplicate_metrics else 0.0,
                    "url_valid_rate": validation_result.url_metrics.valid_rate if validation_result.url_metrics else 1.0,
                    "schema_valid_rate": validation_result.schema_metrics.valid_rate if validation_result.schema_metrics else 1.0,
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

        logger.debug(f"task_id={task_id} [GRAPH:diagnosis_node] Running diagnosis agent")

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

    async def healing_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        task: Optional[ScrapingTask] = state.get("scraping_task")
        raw_results = state.get("raw_results")
        val_dict = state.get("validation_result") or {}
        diag_dict = state.get("diagnosis_result") or {}
        schema_dict = state.get("extraction_schema")

        logger.debug(f"task_id={task_id} [GRAPH:healing_node] Running healing agent")

        val_result = ValidationResult(**val_dict) if val_dict else ValidationResult(status="broken", health_score=0.0)
        diag_result = DiagnosisResult(**diag_dict) if diag_dict else DiagnosisResult(root_cause=RootCause.UNKNOWN)
        current_schema = ExtractionSchema(**schema_dict) if schema_dict else ExtractionSchema()

        success, healed_schema, evaluation, healed_records, history = await healer.heal(
            task=task or ScrapingTask(task_id=task_id, objective="", target_urls=[]),
            diagnosis=diag_result,
            validation=val_result,
            current_schema=current_schema,
            raw_results=raw_results,
        )

        final_output = state.get("final_output")
        if not final_output:
            final_output = ScrapingResult(task_id=task_id, status="failed", records=[])

        updated_meta = dict(final_output.metadata)
        updated_meta["repair_history"] = history
        updated_meta["repair_attempts"] = len(history)
        updated_meta["health_before"] = evaluation.before.health
        updated_meta["health_after"] = evaluation.after.health

        if success and evaluation.accepted:
            final_output.status = "success"
            final_output.records = healed_records
            final_output.error = None
            updated_meta["self_healed"] = True
            updated_meta["health_score"] = evaluation.after.health
            updated_meta["quality_score"] = evaluation.after.quality
            updated_meta["record_count"] = len(healed_records)
            repair_type_val = history[-1]["repair_type"] if history else "REPAIR_CSS_SELECTORS"
            updated_meta["repair_type"] = repair_type_val
        else:
            final_output.status = "failed" if not healed_records else "partial"
            final_output.error = "Unable to recover scraper after bounded repair attempts"
            updated_meta["self_healed"] = False
            updated_meta["escalated"] = True

        final_output.metadata = updated_meta

        return {
            "final_output": final_output,
            "extraction_schema": healed_schema.model_dump() if healed_schema else None,
            "repair_evaluation": evaluation.model_dump(),
            "repair_history": history,
            "repair_attempt": state.get("repair_attempt", 0) + len(history),
            "extracted_results": healed_records,
        }

    async def escalate_node(state: ScrapingGraphState) -> dict[str, Any]:
        task_id = state.get("task_id", "unknown-task")
        final_output = state.get("final_output")
        if not final_output:
            final_output = ScrapingResult(task_id=task_id, status="failed", records=[])

        diag_dict = state.get("diagnosis_result") or {}
        diag = DiagnosisResult(**diag_dict) if diag_dict else None

        updated_meta = dict(final_output.metadata)
        updated_meta["self_healed"] = False
        updated_meta["escalated"] = True
        updated_meta["escalation_reason"] = (
            f"Diagnosis inconclusive (confidence={diag.confidence:.2f}, root_cause={diag.root_cause.value})"
            if diag
            else "Unrecoverable failure detected"
        )
        final_output.metadata = updated_meta
        logger.warning(f"Escalation triggered | task_id={task_id} | reason={updated_meta['escalation_reason']}")

        return {"final_output": final_output}

    def should_repair(state: ScrapingGraphState) -> str:
        """Route from validation: check if repair is actually justified."""
        val_dict = state.get("validation_result")
        if not val_dict:
            if state.get("final_output") and state["final_output"].status == "failed":
                return "diagnose"
            return "end"

        status = val_dict.get("status", "healthy")
        health = val_dict.get("health_score", 1.0)
        failures = val_dict.get("failures", [])

        if status == "healthy" and health >= 0.80:
            return "end"

        # Check if attempts exceeded budget
        attempts = state.get("repair_attempt", 0)
        if attempts >= 3:
            return "end"

        if status in ("broken", "unstable") or (status == "degraded" and failures):
            return "diagnose"

        return "end"

    def should_heal(state: ScrapingGraphState) -> str:
        """Route from diagnosis: verify if repair is possible or if it must escalate / end."""
        diag_dict = state.get("diagnosis_result")
        if not diag_dict:
            return "escalate"

        root_cause = diag_dict.get("root_cause", "UNKNOWN")
        confidence = diag_dict.get("confidence", 0.0)

        # Source data quality issues are not scraper failures -> bypass healing to end
        if root_cause == RootCause.SOURCE_DATA_QUALITY.value:
            logger.info("Diagnosis identified SOURCE_DATA_QUALITY. Bypassing repair.")
            return "end"

        # Low confidence or unknown cause -> escalate
        if confidence < 0.50 or root_cause == RootCause.UNKNOWN.value:
            logger.info(f"Diagnosis confidence too low ({confidence:.2f}) or UNKNOWN. Escalating.")
            return "escalate"

        return "heal"

    graph = StateGraph(ScrapingGraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("scraper", scraper_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("validation", validation_node)
    graph.add_node("diagnosis", diagnosis_node)
    graph.add_node("healing", healing_node)
    graph.add_node("escalate", escalate_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "scraper")
    graph.add_edge("scraper", "extraction")
    graph.add_edge("extraction", "validation")

    graph.add_conditional_edges(
        "validation",
        should_repair,
        {
            "diagnose": "diagnosis",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "diagnosis",
        should_heal,
        {
            "heal": "healing",
            "escalate": "escalate",
            "end": END,
        },
    )

    graph.add_edge("healing", END)
    graph.add_edge("escalate", END)

    return graph.compile()
