from typing import Any, Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.agents.gmaps import GoogleMapsAgent
from app.agents.healing import HealingAgent
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
from app.brightdata.schemas import (
    CollectorStatus,
    ScrapeTargetRequest,
    ScraperHealRequest,
    ScraperHealResponse,
    ScraperResolveResponse,
    ScraperRunRequest,
    ScraperRunResponse,
)
from app.brightdata.service import BrightDataService
from app.config.logging import get_logger, setup_logging
from app.config.settings import get_settings
from app.gmaps.service import GoogleMapsService
from app.graph.state import ScrapingGraphState
from app.graph.workflow import create_scraping_workflow
from app.llm.exceptions import (
    LLMConnectionError,
    LLMError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)
from app.llm.ollama_client import OllamaClient
from app.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask

setup_logging()
logger = get_logger("API")
settings = get_settings()

app = FastAPI(
    title="Self-Healing Multi-Agent Web Scraper",
    description="Multi-agent self-healing web scraper with LangGraph, local Ollama Qwen3:8b, Bright Data, and Google Maps agent.",
    version="0.5.0",
)

# Initialize core clients and agents
llm_client = OllamaClient(settings=settings)
brightdata_client = BrightDataClient(settings=settings)
brightdata_service = BrightDataService(settings=settings, client=brightdata_client)
gmaps_service = GoogleMapsService(settings=settings, client=brightdata_client)
gmaps_agent = GoogleMapsAgent(service=gmaps_service, llm_client=llm_client, settings=settings)
planner_agent = ScrapingPlannerAgent(llm_client=llm_client)
scraper_agent = ScraperAgent(brightdata_client=brightdata_client)
healing_agent = HealingAgent(llm_client=llm_client, scraper_agent=scraper_agent)

# Initialize compiled LangGraph workflow
workflow = create_scraping_workflow(
    planner_agent=planner_agent,
    scraper_agent=scraper_agent,
    healing_agent=healing_agent,
)


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> None:
    """Verify API key if API_SECRET_KEY is configured in settings."""
    secret = settings.API_SECRET_KEY
    if not secret:
        return
    token = x_api_key
    if not token and authorization:
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()
    if not token or token != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide 'X-API-Key' or 'Authorization: Bearer <key>'.",
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
        "phase": 5,
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


from app.crawler.job_manager import default_job_manager
from app.export.exporter import DataExporter


async def _run_background_workflow(task_id: str, query: str, urls: list[str]):
    """Execute scraping workflow in background with progress and checkpoint tracking."""
    default_job_manager.create_job(job_id=task_id, query=query, total_urls=len(urls))
    default_job_manager.update_job_status(task_id, status="running")
    initial_state: ScrapingGraphState = {
        "task_id": task_id,
        "original_user_query": query,
        "target_urls": urls,
        "repair_attempt": 0,
    }
    try:
        final_state = await workflow.ainvoke(initial_state)
        result: Optional[ScrapingResult] = final_state.get("final_output")
        if result and result.records:
            default_job_manager.record_checkpoint(
                job_id=task_id,
                url="aggregated_results",
                status="completed",
                records=result.records,
            )
            default_job_manager.update_job_status(task_id, status="completed")
        else:
            err = result.error if result else "Workflow completed without records"
            default_job_manager.update_job_status(task_id, status="failed", error=err)
    except Exception as e:
        logger.error(f"Background job execution failed for {task_id}: {e}")
        default_job_manager.update_job_status(task_id, status="failed", error=str(e))


