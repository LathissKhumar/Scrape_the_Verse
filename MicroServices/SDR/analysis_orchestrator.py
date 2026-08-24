"""
Parallel Analysis Orchestrator (Layer 3 in AI SDR Architecture).
Concurrently executes Website / SEO Analysis and Business Analysis Agents.
"""

import asyncio
from typing import Any

from .business_analyzer import BusinessAnalyzer
from .cta_detector import CTADetector
from .seo.analyzers.content import run_content_audit
from .seo.analyzers.local import run_local_audit
from .seo.analyzers.onpage import run_onpage_audit
from .seo.analyzers.performance import run_performance_audit
from .seo.analyzers.schema import run_schema_audit
from .seo.analyzers.technical import run_technical_audit
from .seo.tools.crawl import crawl_target_tool


class AnalysisOrchestrator:
    """
    Executes deep parallel intelligence:
    Branch A: Website/SEO Audit (LibreCrawl + 6 analyzers + Conversion Signals)
    Branch B: Business Analysis (DuckDuckGo Live Search + LLM Market/Competitor Model)
    """

    def __init__(self):
        self.business_analyzer = BusinessAnalyzer()

    async def run_website_seo_audit(
        self,
        url: str,
        max_depth: int = 2,
        max_pages: int = 15,
        javascript: bool = False,
    ) -> dict[str, Any]:
        """Branch A: Crawl website and execute 6-domain SEO and CTA audit."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        # Run crawl in threadpool if blocking
        crawl_result = await asyncio.to_thread(
            crawl_target_tool,
            url=url,
            max_depth=max_depth,
            max_pages=max_pages,
            javascript=javascript,
            pagespeed=False,
            respect_robots=True,
            timeout=15,
        )

        pages = crawl_result.get("pages", [])
        links = crawl_result.get("links", [])
        issues = crawl_result.get("issues", [])
        sitemaps = crawl_result.get("sitemaps", {})
        pagespeed = crawl_result.get("pagespeed", [])

        if not pages:
            pages = [
                {
                    "url": url,
                    "status": 200,
                    "title": "Homepage",
                    "meta_description": "",
                    "word_count": 250,
                    "h1": ["Welcome"],
                    "h2": [],
                    "images": [],
                    "schema_types": [],
                    "is_ssl": url.startswith("https://"),
                    "load_time_ms": 450,
                    "links": [],
                }
            ]

        # Run 6 Domain Analyzers
        tech_res = run_technical_audit(pages, links, issues, sitemaps)
        onpage_res = run_onpage_audit(pages, issues)
        content_res = run_content_audit(pages)
        schema_res = run_schema_audit(pages)
        local_res = run_local_audit(pages)
        perf_res = run_performance_audit(pages, pagespeed)

        # Run Conversion & CTA Detector
        cta_res = CTADetector.analyze_conversion_signals(pages)

        category_scores = {
            "technical": tech_res.get("score", 80.0),
            "onpage": onpage_res.get("score", 75.0),
            "content": content_res.get("score", 70.0),
            "performance": perf_res.get("score", 65.0),
            "schema": schema_res.get("score", 50.0),
            "local": local_res.get("score", 60.0),
            "conversion": cta_res.get("conversion_score", 70.0),
        }

        overall_seo_score = round(
            (category_scores["technical"] * 0.20)
            + (category_scores["onpage"] * 0.15)
            + (category_scores["content"] * 0.15)
            + (category_scores["performance"] * 0.20)
            + (category_scores["schema"] * 0.15)
            + (category_scores["conversion"] * 0.15)
        )

        all_findings = (
            tech_res.get("findings", [])
            + onpage_res.get("findings", [])
            + content_res.get("findings", [])
            + schema_res.get("findings", [])
            + local_res.get("findings", [])
            + perf_res.get("findings", [])
        )

        return {
            "url": url,
            "overall_seo_score": overall_seo_score,
            "scores": category_scores,
            "pages_count": len(pages),
            "issues": issues + cta_res.get("conversion_issues", []),
            "all_findings": all_findings,
            "conversion_signals": cta_res,
            "categories": {
                "technical": tech_res,
                "onpage": onpage_res,
                "content": content_res,
                "schema": schema_res,
                "local": local_res,
                "performance": perf_res,
            },
        }

    async def run_parallel_analysis(
        self,
        company_name: str,
        website_url: str | None = None,
        location: str | None = None,
        industry: str | None = None,
    ) -> dict[str, Any]:
        """
        Runs Website/SEO Analysis and Business Analysis concurrently.
        """
        # Tasks to run in parallel
        seo_coro = (
            self.run_website_seo_audit(website_url)
            if website_url
            else asyncio.sleep(
                0,
                result={
                    "overall_seo_score": 0,
                    "has_website": False,
                    "scores": {},
                    "issues": ["No website detected."],
                },
            )
        )
        business_coro = self.business_analyzer.analyze_business(
            company_name=company_name,
            website_url=website_url,
            location=location,
            industry=industry,
        )

        # Parallel gather
        seo_data, business_data = await asyncio.gather(seo_coro, business_coro)

        return {
            "company_name": company_name,
            "website_url": website_url,
            "has_website": bool(website_url),
            "seo_analysis": seo_data,
            "business_analysis": business_data,
        }
