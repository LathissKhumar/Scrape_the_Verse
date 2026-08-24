"""
SDR Opportunity Builder (Layer 5 in AI SDR Architecture).
Synthesizes website audit findings, technical metrics, and UX issues into scored Opportunity objects.
"""

from typing import Any
from uuid import uuid4


class OpportunityBuilder:
    """
    Analyzes audit findings across 6 categories (Technical, On-Page, Content, Schema, Local, Performance)
    and creates actionable business opportunities.
    """

    @staticmethod
    def build_opportunities_from_audit(
        audit_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        opportunities: list[dict[str, Any]] = []
        scores = audit_state.get("scores", {})
        categories = audit_state.get("categories", {})
        issues = audit_state.get("issues", [])

        # 1. WEBSITE REDESIGN / UX OPPORTUNITY
        perf_score = scores.get("performance", 75.0)
        tech_score = scores.get("technical", 80.0)
        combined_design_score = (perf_score + tech_score) / 2.0

        design_evidence = []
        for issue in issues[:10]:
            if any(
                k in str(issue).lower()
                for k in ["viewport", "responsive", "mobile", "css", "layout", "slow"]
            ):
                design_evidence.append({"finding": issue, "type": "UX/Design"})

        if combined_design_score < 85.0 or design_evidence:
            opp_score = round(max(50.0, 100.0 - combined_design_score + 10.0), 1)
            opportunities.append(
                {
                    "id": f"opp_{uuid4().hex[:12]}",
                    "type": "WEBSITE_REDESIGN",
                    "score": min(98.0, opp_score),
                    "problem_summary": f"Suboptimal mobile performance and technical UX score ({combined_design_score:.1f}/100).",
                    "evidence": design_evidence[:5],
                    "recommended": opp_score >= 50.0,
                    "status": "IDENTIFIED",
                }
            )

        # 2. LOCAL SEO OPPORTUNITY
        local_score = scores.get("local", 60.0)
        schema_score = scores.get("schema", 50.0)
        local_evidence = []
        for issue in issues:
            if any(
                k in str(issue).lower()
                for k in ["local", "schema", "nap", "address", "map", "json-ld"]
            ):
                local_evidence.append({"finding": issue, "type": "Local SEO"})

        if local_score < 80.0 or schema_score < 70.0 or local_evidence:
            opp_score = round(
                max(55.0, 100.0 - ((local_score + schema_score) / 2.0)), 1
            )
            opportunities.append(
                {
                    "id": f"opp_{uuid4().hex[:12]}",
                    "type": "LOCAL_SEO",
                    "score": min(96.0, opp_score),
                    "problem_summary": f"Incomplete Schema markup ({schema_score:.1f}/100) and local business optimization gaps.",
                    "evidence": local_evidence[:5],
                    "recommended": opp_score >= 50.0,
                    "status": "IDENTIFIED",
                }
            )

        # 3. SPEED & CORE WEB VITALS OPTIMIZATION
        if perf_score < 80.0:
            opp_score = round(max(60.0, 100.0 - perf_score), 1)
            opportunities.append(
                {
                    "id": f"opp_{uuid4().hex[:12]}",
                    "type": "SPEED_PERFORMANCE",
                    "score": min(99.0, opp_score),
                    "problem_summary": f"Slow page response metrics and performance score ({perf_score:.1f}/100).",
                    "evidence": [{"metric": "Performance Score", "score": perf_score}],
                    "recommended": opp_score >= 50.0,
                    "status": "IDENTIFIED",
                }
            )

        # 4. CONTENT STRATEGY & ON-PAGE SEO
        content_score = scores.get("content", 70.0)
        onpage_score = scores.get("onpage", 75.0)
        if content_score < 80.0 or onpage_score < 80.0:
            opp_score = round(
                max(50.0, 100.0 - ((content_score + onpage_score) / 2.0)), 1
            )
            opportunities.append(
                {
                    "id": f"opp_{uuid4().hex[:12]}",
                    "type": "CONTENT_STRATEGY",
                    "score": min(94.0, opp_score),
                    "problem_summary": f"On-page metadata and content depth optimization opportunities ({onpage_score:.1f}/100).",
                    "evidence": [
                        {"content_score": content_score, "onpage_score": onpage_score}
                    ],
                    "recommended": opp_score >= 50.0,
                    "status": "IDENTIFIED",
                }
            )

        # Default fallback opportunity if none flagged
        if not opportunities:
            opportunities.append(
                {
                    "id": f"opp_{uuid4().hex[:12]}",
                    "type": "CONVERSION_OPTIMIZATION",
                    "score": 75.0,
                    "problem_summary": "Comprehensive conversion rate optimization and competitive SEO enhancement.",
                    "evidence": [
                        {
                            "audit_summary": "Overall baseline passed, advanced CRO recommended."
                        }
                    ],
                    "recommended": True,
                    "status": "IDENTIFIED",
                }
            )

        # Sort opportunities by score descending
        opportunities.sort(key=lambda x: x["score"], reverse=True)
        if opportunities and not any(o.get("recommended") for o in opportunities):
            opportunities[0]["recommended"] = True

        return opportunities
