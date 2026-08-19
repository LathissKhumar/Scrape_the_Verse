import asyncio
from pathlib import Path
import sys
import time
from typing import Any

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Suppress harmless asyncio pipe teardown noise on Windows
def _silence_unraisablehook(unraisable):
    if unraisable.exc_type in (ValueError, ResourceWarning) and "closed pipe" in str(unraisable.exc_value or ""):
        return
    if unraisable.exc_type is RuntimeError and "Event loop is closed" in str(unraisable.exc_value or ""):
        return
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = _silence_unraisablehook

from app.agents.diagnosis import DiagnosisAgent
from app.agents.extraction import ExtractionAgent
from app.agents.healing import HealingAgent
from app.agents.planner import ScrapingPlannerAgent
from app.agents.scraper import ScraperAgent
from app.agents.validation import ValidationAgent
from app.config.settings import get_settings
from app.graph.workflow import create_scraping_workflow
from app.graph.state import ScrapingGraphState
from app.llm.ollama_client import OllamaClient


async def run_stress_query(
    test_name: str,
    query: str,
    urls: list[str],
    expected_fields: list[str],
) -> dict[str, Any]:
    print("\n" + "=" * 70)
    print(f">> RUNNING TEST: {test_name}")
    print("=" * 70)
    print(f"Query:        {query}")
    print(f"Target URLs:  {urls}")
    print(f"Expected:     {expected_fields}")
    print("-" * 70)

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

    state: ScrapingGraphState = {
        "task_id": f"stress_{int(time.time())}",
        "original_user_query": query,
        "target_urls": urls,
        "repair_attempt": 0,
    }

    start_time = time.time()
    try:
        result = await workflow.ainvoke(state)
        elapsed = time.time() - start_time
        output = result.get("final_output")

        status = output.status if output else "failed"
        health = output.metadata.get("health_score", 0.0) if output else 0.0
        records = output.records if output else []
        anomalies = output.metadata.get("anomalies", []) if output else ["No output"]

        print(f"\n[RESULT] Status: {status.upper()} | Health: {health:.2f} | Records: {len(records)} | Time: {elapsed:.2f}s")
        if records:
            print(f"Sample Record: {records[0]}")

        return {
            "test_name": test_name,
            "status": status,
            "health_score": health,
            "records_count": len(records),
            "elapsed_seconds": elapsed,
            "anomalies": anomalies,
            "sample_record": records[0] if records else None,
            "passed": status in ("healthy", "success", "degraded") and len(records) > 0,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] Test failed with exception: {e}")
        return {
            "test_name": test_name,
            "status": "error",
            "health_score": 0.0,
            "records_count": 0,
            "elapsed_seconds": elapsed,
            "error": str(e),
            "passed": False,
        }


async def main():
    print("======================================================================")
    print("  SCRAPE THE VERSE - NATIVE ENGINE HIGH-DIFFICULTY BENCHMARK")
    print("======================================================================")

    test_cases = [
        # Test 1: Parallel Multi-Store / Multi-Book Scraping (Multi-URL concurrent Playwright contexts)
        {
            "name": "Parallel Multi-Page Book Extraction",
            "query": "Extract the title, price, and availability status of each book",
            "urls": [
                "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
                "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
            ],
            "expected_fields": ["title", "price", "availability"],
        },
        # Test 2: Unstructured Rich Content & Nested Quotes Extraction
        {
            "name": "Unstructured Quotes & Authors Extraction",
            "query": "Extract quotes and their authors from this page",
            "urls": [
                "https://quotes.toscrape.com/",
            ],
            "expected_fields": ["quote", "author"],
        },
        # Test 3: Complex Table Extraction with Multiple Attributes
        {
            "name": "Full Table Metadata & Pricing Breakdown Extraction",
            "query": "Extract UPC, product type, price tax excluded, and number of reviews",
            "urls": [
                "https://books.toscrape.com/catalogue/soumission_998/index.html",
            ],
            "expected_fields": ["UPC", "product_type", "price", "reviews"],
        },
    ]

    results = []
    for tc in test_cases:
        res = await run_stress_query(
            test_name=tc["name"],
            query=tc["query"],
            urls=tc["urls"],
            expected_fields=tc["expected_fields"],
        )
        results.append(res)

    print("\n" + "=" * 70)
    print("  BENCHMARK SUMMARY REPORT")
    print("=" * 70)
    total_passed = sum(1 for r in results if r.get("passed"))
    print(f"Total Tests: {len(results)} | Passed: {total_passed}/{len(results)}")
    for r in results:
        pass_icon = "[PASS]" if r.get("passed") else "[FAIL]"
        print(f" - {r['test_name']:<45} {pass_icon} | Status={r['status']} | Health={r['health_score']:.2f} | Time={r['elapsed_seconds']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
