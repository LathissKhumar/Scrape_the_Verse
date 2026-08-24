from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.schemas import RepairMemoryRecord, RepairType


def test_signature_generation_deterministic():
    memory = RepairMemory()
    url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
    html = "<div class='product_pod'><h3><a href='...'>Title</a></h3></div>"
    fields = ["title", "price"]

    sig1 = memory.generate_signature(url=url, html=html, fields=fields)
    sig2 = memory.generate_signature(url=url, html=html, fields=fields)

    assert sig1 == sig2
    assert len(sig1) >= 8


def test_signature_changes_on_dom_change():
    memory = RepairMemory()
    url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
    html_old = "<div class='product_pod'><h3>Title</h3></div>"
    html_new = "<article class='product_item'><h2>Title</h2></article>"
    fields = ["title"]

    sig_old = memory.generate_signature(url=url, html=html_old, fields=fields)
    sig_new = memory.generate_signature(url=url, html=html_new, fields=fields)

    assert sig_old != sig_new


def test_record_and_retrieve_repair_memory():
    memory = RepairMemory()
    record = RepairMemoryRecord(
        domain="books.toscrape.com",
        signature="sig_abc123",
        root_cause="SELECTOR_DRIFT",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        successful_patch={"title": "h3 a"},
        health_before=0.30,
        health_after=0.95,
        strategy="css",
    )
    memory.record_success(record)

    # Exact signature match
    matches = memory.find_similar_repairs(
        domain="books.toscrape.com", signature="sig_abc123"
    )
    assert len(matches) == 1
    assert matches[0].successful_patch == {"title": "h3 a"}

    # Domain match without exact signature
    domain_matches = memory.find_similar_repairs(domain="books.toscrape.com")
    assert len(domain_matches) == 1

    # Unmatched domain
    empty = memory.find_similar_repairs(domain="other-domain.com")
    assert len(empty) == 0
