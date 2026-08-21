import asyncio
import gc
import os
import sys
import time
import tracemalloc
import statistics
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath("."))

from leadfinder.crawler.block_detector import BlockDetector
from leadfinder.crawler.circuit_breaker import DomainCircuitBreaker
from leadfinder.crawler.rate_limiter import DomainRateLimiter
from leadfinder.crawler.url_validator import UrlSecurityValidator
from leadfinder.extraction.cleaner import HTMLCleaner
from leadfinder.extraction.dedup import RecordDeduplicator
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.grid_cards import GridCardExtractor
from leadfinder.extraction.schema import RawPage
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.engine import ValidationEngine

# Mock HTML Generator for High-Throughput Benchmarking
def generate_mock_html(num_cards: int = 10) -> str:
    cards = []
    for i in range(num_cards):
        cards.append(f"""
        <article class="product-item">
            <h2 class="product-title">Benchmark Item #{i}</h2>
            <p class="description">High-performance extraction benchmark payload</p>
            <span class="price">${10.0 + i:.2f}</span>
            <span class="stock">In Stock</span>
            <a class="link" href="/products/item-{i}">View Product</a>
            <img class="photo" data-src="/images/item-{i}.jpg" src="/placeholder.gif" alt="Item {i}"/>
        </article>
        """)
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Benchmark Catalog</title></head>
    <body>
        <div class="product-grid">
            {''.join(cards)}
        </div>
    </body>
    </html>
    """

async def benchmark_extraction_throughput(url_counts: list[int]):
    print("=== STARTING EXTRACTION ENGINE SCALABILITY BENCHMARK ===")
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="bench_task",
        objective="Extract benchmark items",
        target_urls=["https://bench.example.com/catalog"],
        fields=["title", "price", "link", "image", "description", "stock"],
    )
    
    mock_html = generate_mock_html(num_cards=10) # 10 records per page
    
    results = {}

    for count in url_counts:
        print(f"\n--- Benchmarking {count:,} URLs (Payload: {count * 10:,} records) ---")
        gc.collect()
        tracemalloc.start()
        
        latencies = []
        start_time = time.time()
        
        # Batch size for memory safety
        batch_size = 500
        total_records_extracted = 0
        
        for i in range(0, count, batch_size):
            current_batch = min(batch_size, count - i)
            
            # Execute batch extraction
            pages = [
                RawPage(url=f"https://bench.example.com/page/{i+j}", html=mock_html)
                for j in range(current_batch)
            ]
            for page in pages:
                t0 = time.time()
                ext_res = await engine.extract_async(raw_content=page, task=task)
                latencies.append((time.time() - t0) * 1000.0) # ms
                total_records_extracted += len(ext_res.records)
        
        total_duration = time.time() - start_time
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg_latency = statistics.mean(latencies)
        throughput_rps = count / total_duration
        pages_per_min = throughput_rps * 60.0
        
        results[count] = {
            "urls": count,
            "total_records": total_records_extracted,
            "duration_sec": round(total_duration, 2),
            "throughput_rps": round(throughput_rps, 1),
            "pages_per_min": round(pages_per_min, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "peak_ram_mb": round(peak_mem / (1024 * 1024), 2),
        }
        print(f"Results for {count:,} URLs:")
        print(f"  Duration: {total_duration:.2f}s | Throughput: {throughput_rps:.1f} RPS ({pages_per_min:.0f} pages/min)")
        print(f"  Latency: Avg={avg_latency:.2f}ms | p50={p50:.2f}ms | p95={p95:.2f}ms | p99={p99:.2f}ms")
        print(f"  Memory Peak: {peak_mem / (1024 * 1024):.2f} MB")
        
    return results

async def benchmark_concurrency_limits():
    print("\n=== CONCURRENCY & BOTTLENECK ANALYSIS ===")
    
    # Test 1: In-memory URL Deduplication Scalability (1M URLs)
    print("\n--- Testing URL Deduplication at 1,000,000 URLs ---")
    urls_1m = [f"https://example.com/products/item-{i % 500000}" for i in range(1000000)] # 50% duplicate rate
    t0 = time.time()
    tracemalloc.start()
    
    seen = set()
    unique_count = 0
    for u in urls_1m:
        if u not in seen:
            seen.add(u)
            unique_count += 1
    t_dedup = time.time() - t0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Deduplicated 1,000,000 URLs in {t_dedup:.3f}s -> {unique_count:,} unique URLs.")
    print(f"RAM peak consumed by 1M set: {peak_mem / (1024 * 1024):.2f} MB")

    # Test 2: Rate Limiter & Circuit Breaker Scalability across 10,000 Domains
    print("\n--- Testing Rate Limiter & Circuit Breaker across 10,000 Domains ---")
    limiter = DomainRateLimiter(requests_per_second=50)
    breaker = DomainCircuitBreaker(failure_threshold=5)
    t0 = time.time()
    for i in range(10000):
        domain_url = f"https://domain-{i}.com/page"
        breaker.allow_request(domain_url)
        limiter.record_429(domain_url, retry_after_seconds=1.0)
    t_domains = time.time() - t0
    print(f"Evaluated 10,000 unique domains in {t_domains:.3f}s (Rate: {10000 / t_domains:.0f} ops/sec)")

if __name__ == "__main__":
    asyncio.run(benchmark_extraction_throughput([1000, 5000, 10000]))
    asyncio.run(benchmark_concurrency_limits())
