"""
Master SDR Orchestrator (AgencyOS AI SDR Architecture).
Connects Normalization -> Parallel Analysis (SEO + Business) -> Prompt Generation ->
Opportunity Engine -> Proposal Generator -> Outreach Preparation -> Lead Manager & Voice Agent.
"""

import os
import sys
from typing import Any, Dict, List, Optional
import httpx

_current_dir = os.path.dirname(os.path.abspath(__file__))
_seo_dir = os.path.join(_current_dir, "seo")
_workspace_root = os.path.dirname(os.path.dirname(_current_dir))

for _p in (_current_dir, _seo_dir, _workspace_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from MicroServices.SDR.analysis_orchestrator import AnalysisOrchestrator
from MicroServices.SDR.normalizer import DataNormalizer
from MicroServices.SDR.opportunity_engine import OpportunityEngine, SelectedOffer
from MicroServices.SDR.outreach_preparer import OmnichannelOutreachPack, OutreachPreparer
from MicroServices.SDR.prompt_generator import PersonalizedPromptPack, PromptGenerator
from MicroServices.SDR.proposal_generator import ProposalDocument, ProposalGenerator


class SDROrchestrator:
    def __init__(
        self,
        lead_manager_url: str = "http://127.0.0.1:8082",
        voice_agent_url: str = "http://127.0.0.1:8084",
    ):
        self.lead_manager_url = lead_manager_url.rstrip("/")
        self.voice_agent_url = voice_agent_url.rstrip("/")
        self.analysis_orchestrator = AnalysisOrchestrator()
        self.prompt_generator = PromptGenerator()

    async def process_discovered_prospect(
        self,
        raw_lead_data: Dict[str, Any],
        auto_dispatch_to_lead_manager: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the entire 10-layer AI SDR intelligence pipeline for a prospect.
        """
        # 1. Layer 2: In-Flight Data Normalization
        normalized = DataNormalizer.normalize_lead(raw_lead_data)
        company_name = normalized["company_name"]
        website_url = normalized["website_url"]
        has_website = normalized["has_website"]
        location = normalized["location"]
        industry = normalized["industry"]

        # 2. Layer 3: True Parallel Analysis (SEO + Business with Live Web Search)
        analysis_result = await self.analysis_orchestrator.run_parallel_analysis(
            company_name=company_name,
            website_url=website_url,
            location=location,
            industry=industry,
        )
        seo_data = analysis_result.get("seo_analysis", {})
        business_data = analysis_result.get("business_analysis", {})

        # 3. Layer 4: Prompt Generation Layer
        prompt_pack = await self.prompt_generator.generate_sales_context(
            company_name=company_name,
            website_url=website_url,
            industry=industry,
            location=location,
            seo_data=seo_data,
            business_data=business_data,
        )

        # 4. Layer 5: Opportunity Engine (Agency Service Catalog Matching)
        offers = OpportunityEngine.evaluate_opportunities(
            seo_data=seo_data,
            business_data=business_data,
            has_website=has_website,
        )
        recommended_services = [o.service_title for o in offers if o.recommended]
        top_opportunity_score = max((o.priority_score for o in offers), default=75.0)

        # 5. Layer 6: Proposal Generator (Markdown / PDF Deliverable)
        proposal = ProposalGenerator.generate_proposal(
            company_name=company_name,
            website_url=website_url,
            prompt_pack=prompt_pack,
            offers=offers,
            seo_data=seo_data,
            business_data=business_data,
        )

        # 6. Layer 7: Outreach Preparation (Omnichannel Pack)
        outreach_pack = OutreachPreparer.prepare_outreach(
            company_name=company_name,
            website_url=website_url,
            contact_name=normalized.get("primary_contact_name"),
            prompt_pack=prompt_pack,
            proposal=proposal,
            top_offers=offers,
        )

        # 7. Layer 8 & 9: Dispatch to Lead Manager (:8082) & Voice Agent (:8084)
        created_lead_id = None
        lead_record = None

        if auto_dispatch_to_lead_manager:
            lead_payload = {
                "company_name": company_name,
                "campaign_id": normalized.get("campaign_id"),
                "industry": industry,
                "location": location,
                "website_url": website_url,
                "primary_contact_name": normalized.get("primary_contact_name"),
                "primary_contact_email": normalized.get("primary_contact_email"),
                "primary_contact_phone": normalized.get("primary_contact_phone"),
                "source": normalized.get("source", "leadfinder+sdr"),
                "fit_score": business_data.get("business_score", 70.0),
                "opportunity_score": top_opportunity_score,
                "recommended_services": recommended_services,
                "metadata": {
                    **normalized.get("metadata", {}),
                    "dedupe_key": normalized.get("dedupe_key"),
                    "has_website": has_website,
                    "seo_summary": {
                        "score": seo_data.get("overall_seo_score", 0),
                        "issues_count": len(seo_data.get("issues", [])),
                    },
                    "business_summary": {
                        "score": business_data.get("business_score", 0),
                        "strengths": business_data.get("strengths", []),
                        "weaknesses": business_data.get("weaknesses", []),
                    },
                    "prompt_pack": prompt_pack.model_dump(),
                    "proposal_summary": {
                        "proposal_id": proposal.proposal_id,
                        "investment": proposal.investment_matrix,
                    },
                    "outreach_summary": {
                        "email_touches": len(outreach_pack.email_sequence),
                        "has_call_script": True,
                    },
                },
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    # Create Lead
                    lead_res = await client.post(
                        f"{self.lead_manager_url}/api/v1/leads",
                        json=lead_payload,
                    )
                    if lead_res.status_code in (200, 201):
                        lead_record = lead_res.json()
                        created_lead_id = lead_record["id"]

                        # Ingest Opportunities
                        opp_payload = [
                            {
                                "type": o.service_code,
                                "score": o.priority_score,
                                "problem_summary": o.problem_addressed,
                                "evidence": [{"deliverables": o.deliverables, "solution": o.solution_package}],
                                "recommended": o.recommended,
                            }
                            for o in offers
                        ]
                        await client.post(
                            f"{self.lead_manager_url}/api/v1/events",
                            json={
                                "type": "opportunity.created",
                                "lead_id": created_lead_id,
                                "actor": "SDR",
                                "payload": {"opportunities": opp_payload},
                            },
                        )

                        # Ingest Proposal Created -> Advances stage to PROPOSAL_READY
                        await client.post(
                            f"{self.lead_manager_url}/api/v1/events",
                            json={
                                "type": "proposal.created",
                                "lead_id": created_lead_id,
                                "actor": "SDR",
                                "payload": {
                                    "summary": f"Comprehensive proposal generated for {company_name}.",
                                    "recommended_services": recommended_services,
                                    "proposal_id": proposal.proposal_id,
                                },
                            },
                        )

                        # If lead has NO website, route to Voice Agent for website creation pitch
                        if not has_website:
                            await client.post(
                                f"{self.lead_manager_url}/api/v1/events",
                                json={
                                    "type": "lead.qualified",
                                    "lead_id": created_lead_id,
                                    "actor": "VoiceAgent",
                                    "payload": {
                                        "summary": f"Target has no website. Queued for Voice Agent website creation call.",
                                        "route": "VOICE_AGENT_PITCH",
                                    },
                                },
                            )
                except Exception:
                    pass

        return {
            "success": True,
            "lead_id": created_lead_id,
            "company_name": company_name,
            "has_website": has_website,
            "normalized_lead": normalized,
            "seo_analysis": seo_data,
            "business_analysis": business_data,
            "prompt_pack": prompt_pack.model_dump(),
            "selected_offers": OpportunityEngine.to_dict_list(offers),
            "proposal": proposal.model_dump(),
            "outreach_pack": outreach_pack.model_dump(),
            "lead_record": lead_record,
        }
