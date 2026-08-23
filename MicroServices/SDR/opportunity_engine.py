"""
Opportunity Engine (Layer 5 in AI SDR Architecture).
Matches prospect weaknesses and SEO/Business findings to structured Agency Service offerings
with impact scoring (1-100), urgency scoring (1-100), and expected business outcomes.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class SelectedOffer(BaseModel):
    id: str = Field(default_factory=lambda: f"opp_{uuid4().hex[:12]}")
    service_code: str
    service_title: str
    impact_score: float
    urgency_score: float
    priority_score: float
    problem_addressed: str
    solution_package: str
    deliverables: List[str] = Field(default_factory=list)
    estimated_price_usd: int
    expected_outcomes: List[str] = Field(default_factory=list)
    recommended: bool = True


class OpportunityEngine:
    """
    Evaluates parallel intelligence against the Agency Service Catalog.
    """

    SERVICE_CATALOG = {
        "WEBSITE_REDESIGN": {
            "title": "Website Redesign & Conversion Architecture",
            "base_price": 1999,
            "deliverables": [
                "Modern, responsive mobile UX overhaul",
                "High-conversion booking and contact architecture",
                "Speed-optimized clean code framework",
                "Brand identity and trust badges integration",
            ],
            "outcomes": [
                "Eliminate mobile bounce rate",
                "Double visitor-to-lead conversion rate",
            ],
        },
        "LOCAL_SEO": {
            "title": "Local 3-Pack Google Maps & Schema Sprint",
            "base_price": 750,
            "deliverables": [
                "Complete Schema.org LocalBusiness JSON-LD injection",
                "Google Business Profile optimization and citation cleanup",
                "Local keyword targeting and NAP consistency audit",
            ],
            "outcomes": [
                "Top 3 Google Maps local ranking placement",
                "+35% increase in inbound local phone inquiries",
            ],
        },
        "SPEED_PERFORMANCE": {
            "title": "Core Web Vitals & Speed Boost",
            "base_price": 500,
            "deliverables": [
                "Image compression and WebP next-gen format conversion",
                "Critical CSS inlining and script deferral",
                "Server TTFB and caching optimization (<1.8s target)",
            ],
            "outcomes": [
                "Pass Google Core Web Vitals assessment",
                "Higher mobile search ranking factor",
            ],
        },
        "CONTENT_STRATEGY": {
            "title": "High-Intent Search Content Strategy",
            "base_price": 900,
            "deliverables": [
                "High-value service landing pages creation",
                "On-page metadata, H1/H2 hierarchy, and semantic enrichment",
                "Competitor keyword gap targeting",
            ],
            "outcomes": [
                "Rank for high-intent customer purchase searches",
                "Build domain authority and topical trust",
            ],
        },
        "AI_BOOKING_FUNNEL": {
            "title": "24/7 Automated Booking & Lead Capture Funnel",
            "base_price": 1200,
            "deliverables": [
                "Instant appointment booking widget integration",
                "Click-to-call and WhatsApp fast-response widget",
                "Automated lead notification & CRM dispatch pipeline",
            ],
            "outcomes": [
                "Capture 100% of after-hours web inquiries",
                "Instant lead confirmation within 60 seconds",
            ],
        },
    }

    @classmethod
    def evaluate_opportunities(
        cls,
        seo_data: Dict[str, Any],
        business_data: Dict[str, Any],
        has_website: bool = True,
    ) -> List[SelectedOffer]:
        offers: List[SelectedOffer] = []
        scores = seo_data.get("scores", {})
        issues = seo_data.get("issues", [])
        weaknesses = business_data.get("weaknesses", [])
        cta_signals = seo_data.get("conversion_signals", {})

        # If lead has NO website, primary offer is Full Website & Local Launch
        if not has_website:
            spec = cls.SERVICE_CATALOG["WEBSITE_REDESIGN"]
            offers.append(
                SelectedOffer(
                    service_code="WEBSITE_REDESIGN",
                    service_title="Complete Digital Presence & Custom Website Build",
                    impact_score=95.0,
                    urgency_score=90.0,
                    priority_score=92.5,
                    problem_addressed="Business currently has no dedicated website or online conversion funnel.",
                    solution_package="Custom high-performance website build with integrated local Google Maps setup.",
                    deliverables=spec["deliverables"],
                    estimated_price_usd=spec["base_price"],
                    expected_outcomes=spec["outcomes"],
                    recommended=True,
                )
            )
            return offers

        # 1. Evaluate Website Redesign / UX
        perf_s = scores.get("performance", 75.0)
        tech_s = scores.get("technical", 80.0)
        conv_s = scores.get("conversion", 70.0)
        if (perf_s + tech_s + conv_s) / 3.0 < 80.0:
            impact = min(98.0, 100.0 - ((perf_s + tech_s) / 2.0) + 15.0)
            urgency = 85.0 if conv_s < 60.0 else 75.0
            spec = cls.SERVICE_CATALOG["WEBSITE_REDESIGN"]
            offers.append(
                SelectedOffer(
                    service_code="WEBSITE_REDESIGN",
                    service_title=spec["title"],
                    impact_score=round(impact, 1),
                    urgency_score=round(urgency, 1),
                    priority_score=round((impact * 0.6) + (urgency * 0.4), 1),
                    problem_addressed=f"Suboptimal UX, low conversion signals ({conv_s}/100), and mobile layout barriers.",
                    solution_package="Complete redesign sprint focused on user experience and lead capture.",
                    deliverables=spec["deliverables"],
                    estimated_price_usd=spec["base_price"],
                    expected_outcomes=spec["outcomes"],
                    recommended=True,
                )
            )

        # 2. Evaluate Local SEO & Google Maps
        schema_s = scores.get("schema", 50.0)
        local_s = scores.get("local", 60.0)
        if schema_s < 75.0 or local_s < 75.0:
            impact = round(max(60.0, 100.0 - ((schema_s + local_s) / 2.0) + 10.0), 1)
            urgency = 80.0
            spec = cls.SERVICE_CATALOG["LOCAL_SEO"]
            offers.append(
                SelectedOffer(
                    service_code="LOCAL_SEO",
                    service_title=spec["title"],
                    impact_score=min(95.0, impact),
                    urgency_score=urgency,
                    priority_score=round((impact * 0.5) + (urgency * 0.5), 1),
                    problem_addressed=f"Missing structured LocalBusiness schema ({schema_s}/100) limiting Google 3-Pack visibility.",
                    solution_package="Turnkey Local SEO sprint to dominate local Google search listings.",
                    deliverables=spec["deliverables"],
                    estimated_price_usd=spec["base_price"],
                    expected_outcomes=spec["outcomes"],
                    recommended=True,
                )
            )

        # 3. Evaluate Speed & Performance
        if perf_s < 75.0:
            impact = round(max(60.0, 100.0 - perf_s + 10.0), 1)
            urgency = 85.0
            spec = cls.SERVICE_CATALOG["SPEED_PERFORMANCE"]
            offers.append(
                SelectedOffer(
                    service_code="SPEED_PERFORMANCE",
                    service_title=spec["title"],
                    impact_score=min(96.0, impact),
                    urgency_score=urgency,
                    priority_score=round((impact * 0.5) + (urgency * 0.5), 1),
                    problem_addressed=f"Slow load speeds ({perf_s}/100) causing customer drop-off before viewing services.",
                    solution_package="Core Web Vitals performance tuning to achieve sub-1.8 second loading.",
                    deliverables=spec["deliverables"],
                    estimated_price_usd=spec["base_price"],
                    expected_outcomes=spec["outcomes"],
                    recommended=True,
                )
            )

        # 4. Evaluate AI Booking Funnel
        if not cta_signals.get("has_booking_engine") or not cta_signals.get("has_live_chat"):
            spec = cls.SERVICE_CATALOG["AI_BOOKING_FUNNEL"]
            offers.append(
                SelectedOffer(
                    service_code="AI_BOOKING_FUNNEL",
                    service_title=spec["title"],
                    impact_score=88.0,
                    urgency_score=82.0,
                    priority_score=85.0,
                    problem_addressed="No automated instant booking mechanism to capture high-intent inquiries 24/7.",
                    solution_package="Deploy conversion-optimized online booking widget and instant lead capture pipeline.",
                    deliverables=spec["deliverables"],
                    estimated_price_usd=spec["base_price"],
                    expected_outcomes=spec["outcomes"],
                    recommended=True,
                )
            )

        # Sort offers by priority_score descending
        offers.sort(key=lambda o: o.priority_score, reverse=True)
        return offers

    @classmethod
    def to_dict_list(cls, offers: List[SelectedOffer]) -> List[Dict[str, Any]]:
        return [o.model_dump() for o in offers]
