"""
Prompt Generation Layer (Layer 4 in AI SDR Architecture).
Synthesizes parallel Website Analysis + Business Analysis findings into
a structured, narrative-rich PersonalizedPromptPack using LLM.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from MicroServices.Lead_Manager.agents.llm_factory import LLMClient


class PersonalizedPromptPack(BaseModel):
    company_context: str
    key_problems: List[str] = Field(default_factory=list)
    value_angles: List[str] = Field(default_factory=list)
    recommended_services: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(default_factory=list)
    objections_and_responses: List[Dict[str, str]] = Field(default_factory=list)


class PromptGenerator:
    """
    Synthesizes technical SEO & business intelligence into high-conversion sales narrative context.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def generate_sales_context(
        self,
        company_name: str,
        website_url: Optional[str],
        industry: Optional[str] = None,
        location: Optional[str] = None,
        seo_data: Optional[Dict[str, Any]] = None,
        business_data: Optional[Dict[str, Any]] = None,
    ) -> PersonalizedPromptPack:
        seo_data = seo_data or {}
        business_data = business_data or {}

        seo_score = seo_data.get("overall_seo_score", 70)
        seo_issues = seo_data.get("issues", [])
        business_weaknesses = business_data.get("weaknesses", [])
        competitor_insights = business_data.get("competitor_insights", "")

        system_prompt = (
            "You are a World-Class SDR Sales Strategist and Copywriter. "
            "Synthesize the provided website audit and business intelligence into an authentic, "
            "compelling sales context pack for outreach. "
            "Return a valid JSON object with the following exact keys:\n"
            "{\n"
            '  "company_context": "2-sentence executive summary of who they are and their digital opportunity",\n'
            '  "key_problems": ["list of 3 specific technical & business pain points discovered"],\n'
            '  "value_angles": ["list of 3 sharp, compelling ROI value angles to pitch"],\n'
            '  "recommended_services": ["list of 2-3 agency offerings that solve these exact problems"],\n'
            '  "proof_points": ["list of 2-3 credible data proof points or metrics"],\n'
            '  "objections_and_responses": [\n'
            '    {"objection": "Already have an agency/web designer", "response": "tactical response"},\n'
            '    {"objection": "Get all business via word of mouth", "response": "tactical response"},\n'
            '    {"objection": "No budget right now", "response": "tactical response"}\n'
            '  ]\n'
            "}"
        )

        user_prompt = (
            f"Target Company: {company_name}\n"
            f"Website: {website_url or 'No Website (Needs custom web foundation)'}\n"
            f"Industry: {industry or 'Local Business'}\n"
            f"Location: {location or 'Local Market'}\n\n"
            f"SEO Health Score: {seo_score}/100\n"
            f"SEO & UX Issues: {', '.join(str(i) for i in seo_issues[:5])}\n"
            f"Business Weaknesses: {', '.join(str(w) for w in business_weaknesses[:4])}\n"
            f"Competitor Landscape: {competitor_insights}\n\n"
            f"Generate the comprehensive sales context pack."
        )

        llm_result = await self.llm.generate_json(prompt=user_prompt, system_prompt=system_prompt)

        if llm_result and isinstance(llm_result, dict) and "company_context" in llm_result:
            try:
                return PersonalizedPromptPack(**llm_result)
            except Exception:
                pass

        # Fallback synthesis
        problems = []
        if seo_score < 80 and seo_issues:
            problems.append(f"Technical & speed issues: {seo_issues[0]}")
        problems.extend(business_weaknesses[:2])
        if not problems:
            problems = ["Suboptimal mobile conversion rate and under-leveraged local Google 3-Pack rankings."]

        return PersonalizedPromptPack(
            company_context=(
                f"{company_name} is an active business operating in {location or 'their market'} "
                f"({website_url or 'currently without dedicated web presence'}). "
                f"Significant headroom exists to capture local market share with modern digital infrastructure."
            ),
            key_problems=problems[:3],
            value_angles=[
                f"Directly capture ready-to-buy customers searching for {industry or 'services'} locally.",
                "Convert 2x more website visitors into booked phone consultations.",
                "Dominate local Google Maps 3-pack search results over top competitors.",
            ],
            recommended_services=[
                "Website Redesign & Conversion Architecture",
                "Local SEO & Google Maps 3-Pack Sprint",
                "Speed & Core Web Vitals Optimization",
            ],
            proof_points=[
                "Local Schema and Google Maps optimization typically generates a 38% uplift in inbound phone calls.",
                "Sub-2 second mobile page loads reduce bounce rates by up to 40%.",
                "Implementing instant online booking captures high-intent after-hours inquiries.",
            ],
            objections_and_responses=[
                {
                    "objection": "We already have an agency / web designer.",
                    "response": "Understood! Our technical audit revealed 3 specific crawl gaps that traditional web designers often overlook. We can send you the report so your team can patch them directly.",
                },
                {
                    "objection": "We get most clients by word of mouth.",
                    "response": "Word of mouth is fantastic. When referrals Google your name to verify, ensuring a flawless mobile site turns those referrals into immediate booked appointments.",
                },
                {
                    "objection": "We don't have budget for a full overhaul.",
                    "response": "You don't need a complete rebuild. Our findings pinpoint targeted, high-impact fixes (like Local Schema & speed) that take days to deploy with immediate ROI.",
                },
            ],
        )
