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


async def execute_query(query: str, target_urls: Optional[list[str]] = None):
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

    urls = target_urls or []

    print("\n" + "=" * 60)
    print("  SCRAPE THE VERSE - CLI QUERY EXECUTOR")
    print("=" * 60)
    print(f"Query:        {query}")
    if urls:
        print(f"Target URLs ({len(urls)}):")
        for u in urls:
            print(f"  - {u}")
    print(f"Engine Mode:  {'Bright Data' if settings.BRIGHTDATA else 'Native Playwright Engine (Parallel)'}")
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
        help="Plain language query (e.g. 'Compare prices of iPhone 15')",
    )
    parser.add_argument(
        "-u", "--urls",
        nargs="+",
        default=None,
        help="One or more target URLs (separated by spaces or commas)",
    )

    args = parser.parse_args()

    # Normalize URLs from args
    target_urls: list[str] = []
    if args.urls:
        for u in args.urls:
            for piece in u.split(","):
                clean = piece.strip()
                if clean:
                    target_urls.append(clean)

    if args.query:
        asyncio.run(execute_query(query=args.query, target_urls=target_urls))
    else:
        # Interactive mode
        print("\n" + "=" * 60)
        print("  SCRAPE THE VERSE - INTERACTIVE PROMPT")
        print("=" * 60)
        user_query = input("\nEnter your scraping query: ").strip()
        if not user_query:
            print("No query provided. Exiting.")
            sys.exit(0)
        raw_urls = input("Enter target URLs (separated by commas, or press Enter to skip): ").strip()
        interactive_urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
        asyncio.run(execute_query(query=user_query, target_urls=interactive_urls))


if __name__ == "__main__":
    main()
