"""
Proposal Generator (Layer 6 in AI SDR Architecture).
Generates structured Markdown / PDF proposal documents for internal lead maintenance,
CRM records, and client deliverables.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .opportunity_engine import SelectedOffer
from .prompt_generator import PersonalizedPromptPack


class ProposalDocument(BaseModel):
    proposal_id: str
    company_name: str
    website_url: Optional[str]
    generated_at: str
    executive_summary: str
    current_state_audit: Dict[str, Any] = Field(default_factory=dict)
    recommended_solutions: List[Dict[str, Any]] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    investment_matrix: Dict[str, Any] = Field(default_factory=dict)
    timeline_weeks: int = 4
    next_steps: List[str] = Field(default_factory=list)
    markdown_content: str


class ProposalGenerator:
    """
    Creates comprehensive client proposals matching identified opportunities and prompt context.
    """

    @classmethod
    def generate_proposal(
        cls,
        company_name: str,
        website_url: Optional[str],
        prompt_pack: PersonalizedPromptPack,
        offers: List[SelectedOffer],
        seo_data: Optional[Dict[str, Any]] = None,
        business_data: Optional[Dict[str, Any]] = None,
    ) -> ProposalDocument:
        proposal_id = f"prop_{company_name.lower().replace(' ', '_')[:12]}_{int(datetime.now(timezone.utc).timestamp())}"
        top_offers = offers[:3]
        total_setup = sum(o.estimated_price_usd for o in top_offers)

        # 1. Executive Summary
        exec_summary = (
            f"Digital Growth Proposal for {company_name}.\n"
            f"Based on our technical crawl of {website_url or 'your commercial footprint'} and local market benchmarking, "
            f"we identified {len(top_offers)} high-impact opportunities to eliminate customer drop-off and capture market share."
        )

        # 2. Audit Breakdown
        current_state = {
            "seo_health_score": seo_data.get("overall_seo_score", 70) if seo_data else 70,
            "key_problems": prompt_pack.key_problems,
            "competitor_pressures": business_data.get("competitor_insights", "") if business_data else "",
        }

        # 3. Deliverables Checklist
        all_deliverables = []
        for o in top_offers:
            all_deliverables.extend(o.deliverables)
        all_deliverables.append("Dedicated Analytics Dashboard & Monthly Performance Review")

        # 4. Investment Matrix
        investment_matrix = {
            "primary_package": top_offers[0].service_title if top_offers else "Custom Growth Sprint",
            "one_time_investment_usd": total_setup,
            "monthly_retainer_usd": 499,
            "roi_guarantee": "30-Day Measurable Search & Speed Improvement",
            "line_items": [
                {"service": o.service_title, "amount_usd": o.estimated_price_usd}
                for o in top_offers
            ],
        }

        # 5. Next Steps
        next_steps = [
            "1. Confirm strategy on a brief 15-minute alignment call.",
            "2. Access verification & technical deployment sprint (Weeks 1-2).",
            "3. Live testing, Google Search Console indexing, and performance reporting (Weeks 3-4).",
        ]

        # 6. Generate Markdown Document
        md_lines = [
            f"# Digital Growth & Optimization Proposal",
            f"**Prepared for:** {company_name}",
            f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            f"**Proposal ID:** `{proposal_id}`",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            exec_summary,
            "",
            "## 2. Identified Technical & Market Pain Points",
        ]
        for p in prompt_pack.key_problems:
            md_lines.append(f"- **Issue:** {p}")

        md_lines.extend([
            "",
            "## 3. Recommended Solution Package",
        ])
        for o in top_offers:
            md_lines.append(f"### {o.service_title} (Priority Score: {o.priority_score}/100)")
            md_lines.append(f"*{o.solution_package}*")
            md_lines.append("**Deliverables:**")
            for d in o.deliverables:
                md_lines.append(f"- {d}")
            md_lines.append("")

        md_lines.extend([
            "## 4. Investment & Deliverables Summary",
            f"- **Total Setup Sprint Investment:** ${total_setup:,} USD",
            "- **Optional Monthly Growth & Maintenance Retainer:** $499/month",
            "- **Estimated Sprint Timeline:** 4 Weeks",
            "",
            "## 5. Next Steps",
        ])
        for s in next_steps:
            md_lines.append(s)

        markdown_content = "\n".join(md_lines)

        return ProposalDocument(
            proposal_id=proposal_id,
            company_name=company_name,
            website_url=website_url,
            generated_at=datetime.now(timezone.utc).isoformat(),
            executive_summary=exec_summary,
            current_state_audit=current_state,
            recommended_solutions=[o.model_dump() for o in top_offers],
            deliverables=all_deliverables,
            investment_matrix=investment_matrix,
            timeline_weeks=4,
            next_steps=next_steps,
            markdown_content=markdown_content,
        )
