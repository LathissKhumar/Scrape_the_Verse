"""Interactive and argument-based CLI for Scrape_the_Verse (Dual-Engine: Native & Bright Data)."""

import argparse
import asyncio
import sys
import warnings

from colorama import Fore, Style
from colorama import init as colorama_init

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
    if unraisable.exc_type in (ValueError, ResourceWarning) and "closed pipe" in str(
        unraisable.exc_value or ""
    ):
        return
    if unraisable.exc_type is RuntimeError and "Event loop is closed" in str(
        unraisable.exc_value or ""
    ):
        return
    sys.__unraisablehook__(unraisable)


sys.unraisablehook = _silence_unraisablehook

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent
_repo_root = _pkg_root.parent
for _path in (str(_pkg_root), str(_repo_root)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from leadfinder.agents.diagnosis import DiagnosisAgent
from leadfinder.agents.extraction import ExtractionAgent
from leadfinder.agents.gmaps import GoogleMapsAgent
from leadfinder.agents.healing import HealingAgent
from leadfinder.agents.planner import ScrapingPlannerAgent
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.agents.validation import ValidationAgent
from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.service import BrightDataService
from leadfinder.config.logging import setup_logging
from leadfinder.config.settings import get_settings
from leadfinder.export.exporter import DataExporter
from leadfinder.gmaps.service import GoogleMapsService
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.graph.workflow import create_scraping_workflow
from leadfinder.llm.ollama_client import OllamaClient
from leadfinder.models.schemas import ScrapingTask


async def check_brightdata_health(verbose: bool = False):
    """Inspect and test Bright Data collectors and API credentials."""
    setup_logging(verbose=verbose, is_cli=True)
    settings = get_settings()
    client = BrightDataClient(settings=settings)

    print("\n" + "=" * 65)
    print(
        f"  {Style.BRIGHT}BRIGHT DATA COLLECTOR & SYSTEM HEALTH CHECK{Style.RESET_ALL}"
    )
    print("=" * 65)
    print(
        f"  BRIGHTDATA Enabled:           {Fore.GREEN if settings.BRIGHTDATA else Fore.YELLOW}{settings.BRIGHTDATA}{Style.RESET_ALL}"
    )
    print(
        f"  API Key Configured:           {Fore.GREEN if bool(settings.BRIGHTDATA_API_KEY) else Fore.RED}{'Yes (***' + str(settings.BRIGHTDATA_API_KEY)[-4:] + ')' if settings.BRIGHTDATA_API_KEY else 'No'}{Style.RESET_ALL}"
    )
    print(
        f"  Discovery Collector ID:       {Fore.CYAN}{settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID or settings.BRIGHTDATA_COLLECTOR_ID or 'Not Set'}{Style.RESET_ALL}"
    )
    print(
        f"  Company Profile Collector ID: {Fore.CYAN}{settings.BRIGHTDATA_COMPANY_COLLECTOR_ID or 'Not Set'}{Style.RESET_ALL}"
    )
    print("-" * 65)

    if not client.is_configured:
        print(
            f"{Fore.RED}[STATUS] Bright Data is NOT fully configured.{Style.RESET_ALL}"
        )
        print("To enable, set BRIGHTDATA=True and provide BRIGHTDATA_API_KEY in .env")
        return

    print(
        f"{Fore.GREEN}[STATUS] Bright Data credentials configured successfully!{Style.RESET_ALL}"
    )
    print(
        f'You can run lead generation via: {Style.BRIGHT}python cli.py "solar panels" --leads{Style.RESET_ALL}'
    )
    print(
        f'Or run query fast-path via:      {Style.BRIGHT}python cli.py "solar panels" --engine brightdata{Style.RESET_ALL}'
    )
    print("=" * 65 + "\n")


async def execute_lead_gen(
    query: str,
    enrich: bool = True,
    output_path: str | None = None,
    output_format: str | None = None,
    verbose: bool = False,
):
    """Execute chained 2-Tier Lead Generation using Bright Data collectors."""
    setup_logging(verbose=verbose, is_cli=True)
    settings = get_settings()
    service = BrightDataService(settings=settings)

    print("\n" + "=" * 65)
    print(f"  {Style.BRIGHT}BRIGHT DATA B2B LEAD GENERATOR{Style.RESET_ALL}")
    print("=" * 65)
    print(f"{Style.BRIGHT}Query:{Style.RESET_ALL}              {query}")
    print(
        f"{Style.BRIGHT}Profile Enrichment:{Style.RESET_ALL} {'Enabled (Tier 2 PDP)' if enrich else 'Disabled (Tier 1 Only)'}"
    )
    print(
        f"{Style.BRIGHT}Discovery Collector:{Style.RESET_ALL}{service.pipeline.discovery_collector_id}"
    )
    print(
        f"{Style.BRIGHT}Company Collector:{Style.RESET_ALL}  {service.pipeline.company_collector_id}"
    )
    print("-" * 65)
    print(
        f"{Fore.LIGHTCYAN_EX}[PIPELINE]   {Style.RESET_ALL}Executing Chained Lead Extraction..."
    )

    try:
        leads = await service.generate_leads(query=query, enrich_profiles=enrich)

        print("\n" + "=" * 65)
        print(
            f"  {Style.BRIGHT}LEAD GENERATION RESULTS ({len(leads)} Leads){Style.RESET_ALL}"
        )
        print("=" * 65)

        if leads:
            for i, lead in enumerate(leads, 1):
                print(
                    f"\n{Fore.CYAN}[Lead #{i}] {Style.BRIGHT}{lead.get('company_name', 'Unknown Company')}{Style.RESET_ALL}"
                )
                if lead.get("product_title"):
                    print(
                        f"  {Style.BRIGHT}Product:{Style.RESET_ALL}       {lead.get('product_title')}"
                    )
                if lead.get("price"):
                    price_info = lead.get("price")
                    if isinstance(price_info, dict):
                        print(
                            f"  {Style.BRIGHT}Price:{Style.RESET_ALL}         {price_info.get('symbol', '₹')}{price_info.get('value', '')} {price_info.get('currency', '')}"
                        )
                    else:
                        print(
                            f"  {Style.BRIGHT}Price:{Style.RESET_ALL}         {price_info}"
                        )
                if lead.get("contact_person"):
                    print(
                        f"  {Style.BRIGHT}Contact Person:{Style.RESET_ALL}{Fore.GREEN} {lead.get('contact_person')}{Style.RESET_ALL}"
                    )
                if lead.get("gstin"):
                    print(
                        f"  {Style.BRIGHT}GSTIN:{Style.RESET_ALL}          {lead.get('gstin')}"
                    )
                if lead.get("established_year"):
                    print(
                        f"  {Style.BRIGHT}Established:{Style.RESET_ALL}    {lead.get('established_year')}"
                    )
                if lead.get("nature_of_business"):
                    print(
                        f"  {Style.BRIGHT}Business Type:{Style.RESET_ALL}  {lead.get('nature_of_business')}"
                    )
                if lead.get("city") or lead.get("state"):
                    print(
                        f"  {Style.BRIGHT}Location:{Style.RESET_ALL}       {lead.get('city', '')}, {lead.get('state', '')}"
                    )
                if lead.get("company_catalog_url"):
                    print(
                        f"  {Style.BRIGHT}Catalog URL:{Style.RESET_ALL}    {lead.get('company_catalog_url')}"
                    )

            if output_path:
                fmt = (output_format or "json").lower()
                if fmt == "csv" or output_path.endswith(".csv"):
                    content = DataExporter.to_csv(leads)
                elif fmt == "ndjson" or output_path.endswith(".ndjson"):
                    content = DataExporter.to_ndjson(leads)
                else:
                    content = DataExporter.to_json(leads)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(
                    f"\n{Fore.GREEN}[EXPORT] Saved {len(leads)} lead records to {output_path} ({fmt.upper()}){Style.RESET_ALL}"
                )
        else:
            print(
                f"\n{Fore.YELLOW}No leads discovered for query '{query}'.{Style.RESET_ALL}"
            )

    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Lead generation failed: {e}{Style.RESET_ALL}")


async def execute_gmaps_leads(
    query: str,
    location: str | None = None,
    output_path: str | None = None,
    output_format: str | None = None,
    verbose: bool = False,
):
    """Execute Google Maps local lead discovery."""
    setup_logging(verbose=verbose, is_cli=True)
    settings = get_settings()
    service = GoogleMapsService(settings=settings)
    agent = GoogleMapsAgent(service=service)

    cat, loc = agent.parse_query_and_location(query)
    eff_loc = location or loc

    print("\n" + "=" * 65)
    print(f"  {Style.BRIGHT}GOOGLE MAPS LOCAL LEAD DISCOVERY{Style.RESET_ALL}")
    print("=" * 65)
    print(f"{Style.BRIGHT}Category:{Style.RESET_ALL}           {cat}")
    print(
        f"{Style.BRIGHT}Location / Zone:{Style.RESET_ALL}    {eff_loc or 'Local Detection'}"
    )
    print(
        f"{Style.BRIGHT}Collector ID:{Style.RESET_ALL}       {service.pipeline.collector_id}"
    )
    print("-" * 65)
    print(
        f"{Fore.LIGHTCYAN_EX}[GMAPS]      {Style.RESET_ALL}Harvesting business listings & public phone numbers..."
    )

    try:
        leads = await service.get_local_leads(query=cat, location=eff_loc)

        print("\n" + "=" * 65)
        print(
            f"  {Style.BRIGHT}GOOGLE MAPS RESULTS ({len(leads)} Leads Found){Style.RESET_ALL}"
        )
        print("=" * 65)

        if leads:
            for i, lead in enumerate(leads, 1):
                print(
                    f"\n{Fore.CYAN}[Place #{i}] {Style.BRIGHT}{lead.get('business_name', 'Unknown')}{Style.RESET_ALL}"
                )
                if lead.get("phone_number"):
                    print(
                        f"  {Style.BRIGHT}Phone Number:{Style.RESET_ALL} {Fore.GREEN}{lead.get('phone_number')}{Style.RESET_ALL}"
                    )
                if lead.get("rating"):
                    reviews = (
                        f"({lead.get('reviews_count')} reviews)"
                        if lead.get("reviews_count")
                        else ""
                    )
                    print(
                        f"  {Style.BRIGHT}Rating:{Style.RESET_ALL}       {lead.get('rating')} ⭐ {reviews}"
                    )
                if lead.get("address"):
                    print(
                        f"  {Style.BRIGHT}Address:{Style.RESET_ALL}      {lead.get('address')}"
                    )
                if lead.get("category"):
                    print(
                        f"  {Style.BRIGHT}Category:{Style.RESET_ALL}     {lead.get('category')}"
                    )
                if lead.get("website"):
                    print(
                        f"  {Style.BRIGHT}Website:{Style.RESET_ALL}      {lead.get('website')}"
                    )
                if lead.get("maps_url"):
                    print(
                        f"  {Style.BRIGHT}Maps Link:{Style.RESET_ALL}    {lead.get('maps_url')}"
                    )

            if output_path:
                fmt = (output_format or "json").lower()
                content = (
                    DataExporter.to_csv(leads)
                    if fmt == "csv"
                    else DataExporter.to_json(leads)
                )
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(
                    f"\n{Fore.GREEN}[EXPORT] Saved {len(leads)} Google Maps leads to {output_path} ({fmt.upper()}){Style.RESET_ALL}"
                )
        else:
            print(
                f"\n{Fore.YELLOW}No Google Maps listings found for '{query}'.{Style.RESET_ALL}"
            )

    except Exception as e:
        print(
            f"\n{Fore.RED}[ERROR] Google Maps extraction failed: {e}{Style.RESET_ALL}"
        )


async def execute_query(
    query: str,
    target_urls: list[str] | None = None,
    engine: str = "auto",
    output_path: str | None = None,
    output_format: str | None = None,
    verbose: bool = False,
):
    """Execute scraping workflow directly from CLI (Supports Dual-Engine)."""
    setup_logging(verbose=verbose, is_cli=True)
    settings = get_settings()
    urls = target_urls or []

    # Decide engine
    engine_choice = engine.lower()
    is_brightdata = (engine_choice == "brightdata") or (
        engine_choice == "auto"
        and settings.BRIGHTDATA
        and (any("indiamart" in u.lower() for u in urls) or not urls)
    )

    if is_brightdata and engine_choice != "local":
        print("\n" + "=" * 65)
        print(
            f"  {Style.BRIGHT}SCRAPE THE VERSE - BRIGHT DATA FAST-PATH{Style.RESET_ALL}"
        )
        print("=" * 65)
        print(f"{Style.BRIGHT}Query:{Style.RESET_ALL}        {query}")
        if urls:
            print(f"{Style.BRIGHT}Target URLs ({len(urls)}):{Style.RESET_ALL}")
            for u in urls:
                print(f"  - {u}")
        print(
            f"{Style.BRIGHT}Engine Mode:{Style.RESET_ALL}  {Fore.GREEN}Bright Data Scraper Studio (Cloud Fast-Path){Style.RESET_ALL}"
        )
        print("-" * 65)
        print(
            f"{Fore.LIGHTCYAN_EX}[PIPELINE]   {Style.RESET_ALL}Executing cloud collectors..."
        )

        service = BrightDataService(settings=settings)
        task = ScrapingTask(
            task_id="cli_fastpath",
            objective=query,
            target_urls=urls or [service.pipeline.format_search_url(query)],
        )
        res = await service.execute_task(task)

        print("\n" + "=" * 65)
        print(
            f"  {Style.BRIGHT}SCRAPING RESULTS ({len(res.records)} Records){Style.RESET_ALL}"
        )
        print("=" * 65)
        if res.records:
            for i, r in enumerate(res.records, 1):
                print(f"\n{Fore.CYAN}[Record {i}]{Style.RESET_ALL}")
                for k, v in r.items():
                    print(f"  {Style.BRIGHT}{k}:{Style.RESET_ALL} {v}")
            if output_path:
                fmt = (output_format or "json").lower()
                content = (
                    DataExporter.to_csv(res.records)
                    if fmt == "csv"
                    else DataExporter.to_json(res.records)
                )
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(
                    f"\n{Fore.GREEN}[EXPORT] Saved {len(res.records)} records to {output_path}{Style.RESET_ALL}"
                )
        else:
            print(
                f"{Fore.YELLOW}No records returned from Bright Data.{Style.RESET_ALL}"
            )
        return

    # Native Multi-Agent LangGraph Engine
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

    print("\n" + "=" * 65)
    print(
        f"  {Style.BRIGHT}SCRAPE THE VERSE - NATIVE MULTI-AGENT ENGINE{Style.RESET_ALL}"
    )
    print("=" * 65)
    print(f"{Style.BRIGHT}Query:{Style.RESET_ALL}        {query}")
    if urls:
        print(f"{Style.BRIGHT}Target URLs ({len(urls)}):{Style.RESET_ALL}")
        for u in urls:
            print(f"  - {u}")
    print(
        f"{Style.BRIGHT}Engine Mode:{Style.RESET_ALL}  {Fore.CYAN}Native Playwright + Ollama Qwen3:8b + Self-Healing{Style.RESET_ALL}"
    )
    print("-" * 65)
    print(
        f"{Fore.LIGHTCYAN_EX}[PIPELINE]   {Style.RESET_ALL}Starting Multi-Agent Workflow (Planner -> Scraper -> Extractor -> Validator)..."
    )

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
            status_color = (
                Fore.GREEN
                if output.status == "success"
                else (Fore.YELLOW if output.status == "partial" else Fore.RED)
            )
            health_val = output.metadata.get("health_score", 0.0)
            quality_val = output.metadata.get("quality_score", 0.0)
            val_status = output.metadata.get("validation_status", "unknown")

            print(
                f"{Style.BRIGHT}Status:{Style.RESET_ALL}        {status_color}{output.status.upper()}{Style.RESET_ALL}"
            )
            print(
                f"{Style.BRIGHT}Health Score:{Style.RESET_ALL}  {health_val:.2f} / 1.00 ({val_status.capitalize()})"
            )
            print(
                f"{Style.BRIGHT}Quality Score:{Style.RESET_ALL} {quality_val:.2f} / 1.00"
            )
            print(
                f"{Style.BRIGHT}Record Count:{Style.RESET_ALL}  {len(output.records)}"
            )
            print("-" * 65)

            if output.records:
                for i, r in enumerate(output.records, 1):
                    print(f"\n{Fore.CYAN}[Record {i}]{Style.RESET_ALL}")
                    for k, v in r.items():
                        print(f"  {Style.BRIGHT}{k}:{Style.RESET_ALL} {v}")
            else:
                print(
                    f"\n{Fore.YELLOW}No structured records extracted.{Style.RESET_ALL}"
                )

            if output_path and output.records:
                fmt = (output_format or "json").lower()
                content = (
                    DataExporter.to_csv(output.records)
                    if fmt == "csv"
                    else DataExporter.to_json(output.records)
                )
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(
                    f"\n{Fore.GREEN}[EXPORT] Saved {len(output.records)} records to {output_path} ({fmt.upper()}){Style.RESET_ALL}"
                )

        else:
            print(f"{Fore.RED}No output produced.{Style.RESET_ALL}")

    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Scraping execution failed: {e}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape_the_Verse CLI: Dual-Engine Web Scraper & B2B Lead Generator"
    )
    parser.add_argument(
        "query",
        nargs="?",
        type=str,
        help="Plain language query or product name (e.g. 'solar panels', 'packaging boxes')",
    )
    parser.add_argument(
        "-u",
        "--urls",
        nargs="+",
        default=None,
        help="One or more target URLs (separated by spaces or commas)",
    )
    parser.add_argument(
        "-e",
        "--engine",
        type=str,
        default="auto",
        choices=["auto", "brightdata", "local"],
        help="Scraping engine to use (brightdata, local, auto). Default: auto",
    )
    parser.add_argument(
        "--leads",
        action="store_true",
        help="Run 2-Tier B2B Lead Generation (Discovery + Company Profile Enrichment)",
    )
    parser.add_argument(
        "--maps",
        action="store_true",
        help="Run Google Maps Local Lead Discovery (Harvests business name, phone, address, ratings)",
    )
    parser.add_argument(
        "--check-brightdata",
        action="store_true",
        help="Inspect and verify Bright Data collector configuration and credentials",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file path to save results (e.g. results.csv or results.json)",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="json",
        choices=["json", "csv", "ndjson"],
        help="Export format (default: json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug logs",
    )

    args = parser.parse_args()

    if args.check_brightdata:
        asyncio.run(check_brightdata_health(verbose=args.verbose))
        return

    # Normalize URLs from args
    target_urls: list[str] = []
    if args.urls:
        for u in args.urls:
            for piece in u.split(","):
                clean = piece.strip()
                if clean:
                    target_urls.append(clean)

    if args.maps:
        query_text = args.query or "plumbers in Chennai"
        asyncio.run(
            execute_gmaps_leads(
                query=query_text,
                output_path=args.output,
                output_format=args.format,
                verbose=args.verbose,
            )
        )
        return

    if args.leads:
        query_text = args.query or "solar panels"
        asyncio.run(
            execute_lead_gen(
                query=query_text,
                enrich=True,
                output_path=args.output,
                output_format=args.format,
                verbose=args.verbose,
            )
        )
        return

    if args.query:
        asyncio.run(
            execute_query(
                query=args.query,
                target_urls=target_urls,
                engine=args.engine,
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
        user_query = input("\nEnter your scraping query (or product name): ").strip()
        if not user_query:
            print("No query provided. Exiting.")
            sys.exit(0)
        mode = input("Run as B2B Lead Generator? (y/N): ").strip().lower()
        if mode in ("y", "yes"):
            asyncio.run(
                execute_lead_gen(
                    query=user_query,
                    enrich=True,
                    output_path=args.output,
                    output_format=args.format,
                    verbose=args.verbose,
                )
            )
        else:
            raw_urls = input(
                "Enter target URLs (separated by commas, or press Enter to skip): "
            ).strip()
            interactive_urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
            asyncio.run(
                execute_query(
                    query=user_query,
                    target_urls=interactive_urls,
                    engine=args.engine,
                    output_path=args.output,
                    output_format=args.format,
                    verbose=args.verbose,
                )
            )


if __name__ == "__main__":
    main()
