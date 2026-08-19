"""Interactive and argument-based CLI for Scrape_the_Verse."""

import argparse
import asyncio
import json
import sys
import warnings
from typing import Optional

warnings.filterwarnings("ignore")


# Silence known Windows Proactor pipe destruction artifact on process exit
def _silence_unraisablehook(unraisable):
    if unraisable.exc_type in (ValueError, ResourceWarning) and "closed pipe" in str(unraisable.exc_value or ""):
        return
    if unraisable.exc_type is RuntimeError and "Event loop is closed" in str(unraisable.exc_value or ""):
        return
    sys.__unraisablehook__(unraisable)


sys.unraisablehook = _silence_unraisablehook

from app.graph.state import ScrapingGraphState
from app.graph.workflow import create_scraping_workflow
from app.llm.ollama_client import OllamaClient
from app.agents.planner import ScrapingPlannerAgent
from app.agents.scraper import ScraperAgent
from app.agents.extraction import ExtractionAgent
from app.agents.validation import ValidationAgent
from app.agents.diagnosis import DiagnosisAgent
from app.agents.healing import HealingAgent
from app.config.settings import get_settings


async def execute_query(query: str, target_url: Optional[str] = None):
    """Execute scraping workflow directly from CLI."""
    settings = get_settings()
    llm = OllamaClient(settings=settings)
    scraper = ScraperAgent()
    planner = ScrapingPlannerAgent(llm_client=llm)
    extractor = ExtractionAgent(llm_client=llm)
    validator = ValidationAgent()
    diagnosis = DiagnosisAgent(llm_client=llm)
    healing = HealingAgent(llm_client=llm, scraper_agent=scraper)

    workflow = create_scraping_workflow(
        planner_agent=planner,
        scraper_agent=scraper,
        extraction_agent=extractor,
        validation_agent=validator,
        diagnosis_agent=diagnosis,
        healing_agent=healing,
    )

    urls = [target_url] if target_url else []

    print("\n" + "=" * 60)
    print("  SCRAPE THE VERSE - CLI QUERY EXECUTOR")
    print("=" * 60)
    print(f"Query:        {query}")
    if target_url:
        print(f"Target URL:   {target_url}")
    print(f"Engine Mode:  {'Bright Data' if settings.BRIGHTDATA else 'Native Playwright Engine'}")
    print("-" * 60)
    print("Executing pipeline (Planner -> Scraper -> Extractor -> Validator)...")

    initial_state: ScrapingGraphState = {
        "task_id": "cli_query",
        "original_user_query": query,
        "target_urls": urls,
        "repair_attempt": 0,
    }

    try:
        result = await workflow.ainvoke(initial_state)
        output = result.get("final_output")

        print("\n" + "=" * 60)
        print("  SCRAPING RESULTS")
        print("=" * 60)
        if output:
            print(f"Status:        {output.status.upper()}")
            print(f"Health Score:  {output.metadata.get('health_score', 0.0):.2f}")
            print(f"Record Count:  {len(output.records)}")
            print("-" * 60)

            for i, r in enumerate(output.records, 1):
                print(f"\n[Record {i}]")
                for k, v in r.items():
                    print(f"  {k}: {v}")

            print("\n" + "-" * 60)
            print("Metadata Summary:")
            meta = {
                "validation_status": output.metadata.get("validation_status"),
                "quality_score": output.metadata.get("quality_score"),
                "self_healed": output.metadata.get("self_healed"),
                "anomalies": output.metadata.get("anomalies", []),
            }
            print(json.dumps(meta, indent=2))
        else:
            print("No output produced.")

    except Exception as e:
        print(f"\n[ERROR] Scraping execution failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape_the_Verse CLI: Natural Language Web Scraper"
    )
    parser.add_argument(
        "query",
        nargs="?",
        type=str,
        help="Plain language query (e.g. 'Extract title and price from https://example.com')",
    )
    parser.add_argument(
        "-u", "--url",
        type=str,
        default=None,
        help="Optional explicit target URL",
    )

    args = parser.parse_args()

    if args.query:
        asyncio.run(execute_query(query=args.query, target_url=args.url))
    else:
        # Interactive mode
        print("\n" + "=" * 60)
        print("  SCRAPE THE VERSE - INTERACTIVE PROMPT")
        print("=" * 60)
        user_query = input("\nEnter your scraping query: ").strip()
        if not user_query:
            print("No query provided. Exiting.")
            sys.exit(0)
        user_url = input("Enter target URL (optional, press Enter to skip): ").strip() or None
        asyncio.run(execute_query(query=user_query, target_url=user_url))


if __name__ == "__main__":
    main()