@app.post("/scrape", dependencies=[Depends(verify_api_key)])
async def scrape(request: ScrapingRequest) -> Any:
    """Execute end-to-end web scraping workflow via LangGraph orchestration or smart lead routing."""
    # Check that URLs were provided either in target_urls or embedded in query text
    query_urls = extract_urls_from_text(request.query)
    combined_urls = list(request.target_urls)
    for u in query_urls:
        if u not in combined_urls:
            combined_urls.append(u)

    if not combined_urls:
        query_text = (request.query or "").strip()
        lower_query = query_text.lower()
        is_generic_command = lower_query.startswith("scrape ") or lower_query.startswith("extract ") or "without" in lower_query or "no url" in lower_query
        is_explicit_lead_req = bool(request.metadata and (request.metadata.get("leads") or request.metadata.get("b2b")))
        is_b2b_query = (
            brightdata_service.is_enabled
            and not is_generic_command
            and (is_explicit_lead_req or any(w in lower_query for w in [" in ", " near ", "supplier", "manufacturer", "dealer", "wholesale", "exporter", "trader"]))
        )

        if gmaps_service.is_enabled and gmaps_agent.is_gmaps_query(query_text) and not is_generic_command:
            task_id = str(uuid4())
            logger.info(f"task_id={task_id} POST /scrape auto-routing keyword-only request to GoogleMapsService: '{query_text}'")
            cat, loc = gmaps_agent.parse_query_and_location(query_text)
            leads = await gmaps_service.get_local_leads(query=cat, location=loc)
            return {
                "task_id": task_id,
                "status": "success" if leads else "empty",
                "records": leads,
                "metadata": {
                    "task_id": task_id,
                    "record_count": len(leads),
                    "scraper_provider": "brightdata_gmaps",
                    "category": cat,
                    "location": loc,
                },
            }
        elif is_b2b_query:
            task_id = str(uuid4())
            logger.info(f"task_id={task_id} POST /scrape auto-routing keyword-only request to BrightDataLeadPipeline: '{query_text}'")
            enrich = request.metadata.get("enrich", True) if request.metadata else True
            leads = await brightdata_service.generate_leads(query=query_text, enrich_profiles=enrich)
            return {
                "task_id": task_id,
                "status": "success" if leads else "empty",
                "records": leads,
                "metadata": {
                    "task_id": task_id,
                    "record_count": len(leads),
                    "scraper_provider": "brightdata_b2b",
                },
            }
        else:
            err_msg = "No target URL was supplied. URL discovery is not implemented."
            logger.error(f"POST /scrape rejected: {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg,
            )

    task_id = str(uuid4())
    logger.info(f"POST /scrape received. Assigned task_id: {task_id} with {len(combined_urls)} URL(s)")

    # Check dual-engine routing: Bright Data Fast-Path vs Native Multi-Agent Engine
    provider = str(request.metadata.get("scraper_provider") or settings.SCRAPER_PROVIDER or "auto").lower()
    is_brightdata_target = any("indiamart" in u.lower() for u in combined_urls) if combined_urls else False
    use_brightdata = (brightdata_service.is_enabled and (provider == "brightdata" or (provider == "auto" and is_brightdata_target))) or provider == "brightdata"

    if use_brightdata and provider != "local":
        logger.info(f"task_id={task_id} Routing to Bright Data Fast-Path (BRIGHTDATA=True)")
        task = ScrapingTask(
            task_id=task_id,
            objective=request.query,
            target_urls=combined_urls,
            metadata=request.metadata,
        )
        try:
            result = await brightdata_service.execute_task(task)
            if result and result.status == "success" and result.records:
                return result.model_dump()
            logger.info(f"task_id={task_id} Bright Data fast-path returned no records. Engaging Native Multi-Agent fallback...")
        except Exception as e:
            logger.warning(f"Bright Data fast-path error ({e}). Falling back to Native Multi-Agent engine...")

    # If caller requested async_job or large URL batch, execute in background
    if request.async_job:
        asyncio.create_task(_run_background_workflow(task_id, request.query, combined_urls))
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "task_id": task_id,
                "job_id": task_id,
                "status": "queued",
                "total_urls": len(combined_urls),
                "message": "Scraping task accepted for background execution",
                "status_url": f"/api/v1/jobs/{task_id}",
            },
        )

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


@app.post("/api/v1/brightdata/leads", dependencies=[Depends(verify_api_key)])
async def generate_brightdata_leads(request: ScrapingRequest) -> dict[str, Any]:
    """Dedicated endpoint for B2B lead generation using chained Bright Data collectors."""
    if not brightdata_service.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bright Data is not enabled. Set BRIGHTDATA=True and provide BRIGHTDATA_API_KEY in .env.",
        )

    query = request.query or (request.target_urls[0] if request.target_urls else "solar panels")
    enrich = request.metadata.get("enrich", True) if request.metadata else True

    leads = await brightdata_service.generate_leads(query=query, enrich_profiles=enrich)
    return {
        "query": query,
        "total_leads": len(leads),
        "leads": leads,
    }


@app.post("/api/v1/gmaps/leads", dependencies=[Depends(verify_api_key)])
async def generate_gmaps_leads(request: ScrapingRequest) -> dict[str, Any]:
    """Dedicated endpoint for discovering local business leads from Google Maps."""
    if not gmaps_service.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bright Data is not enabled. Set BRIGHTDATA=True and provide BRIGHTDATA_API_KEY in .env.",
        )

    query = request.query or "plumbers in Chennai"
    category, location = gmaps_agent.parse_query_and_location(query)
    leads = await gmaps_service.get_local_leads(query=category, location=location)
    return {
        "query": query,
        "category": category,
        "location": location,
        "total_leads": len(leads),
        "leads": leads,
    }


