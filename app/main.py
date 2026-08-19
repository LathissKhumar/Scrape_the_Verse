from typing import Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.agents.planner import ScrapingPlannerAgent
from app.config.logging import get_logger, setup_logging
from app.config.settings import get_settings
from app.llm.exceptions import (
    LLMConnectionError,
    LLMError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)
from app.llm.ollama_client import OllamaClient
from app.models.schemas import ScrapingRequest

setup_logging()
logger = get_logger("API")
settings = get_settings()

app = FastAPI(
    title="Self-Healing Multi-Agent Web Scraper",
    description="Foundational multi-agent self-healing web scraper with LangGraph and local Ollama Qwen3:8b.",
    version="0.1.0",
)

# Initialize LLM client and planner agent
llm_client = OllamaClient(settings=settings)
planner_agent = ScrapingPlannerAgent(llm_client=llm_client)


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


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint returning basic service info and current phase."""
    logger.info("Handling GET /")
    return {
        "service": "self-healing-scraper",
        "status": "running",
        "phase": 1,
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
        "brightdata_configured": bool(settings.BRIGHTDATA_API_KEY),
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
