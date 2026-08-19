from typing import Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.agents.planner import ScrapingPlannerAgent, extract_urls_from_text
from app.agents.scraper import ScraperAgent
from app.brightdata.client import BrightDataClient
from app.brightdata.exceptions import (
    BrightDataAuthError,
    BrightDataConfigError,
    BrightDataEmptyResultError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from app.config.logging import get_logger, setup_logging
from app.config.settings import get_settings
from app.graph.state import ScrapingGraphState
from app.graph.workflow import create_scraping_workflow
from app.llm.exceptions import (
    LLMConnectionError,
    LLMError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)
from app.llm.ollama_client import OllamaClient
from app.models.schemas import ScrapingRequest, ScrapingResult

setup_logging()
logger = get_logger("API")
settings = get_settings()

app = FastAPI(
    title="Self-Healing Multi-Agent Web Scraper",
    description="Multi-agent self-healing web scraper with LangGraph, local Ollama Qwen3:8b, and Bright Data.",
    version="0.2.0",
)

# Initialize core clients and agents
llm_client = OllamaClient(settings=settings)
brightdata_client = BrightDataClient(settings=settings)
planner_agent = ScrapingPlannerAgent(llm_client=llm_client)
scraper_agent = ScraperAgent(brightdata_client=brightdata_client)

# Initialize compiled LangGraph workflow
workflow = create_scraping_workflow(
    planner_agent=planner_agent,
    scraper_agent=scraper_agent,
)


@app.exception_handler(LLMConnectionError)
async def llm_connection_error_handler(request, exc: LLMConnectionError):
    logger.error(f"LLM connection error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "error_type": "LLMConnectionError"},
    )


@app.exception_handler(LLMModelNotFoundError)
async def llm_model_not_found_handler(request, exc: LLMModelNotFoundError):
    logger.error(f"LLM model not found error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "error_type": "LLMModelNotFoundError"},
    )


@app.exception_handler(LLMTimeoutError)
async def llm_timeout_handler(request, exc: LLMTimeoutError):
    logger.error(f"LLM timeout error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": str(exc), "error_type": "LLMTimeoutError"},
    )


@app.exception_handler(LLMError)
async def llm_generic_error_handler(request, exc: LLMError):
    logger.error(f"LLM error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "error_type": "LLMError"},
    )


@app.exception_handler(BrightDataConfigError)
async def brightdata_config_error_handler(request, exc: BrightDataConfigError):
    logger.error(f"Bright Data configuration error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "error_type": "BrightDataConfigError"},
    )


@app.exception_handler(BrightDataAuthError)
async def brightdata_auth_error_handler(request, exc: BrightDataAuthError):
    logger.error(f"Bright Data authentication error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "error_type": "BrightDataAuthError"},
    )


@app.exception_handler(BrightDataError)
async def brightdata_generic_error_handler(request, exc: BrightDataError):
    logger.error(f"Bright Data error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc), "error_type": "BrightDataError"},
    )


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint returning service info and current phase."""
    logger.info("Handling GET /")
    return {
        "service": "self-healing-scraper",
        "status": "running",
        "phase": 2,
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    """Service and configuration health check."""
    logger.info("Handling GET /health")
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "brightdata_configured": brightdata_client.is_configured,
    }


@app.get("/health/llm")
async def health_llm() -> dict[str, Any]:
    """Lightweight health check inspecting Ollama reachability and configured model presence."""
    logger.info("Handling GET /health/llm")
    health_info = await llm_client.check_health()
    if not health_info.get("available") or not health_info.get("model_installed"):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_info,
        )
    return health_info


@app.post("/parse-task")
async def parse_task(request: ScrapingRequest) -> dict[str, Any]:
    """Convert a plain-language scraping request into a structured ScrapingTask."""
    task_id = str(uuid4())
    logger.info(f"POST /parse-task received. Assigned task_id: {task_id}")

    try:
        task = await planner_agent.plan_async(request=request, task_id=task_id)
        return {
            "task_id": task_id,
            "scraping_task": task.model_dump(),
        }
    except LLMError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing scraping task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse scraping task: {str(e)}",
        )


@app.post("/scrape")
async def scrape(request: ScrapingRequest) -> dict[str, Any]:
    """Execute end-to-end web scraping workflow via LangGraph orchestration."""
    # Check that URLs were provided either in target_urls or embedded in query text
    query_urls = extract_urls_from_text(request.query)
    combined_urls = list(request.target_urls)
    for u in query_urls:
        if u not in combined_urls:
            combined_urls.append(u)

    if not combined_urls:
        err_msg = "No target URL was supplied. URL discovery is not implemented."
        logger.error(f"POST /scrape rejected: {err_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )

    task_id = str(uuid4())
    logger.info(f"POST /scrape received. Assigned task_id: {task_id} with {len(combined_urls)} URL(s)")

    initial_state: ScrapingGraphState = {
        "task_id": task_id,
        "original_user_query": request.query,
        "target_urls": combined_urls,
        "repair_attempt": 0,
    }

    try:
        final_state = await workflow.ainvoke(initial_state)
        result: Optional[ScrapingResult] = final_state.get("final_output")
        if not result:
            result = ScrapingResult(
                task_id=task_id,
                status="failed",
                records=[],
                error="Workflow completed without generating final output.",
            )
        else:
            result.task_id = task_id

        return result.model_dump()

    except Exception as e:
        logger.error(f"Error during workflow execution for task_id={task_id}: {e}")
        return {
            "task_id": task_id,
            "status": "failed",
            "records": [],
            "metadata": {"task_id": task_id},
            "error": str(e),
        }
