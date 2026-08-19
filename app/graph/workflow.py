from typing import Any, Optional
from langgraph.graph import END, START, StateGraph

from app.agents.extraction import ExtractionAgent
from app.agents.planner import ScrapingPlannerAgent
from app.agents.scraper import ScraperAgent
from app.brightdata.client import BrightDataClient
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionResult
from app.graph.state import ScrapingGraphState
from app.llm.ollama_client import OllamaClient
from app.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask

logger = get_logger("GRAPH")


def create_scraping_workflow(
    planner_agent: Optional[ScrapingPlannerAgent] = None,
    scraper_agent: Optional[ScraperAgent] = None,
    extraction_agent: Optional[ExtractionAgent] = None,
):
    """Build and compile the Phase 2 LangGraph scraping state machine:

    START -> planner -> scraper -> extraction -> END
    """
    settings = get_settings()
    llm = OllamaClient(settings=settings)
    planner = planner_agent or ScrapingPlannerAgent(llm_client=llm)
    scraper = scraper_agent or ScraperAgent(brightdata_client=BrightDataClient(settings=settings))
    extractor = extraction_agent or ExtractionAgent(llm_client=llm)

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

        # If previous step already produced a failure final_output, keep it
        if state.get("final_output") and state["final_output"].status == "failed":
            return {}

        logger.info(f"task_id={task_id} [GRAPH:extraction_node] Running extraction agent")

        if not raw_results:
            empty_msg = "No raw content retrieved for extraction."
            logger.warning(f"task_id={task_id} {empty_msg}")
            final_res = ScrapingResult(
                task_id=task_id,
                status="partial",
                records=[],
                metadata={"task_id": task_id, "record_count": 0},
                error=empty_msg,
            )
            return {
                "extracted_results": [],
                "final_output": final_res,
            }

        try:
            extraction_result: ExtractionResult = await extractor.extract(
                raw_results=raw_results,
                task=task,
            )

            records = extraction_result.records
            status = "success" if records else "partial"
            final_res = ScrapingResult(
                task_id=task_id,
                status=status,
                records=records,
                metadata={
                    "task_id": task_id,
                    "record_count": len(records),
                    "extraction_strategy": extraction_result.strategy_used,
                    "fallback_used": extraction_result.fallback_used,
                    **extraction_result.metadata,
                },
                error=None if records else "No structured records extracted",
            )

            return {
                "extracted_results": records,
                "final_output": final_res,
            }
        except Exception as e:
            logger.error(f"task_id={task_id} Extraction failure: {e}")
            failure_info = {
                "failure_type": "EXTRACTION_FAILURE",
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

    graph = StateGraph(ScrapingGraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("scraper", scraper_node)
    graph.add_node("extraction", extraction_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "scraper")
    graph.add_edge("scraper", "extraction")
    graph.add_edge("extraction", END)

    return graph.compile()
