from leadfinder.crawler.result_models import CrawlResult
from leadfinder.healing.crawler_healing import CrawlerHealingEngine
from leadfinder.healing.schemas import RepairMemoryRecord, RepairType
from leadfinder.healing.semantic_memory import SemanticRepairMemory


def test_semantic_repair_memory_matching():
    sem_mem = SemanticRepairMemory()
    html_shop1 = "<html><body><main><div class='card'><h2>Title</h2><p>Price</p></div></main></body></html>"
    html_shop2 = "<html><body><main><div class='item-card'><h2>Title</h2><p>Price</p></div></main></body></html>"

    rec1 = RepairMemoryRecord(
        domain="brand-a.com",
        signature="sig_a",
        root_cause="SELECTOR_DRIFT",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        successful_patch={"price": ".prod-price"},
        health_before=0.0,
        health_after=1.0,
        strategy="css",
    )
    sem_mem.register_record(rec1, html_shop1)

    matches = sem_mem.find_cross_domain_candidates(
        html_shop2, fields=["price"], similarity_threshold=0.70
    )
    assert len(matches) >= 1
    assert matches[0].domain == "brand-a.com"


def test_crawler_healing_engine_adaptations():
    crawler_healing = CrawlerHealingEngine()
    initial_res = CrawlResult(
        url="https://example.com",
        status_code=200,
        html="<html><body>Loading...</body></html>",
        error="Timeout waiting for selectors",
        timing_ms=30000,
    )
    adaptations = crawler_healing.generate_crawler_adaptations(initial_res, attempt=1)
    assert len(adaptations) >= 2
    assert adaptations[0]["wait_until"] == "networkidle"
    assert adaptations[0]["timeout_ms"] > 30000
