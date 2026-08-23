"""
A2A Agent Card & Invocation Route for Lead Manager.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .skills import A2ASkillsHandler

a2a_router = APIRouter(tags=["Agent-to-Agent (A2A)"])


class A2AInvokePayload(BaseModel):
    skill: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    caller_agent: Optional[str] = "unknown"


@a2a_router.get("/.well-known/agent.json")
async def serve_agent_card():
    return {
        "name": "LeadManagerAgent",
        "description": "System of record and deterministic lifecycle controller for leads, opportunities, tasks, and meetings.",
        "version": "1.0.0",
        "protocol": "A2A/1.0",
        "endpoints": {
            "agent_card": "http://localhost:8082/.well-known/agent.json",
            "invoke": "http://localhost:8082/a2a/invoke",
        },
        "capabilities": [
            {
                "name": "create_lead",
                "description": "Register a newly discovered lead into the system of record.",
                "parameters": {"company_name": "string (required)", "website_url": "string (optional)"},
            },
            {
                "name": "ingest_event",
                "description": "Process a lifecycle event (email, audit, proposal, meeting) through the state machine.",
                "parameters": {"event_type": "string (required)", "lead_id": "string (required)"},
            },
            {
                "name": "get_lead_status",
                "description": "Query the current stage, opportunities, and tasks for a given lead.",
                "parameters": {"lead_id": "string (optional)", "email": "string (optional)"},
            },
        ],
    }


@a2a_router.post("/a2a/invoke")
async def invoke_skill(payload: A2AInvokePayload):
    skill = payload.skill
    params = payload.parameters

    if skill == "create_lead":
        result = await A2ASkillsHandler.create_lead(params)
        return {"success": True, "result": result}
    elif skill == "ingest_event":
        result = await A2ASkillsHandler.ingest_event(params)
        return {"success": True, "result": result}
    elif skill == "get_lead_status":
        result = await A2ASkillsHandler.get_lead_status(params)
        return {"success": True, "result": result}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown skill '{skill}'")