@app.post("/api/v1/jobs", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_api_key)])
async def create_scraping_job(request: ScrapingRequest) -> dict[str, Any]:
    """Submit a long-running scraping task to execute asynchronously in the background."""
    query_urls = extract_urls_from_text(request.query)
    combined_urls = list(request.target_urls)
    for u in query_urls:
        if u not in combined_urls:
            combined_urls.append(u)

    if not combined_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No target URL was supplied.",
        )

    job_id = str(uuid4())
    logger.info(f"POST /api/v1/jobs accepted job_id: {job_id} for {len(combined_urls)} URLs")
    asyncio.create_task(_run_background_workflow(job_id, request.query, combined_urls))

    return {
        "job_id": job_id,
        "status": "queued",
        "total_urls": len(combined_urls),
        "status_url": f"/api/v1/jobs/{job_id}",
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str) -> dict[str, Any]:
    """Check progress, status, and record counts for an asynchronous scraping job."""
    progress = default_job_manager.get_job(job_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return progress.model_dump()


@app.get("/api/v1/jobs/{job_id}/results")
async def get_job_results(job_id: str, format: str = "json") -> Any:
    """Retrieve extracted records for a completed job in JSON, CSV, or NDJSON format."""
    progress = default_job_manager.get_job(job_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    records = default_job_manager.get_job_records(job_id)
    fmt = format.lower().strip()

    if fmt == "csv":
        csv_str = DataExporter.to_csv(records)
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=csv_str, media_type="text/csv")
    elif fmt == "ndjson":
        ndjson_str = DataExporter.to_ndjson(records)
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=ndjson_str, media_type="application/x-ndjson")
    else:
        return {
            "job_id": job_id,
            "status": progress.status,
            "total_records": len(records),
            "records": records,
        }


# =====================================================================
# DYNAMIC BRIGHT DATA COLLECTOR MANAGEMENT ENDPOINTS
# =====================================================================


@app.post("/scrapers/resolve", response_model=ScraperResolveResponse, dependencies=[Depends(verify_api_key)])
@app.post("/api/v1/brightdata/resolve", response_model=ScraperResolveResponse, dependencies=[Depends(verify_api_key)])
async def resolve_scraper(request: ScrapeTargetRequest) -> ScraperResolveResponse:
    """Resolve target URL + schema against Scraper Registry to reuse or trigger async creation."""
    return await brightdata_service.resolve_scraper(request)


@app.get("/scrapers/jobs/{job_id}", dependencies=[Depends(verify_api_key)])
@app.get("/api/v1/brightdata/jobs/{job_id}", dependencies=[Depends(verify_api_key)])
async def get_scraper_job(job_id: str) -> dict[str, Any]:
    """Inspect status of an asynchronous Bright Data scraper creation job."""
    job = brightdata_service.jobs.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper creation job '{job_id}' not found.",
        )
    return {
        "job_id": job.job_id,
        "scraper_id": job.scraper_id,
        "status": job.status.value.lower(),
        "collector_id": job.collector_id,
        "error": job.error,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@app.post("/scrapers/run", response_model=ScraperRunResponse, dependencies=[Depends(verify_api_key)])
@app.post("/api/v1/brightdata/run", response_model=ScraperRunResponse, dependencies=[Depends(verify_api_key)])
async def run_scraper(request: ScraperRunRequest) -> ScraperRunResponse:
    """Run a ready Bright Data Collector against a target URL."""
    return await brightdata_service.run_collector(
        collector_id=request.collector_id,
        url=request.url,
        timeout_seconds=request.timeout_seconds or 120.0,
    )


@app.post("/scrapers/heal", response_model=ScraperHealResponse, dependencies=[Depends(verify_api_key)])
@app.post("/api/v1/brightdata/heal", response_model=ScraperHealResponse, dependencies=[Depends(verify_api_key)])
async def heal_scraper(request: ScraperHealRequest) -> ScraperHealResponse:
    """Self-heal a broken Bright Data collector using failure description."""
    return await brightdata_service.heal_collector(
        collector_id=request.collector_id,
        failure_description=request.failure_description,
    )


@app.get("/scrapers", dependencies=[Depends(verify_api_key)])
@app.get("/api/v1/brightdata/scrapers", dependencies=[Depends(verify_api_key)])
async def list_scrapers(limit: int = 50, status_filter: Optional[str] = None) -> dict[str, Any]:
    """List tracked Bright Data collectors in the registry."""
    status_enum = CollectorStatus(status_filter.upper()) if status_filter else None
    records = brightdata_service.registry.list_records(limit=limit, status=status_enum)
    return {
        "total": len(records),
        "scrapers": [r.model_dump() for r in records],
    }


@app.get("/scrapers/{scraper_id_or_collector_id}", dependencies=[Depends(verify_api_key)])
async def get_scraper(scraper_id_or_collector_id: str) -> dict[str, Any]:
    """Retrieve details of a specific scraper by internal ID or collector ID."""
    rec = brightdata_service.registry.get_record_by_id(scraper_id_or_collector_id)
    if not rec:
        rec = brightdata_service.registry.get_record_by_collector_id(scraper_id_or_collector_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper '{scraper_id_or_collector_id}' not found in registry.",
        )
    return rec.model_dump()
