import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
from bs4 import BeautifulSoup
from app.extraction.cleaner import clean_html, HTMLCleaner
from app.extraction.grid_cards import GridCardExtractor
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import RawPage
from app.models.schemas import ScrapingTask
from app.validation.engine import ValidationEngine
from app.extraction.dedup import RecordDeduplicator

async def diagnose():
    engine = ExtractionEngine()
    val_engine = ValidationEngine()
    dedup = RecordDeduplicator()

    # T04 Check
    dirty_records = [
        {"title": "  Smartphone X  ", "price": "$999.00", "url": "https://example.com/p1", "date": "2026-01-01"},
        {"title": "Smartphone X", "price": "$999.00", "url": "https://example.com/p1", "date": "2026-01-01"}, # duplicate
        {"title": "", "price": "$0.00", "url": "https://example.com/p2", "date": None}, # empty title
        {"title": "Tablet &amp; Pen", "price": "149 &euro;", "url": "invalid-url", "date": "unknown"}, # entities, bad url
    ]
    cleaned = dedup.deduplicate(dirty_records)
    print("T04 Cleaned records:", cleaned)
    val_res = val_engine.validate(cleaned, ScrapingTask(task_id="t04", objective="Clean", target_urls=["https://example.com"], fields=["title", "price", "url"]))
    print("T04 Validation status:", val_res.status, "health:", val_res.health_score, "invalid urls:", val_res.url_metrics.invalid_urls)

    # T06 Check (Lazy Loading)
    sample_html_t06 = """
    <div class="product-list">
        <div class="product"><h4 class="name">Product A</h4><img class="lazy" data-src="https://cdn.example.com/lazy-a.jpg" src="placeholder.gif"/></div>
        <div class="product"><h4 class="name">Product B</h4><img class="lazy" data-lazy-src="https://cdn.example.com/lazy-b.jpg"/></div>
        <div class="product"><h4 class="name">Product C</h4><img class="lazy" data-original="https://cdn.example.com/lazy-c.jpg"/></div>
    </div>
    """
    task_t06 = ScrapingTask(task_id="t06", objective="Lazy Images", target_urls=["https://example.com/products"], fields=["name", "image"])
    ext_t06 = await engine.extract_async(raw_content=RawPage(url="https://example.com/products", html=sample_html_t06), task=task_t06)
    print("T06 Extracted records:", ext_t06.records)

    # Edge cases check
    # Check Edge Case A-J
    edge_scores = {}
    task_t02 = ScrapingTask(task_id="t02", objective="Extract products", target_urls=["https://store.example.com/products"], fields=["title", "price"])
    
    # A: Empty
    ext_empty = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=""), task=task_t02)
    edge_scores["A"] = (len(ext_empty.records) == 0, f"Records: {len(ext_empty.records)}")
    
    # B: Malformed HTML
    malformed_html = "<div class='product'><h2 class='title'>Unclosed Tag<p class='price'>$50<div><span>Another</span>"
    ext_malformed = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=malformed_html), task=task_t02)
    edge_scores["B"] = (len(ext_malformed.records) >= 1, f"Records: {len(ext_malformed.records)}")

    # C: Duplicate Records
    dupe_html = """
    <div class="grid">
        <div class="item"><h2 class="title">Item 1</h2><span class="price">$10</span></div>
        <div class="item"><h2 class="title">Item 1</h2><span class="price">$10</span></div>
        <div class="item"><h2 class="title">Item 2</h2><span class="price">$20</span></div>
    </div>
    """
    ext_dupe = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=dupe_html), task=task_t02)
    edge_scores["C"] = (len(ext_dupe.records) == 2, f"Records: {len(ext_dupe.records)}")

    # D: Missing Required Field
    missing_f_html = """
    <div class="grid">
        <div class="item"><h2 class="title">Item 1</h2></div>
        <div class="item"><span class="price">$20</span></div>
    </div>
    """
    ext_missing = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=missing_f_html), task=task_t02)
    edge_scores["D"] = (len(ext_missing.records) == 2, f"Records: {len(ext_missing.records)}, recs: {ext_missing.records}")

    # E: Nested
    nested_html = """
    <div class="category">
        <h1>Laptops</h1>
        <div class="product"><h2 class="title">MacBook Pro</h2><span class="price">$2,499</span></div>
        <div class="product"><h2 class="title">ThinkPad X1</h2><span class="price">$1,899</span></div>
    </div>
    """
    ext_nested = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=nested_html), task=task_t02)
    edge_scores["E"] = (len(ext_nested.records) == 2, f"Records: {len(ext_nested.records)}")

    # F: Unicode
    unicode_html = """
    <div class="multilingual">
        <div class="item"><h2 class="title">வணக்கம் உலகம் (Tamil)</h2><span class="price">₹1,500</span></div>
        <div class="item"><h2 class="title">नमस्ते दुनिया (Hindi)</h2><span class="price">₹2,000</span></div>
        <div class="item"><h2 class="title">مرحبا بالعالم (Arabic)</h2><span class="price">350 ر.س</span></div>
        <div class="item"><h2 class="title">你好世界 (Chinese)</h2><span class="price">¥999</span></div>
        <div class="item"><h2 class="title">Super Rocket 🚀✨ (Emoji)</h2><span class="price">$42.00</span></div>
    </div>
    """
    ext_unicode = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=unicode_html), task=task_t02)
    edge_scores["F"] = (len(ext_unicode.records) == 5, f"Records: {len(ext_unicode.records)}")

    # G: Long
    long_html = "<div class='list'>" + "".join([f"<div class='item'><h2 class='title'>Product #{i}</h2><span class='price'>${i}.00</span></div>" for i in range(1000)]) + "</div>"
    ext_long = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=long_html), task=task_t02)
    edge_scores["G"] = (len(ext_long.records) == 1000, f"Records: {len(ext_long.records)}")

    # H: Popup
    popup_html = """
    <div id="newsletter-popup" class="modal">
        <h2>Subscribe to newsletter!</h2>
        <form><input type="email"/><button>Submit</button></form>
    </div>
    <div class="products">
        <div class="item"><h2 class="title">Real Product 1</h2><span class="price">$89.00</span></div>
        <div class="item"><h2 class="title">Real Product 2</h2><span class="price">$99.00</span></div>
    </div>
    """
    ext_popup = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=popup_html), task=task_t02)
    edge_scores["H"] = (len(ext_popup.records) == 2, f"Records: {len(ext_popup.records)}, recs: {ext_popup.records}")

    # I: Table
    table_html = """
    <table class="data-table">
        <tr><th>title</th><th>price</th></tr>
        <tr><td>Server Rack</td><td>$850</td></tr>
        <tr><td>Switch 48-port</td><td>$450</td></tr>
    </table>
    """
    ext_table = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=table_html), task=task_t02)
    edge_scores["I"] = (len(ext_table.records) == 2, f"Records: {len(ext_table.records)}")

    # J: Random order
    random_order_html = """
    <div class="catalog">
        <div class="item"><span class="price">$120</span><h2 class="title">Item Reverse A</h2></div>
        <div class="item"><h2 class="title">Item Normal B</h2><span class="price">$150</span></div>
    </div>
    """
    ext_random = await engine.extract_async(raw_content=RawPage(url="https://example.com", html=random_order_html), task=task_t02)
    edge_scores["J"] = (len(ext_random.records) == 2, f"Records: {len(ext_random.records)}")

    print("\n--- Edge Cases Detailed ---")
    for k, (passed, info) in edge_scores.items():
        print(f"Edge Case {k}: {passed} | {info}")

asyncio.run(diagnose())
