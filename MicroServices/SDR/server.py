"""
SDR Microservice FastAPI Server (Port 8081).
Autonomous Website Audit, SEO Analysis, Opportunity Synthesizer, Proposal Generator, Outreach Pack, and A2A Agent.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sniffio
from starlette.middleware.base import BaseHTTPMiddleware
from .orchestrator import SDROrchestrator

app = FastAPI(
    title="AgencyOS SDR Microservice",
    description="Autonomous Web Crawling (LibreCrawl), 6-domain SEO Auditing, Prompt Generation, Opportunity Synthesis, Proposal Generation, and Outreach Preparation.",
    version="1.0.0",
)


class SniffioASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            token = sniffio.current_async_library_cvar.set("asyncio")
            try:
                await self.app(scope, receive, send)
            finally:
                sniffio.current_async_library_cvar.reset(token)
        else:
            await self.app(scope, receive, send)


app.add_middleware(SniffioASGIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = SDROrchestrator()


# Request / Response Schemas
class AuditRequest(BaseModel):
    url: str
    max_depth: int = 2
    max_pages: int = 20
    javascript: bool = False


class FullPipelineRequest(BaseModel):
    company_name: str
    website_url: Optional[str] = None
    campaign_id: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    source: str = "leadfinder+sdr"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2AInvokeRequest(BaseModel):
    skill: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    caller_agent: Optional[str] = "unknown"


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "sdr_service", "port": 8081}


@app.get("/ready", status_code=status.HTTP_200_OK)
async def ready_check():
    return {"status": "ready", "analyzers": "ready", "librecrawl": "ready"}


@app.get("/.well-known/agent.json")
async def serve_sdr_agent_card():
    """Serve A2A Agent Card for SDR Agent."""
    return {
        "name": "SDRAgent",
        "description": "Specialized autonomous agent for website crawling, technical SEO audits, digital weakness diagnosis, opportunity synthesis, proposal generation, and outreach preparation.",
        "version": "1.0.0",
        "protocol": "A2A/1.0",
        "endpoints": {
            "agent_card": "http://localhost:8081/.well-known/agent.json",
            "invoke": "http://localhost:8081/a2a/invoke",
        },
        "capabilities": [
            {
                "name": "audit_website",
                "description": "Perform deep technical and on-page SEO crawl and audit on a target domain.",
                "parameters": {"url": "string (required)", "max_pages": "integer (optional)"},
            },
            {
                "name": "execute_full_sdr_pipeline",
                "description": "Execute complete SDR workflow: Normalization -> Parallel Audit -> Opportunities -> Proposal -> Outreach Pack -> Lead Manager registration.",
                "parameters": {
                    "company_name": "string (required)",
                    "website_url": "string (optional)",
                    "primary_contact_email": "string (optional)",
                },
            },
        ],
    }


@app.post("/api/v1/audit")
async def audit_website_endpoint(request: AuditRequest):
    """Run full crawl and 6-domain SEO audit on a URL."""
    try:
        results = await orchestrator.analysis_orchestrator.run_website_seo_audit(
            url=request.url,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            javascript=request.javascript,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/pipeline/process-target")
async def process_target_endpoint(request: FullPipelineRequest):
    """
    Executes full SDR pipeline (Layers 2 through 8):
    Normalization -> Parallel Audit -> Prompt Gen -> Opportunities -> Proposal -> Outreach Pack -> Lead Manager registration.
    """
    try:
        result = await orchestrator.process_discovered_prospect(
            raw_lead_data=request.model_dump(),
            auto_dispatch_to_lead_manager=True,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/a2a/invoke")
async def invoke_a2a_skill(request: A2AInvokeRequest):
    """Execute A2A capability on SDR Agent."""
    skill = request.skill
    params = request.parameters

    if skill == "audit_website":
        res = await orchestrator.analysis_orchestrator.run_website_seo_audit(
            url=params.get("url", "")
        )
        return {"success": True, "result": res}
    elif skill in ("execute_full_sdr_pipeline", "audit_and_dispatch_lead", "process_discovered_prospect"):
        res = await orchestrator.process_discovered_prospect(
            raw_lead_data=params,
            auto_dispatch_to_lead_manager=True,
        )
        return {"success": True, "result": res}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown skill '{skill}'")
