"""
Lead Pipeline Client for Lead Finder.
Dispatches discovered targets to SDR (:8081), Voice Agent (:8084), and Lead Manager (:8082).
"""

from typing import Any

import httpx


class LeadPipelineClient:
    def __init__(
        self,
        sdr_url: str = "http://127.0.0.1:8081",
        lead_manager_url: str = "http://127.0.0.1:8082",
        voice_agent_url: str = "http://127.0.0.1:8084",
    ):
        self.sdr_url = sdr_url.rstrip("/")
        self.lead_manager_url = lead_manager_url.rstrip("/")
        self.voice_agent_url = voice_agent_url.rstrip("/")

    async def audit_and_forward_to_lead_manager(
        self,
        company_name: str,
        website_url: str | None = None,
        campaign_id: str | None = None,
        primary_contact_name: str | None = None,
        primary_contact_email: str | None = None,
        primary_contact_phone: str | None = None,
        industry: str | None = None,
        location: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Sends discovered company to SDR (:8081) for normalization, parallel audit,
        opportunity matching, proposal creation, outreach pack generation,
        and persistence in Lead Manager (:8082).
        """
        payload = {
            "company_name": company_name,
            "website_url": website_url,
            "campaign_id": campaign_id,
            "primary_contact_name": primary_contact_name,
            "primary_contact_email": primary_contact_email,
            "primary_contact_phone": primary_contact_phone,
            "industry": industry,
            "location": location,
            "source": "leadfinder",
            "metadata": metadata or {},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.sdr_url}/api/v1/pipeline/process-target",
                json=payload,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"SDR audit & dispatch failed ({resp.status_code}): {resp.text}"
                )
            return resp.json()
