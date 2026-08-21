import asyncio
import os
import sys
import time
from urllib.parse import urljoin

sys.path.insert(0, os.path.abspath("."))

from leadfinder.graph.workflow import create_scraping_workflow
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.config.settings import get_settings


async def run_stress_test():
    print("\n" + "=" * 70)
    print("  ULTRA-COMPLEX SCRAPING STRESS TEST & NOISE AUDIT")
    print("=" * 70)

    workflow = create_scraping_workflow()

    test_cases = [
        {
            "name": "E-Commerce Catalog with Image URLs, Pricing & Availability",
            "query": "Extract the title, price, image URL, and availability for all books on this catalog page",
            "urls": ["https://books.toscrape.com/catalogue/page-1.html"],
            "expected_fields": ["title", "price", "image", "availability"],
        },
        {
            "name": "Nested Quotes, Authors & Tag Lists",
            "query": "Extract the quote text, author name, and tags for each quote",
            "urls": ["https://quotes.toscrape.com/"],
            "expected_fields": ["quote", "author", "tags"],
        },
        {
            "name": "Deep Single-Product Page with Table Metadata & Thumbnail",
            "query": "Extract the book title, UPC code, price tax excluded, stock availability, and main image",
            "urls": ["https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"],
            "expected_fields": ["title", "upc", "price", "availability", "image"],
        },
    ]

    results_summary = []
    flaws_found = []

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] Executing Stress Test: {tc['name']}")
        print(f"Query: {tc['query']}")
        print(f"URLs:  {tc['urls']}")
        print("-" * 70)

        start_time = time.time()
        initial_state: ScrapingGraphState = {
            "task_id": f"stress_ultra_{idx}_{int(time.time())}",
            "original_user_query": tc["query"],
            "target_urls": tc["urls"],
            "repair_attempt": 0,
        }

        try:
            res = await workflow.ainvoke(initial_state)
            elapsed = time.time() - start_time
            output = res.get("final_output")

            if not output:
                print(f"[FAIL] No output produced for {tc['name']}")
                flaws_found.append(f"{tc['name']}: No output returned from graph workflow.")
                continue

            records = output.records
            health_score = output.metadata.get("health_score", 0.0)
            quality_score = output.metadata.get("quality_score", 0.0)

            print(f"Elapsed Time:  {elapsed:.2f}s")
            print(f"Status:        {output.status.upper()}")
            print(f"Health Score:  {health_score:.2f}")
            print(f"Quality Score: {quality_score:.2f}")
            print(f"Record Count:  {len(records)}")

            # --- NOISE & FLAW AUDIT ---
            print("\n--- DETAILED RECORD AUDIT ---")
            for i, r in enumerate(records[:3], 1):
                print(f"Record #{i}: {r}")

            # Check 1: Relative Image URLs instead of Absolute URLs
            for i, r in enumerate(records):
                for k, v in r.items():
                    if any(img_key in k.lower() for img_key in ["image", "img", "thumbnail", "picture"]):
                        if v and isinstance(v, str):
                            if v.startswith("../") or v.startswith("/"):
                                flaw_msg = f"Relative image URL not resolved: field '{k}' = '{v}'"
                                if flaw_msg not in flaws_found:
                                    flaws_found.append(flaw_msg)

                    # Check 2: HTML Tags or Entities remaining inside values (noise)
                    if v and isinstance(v, str):
                        if "<" in v and ">" in v:
                            flaw_msg = f"Unstripped HTML tag noise in record #{i} field '{k}': '{v[:40]}...'"
                            if flaw_msg not in flaws_found:
                                flaws_found.append(flaw_msg)
                        if "&nbsp;" in v or "&#" in v:
                            flaw_msg = f"Unescaped HTML entity noise in field '{k}': '{v}'"
                            if flaw_msg not in flaws_found:
                                flaws_found.append(flaw_msg)

            # Check 3: Missing Requested Fields / Null rates
            missing_fields = []
            for ef in tc["expected_fields"]:
                has_field = any(r.get(ef) is not None and str(r.get(ef)).strip() for r in records)
                if not has_field:
                    missing_fields.append(ef)

            if missing_fields:
                flaw_msg = f"Task '{tc['name']}' failed to extract requested fields: {missing_fields}"
                flaws_found.append(flaw_msg)

            results_summary.append({
                "name": tc["name"],
                "records": len(records),
                "health": health_score,
                "time": elapsed,
                "status": "PASS" if health_score >= 0.80 else "DEGRADED",
            })

        except Exception as e:
            print(f"[ERROR] Exception during {tc['name']}: {e}")
            flaws_found.append(f"{tc['name']} crashed with exception: {e}")

    print("\n" + "=" * 70)
    print("  STRESS TEST FINAL RESULTS & AUDIT REPORT")
    print("=" * 70)
    for s in results_summary:
        print(f"[{s['status']}] {s['name']} | Records: {s['records']} | Health: {s['health']:.2f} | Time: {s['time']:.2f}s")

    print("\n" + "=" * 70)
    print(f"  DETECTED FLAWS & NOISE FINDINGS ({len(flaws_found)})")
    print("=" * 70)
    if flaws_found:
        for i, f in enumerate(flaws_found, 1):
            print(f"{i}. {f}")
    else:
        print("Zero flaws or noise detected! All records are pristine.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_stress_test())
