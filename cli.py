"""Interactive and argument-based CLI for Scrape_the_Verse."""

import argparse
import asyncio
import json
import sys
import warnings
from typing import Optional
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
warnings.filterwarnings("ignore")


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.export.exporter import DataExporter


async def execute_query(
    query: str,
    target_urls: Optional[list[str]] = None,
    output_path: Optional[str] = None,
    output_format: Optional[str] = None,
    verbose: bool = False,
):
    """Execute scraping workflow directly from CLI."""
    setup_logging(verbose=verbose, is_cli=True)

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
    engine_name = "Bright Data" if settings.BRIGHTDATA else "Native Playwright Engine (Parallel)"

    print("\n" + "=" * 65)
    print(f"  {Style.BRIGHT}SCRAPE THE VERSE - CLI QUERY EXECUTOR{Style.RESET_ALL}")
    print("=" * 65)
    print(f"{Style.BRIGHT}Query:{Style.RESET_ALL}        {query}")
    if urls:
        print(f"{Style.BRIGHT}Target URLs ({len(urls)}):{Style.RESET_ALL}")
        for u in urls:
            print(f"  - {u}")
    print(f"{Style.BRIGHT}Engine Mode:{Style.RESET_ALL}  {engine_name}")
    print("-" * 65)
    print(f"{Fore.LIGHTCYAN_EX}[PIPELINE]   {Style.RESET_ALL}Starting (Planner -> Scraper -> Extractor -> Validator)...")

    initial_state: ScrapingGraphState = {
        "task_id": "cli_query",
        "original_user_query": query,
        "target_urls": urls,
        "repair_attempt": 0,
    }

    try:
        result = await workflow.ainvoke(initial_state)
        output = result.get("final_output")

        print("\n" + "=" * 65)
        print(f"  {Style.BRIGHT}SCRAPING RESULTS{Style.RESET_ALL}")
        print("=" * 65)
        if output:
            status_color = Fore.GREEN if output.status == "success" else (Fore.YELLOW if output.status == "partial" else Fore.RED)
            health_val = output.metadata.get("health_score", 0.0)
            quality_val = output.metadata.get("quality_score", 0.0)
            val_status = output.metadata.get("validation_status", "unknown")

            print(f"{Style.BRIGHT}Status:{Style.RESET_ALL}        {status_color}{output.status.upper()}{Style.RESET_ALL}")
            print(f"{Style.BRIGHT}Health Score:{Style.RESET_ALL}  {health_val:.2f} / 1.00 ({val_status.capitalize()})")
            print(f"{Style.BRIGHT}Quality Score:{Style.RESET_ALL} {quality_val:.2f} / 1.00")
            print(f"{Style.BRIGHT}Record Count:{Style.RESET_ALL}  {len(output.records)}")
            print("-" * 65)

            if output.records:
                for i, r in enumerate(output.records, 1):
                    print(f"\n{Fore.CYAN}[Record {i}]{Style.RESET_ALL}")
                    for k, v in r.items():
                        print(f"  {Style.BRIGHT}{k}:{Style.RESET_ALL} {v}")
            else:
                print(f"\n{Fore.YELLOW}No structured records extracted.{Style.RESET_ALL}")

            print("\n" + "-" * 65)
            print(f"{Style.BRIGHT}Metadata Summary:{Style.RESET_ALL}")
            print(f"  Validation Status: {val_status}")
            print(f"  Quality Score:     {quality_val:.2f}")
            print(f"  Self-Healed:       {output.metadata.get('self_healed')}")

            anomalies = output.metadata.get("anomalies", [])
            if anomalies:
                print(f"  Anomalies Detected ({len(anomalies)}):")
                for a in anomalies:
                    print(f"    - {a}")
            else:
                print("  Anomalies:         None")

            if output_path and output.records:
                fmt = (output_format or "json").lower()
                if fmt == "csv" or output_path.endswith(".csv"):
                    content = DataExporter.to_csv(output.records)
                elif fmt == "ndjson" or output_path.endswith(".ndjson"):
                    content = DataExporter.to_ndjson(output.records)
                else:
                    content = DataExporter.to_json(output.records)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"\n{Fore.GREEN}[EXPORT] Saved {len(output.records)} records to {output_path} ({fmt.upper()}){Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}No output produced.{Style.RESET_ALL}")

    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Scraping execution failed: {e}{Style.RESET_ALL}")


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
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path to save results (e.g. results.csv or results.json)",
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="json",
        choices=["json", "csv", "ndjson"],
        help="Export format (default: json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logs",
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
        asyncio.run(
            execute_query(
                query=args.query,
                target_urls=target_urls,
                output_path=args.output,
                output_format=args.format,
                verbose=args.verbose,
            )
        )
    else:
        # Interactive mode
        setup_logging(verbose=args.verbose, is_cli=True)
        print("\n" + "=" * 65)
        print(f"  {Style.BRIGHT}SCRAPE THE VERSE - INTERACTIVE PROMPT{Style.RESET_ALL}")
        print("=" * 65)
        user_query = input("\nEnter your scraping query: ").strip()
        if not user_query:
            print("No query provided. Exiting.")
            sys.exit(0)
        raw_urls = input("Enter target URLs (separated by commas, or press Enter to skip): ").strip()
        interactive_urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
        asyncio.run(
            execute_query(
                query=user_query,
                target_urls=interactive_urls,
                output_path=args.output,
                output_format=args.format,
                verbose=args.verbose,
            )
        )


if __name__ == "__main__":
    main()

