import pytest
from leadfinder.extraction.grid_cards import GridCardExtractor
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.schema import RawPage
from leadfinder.models.schemas import ScrapingTask

@pytest.mark.asyncio
async def test_lazy_loading_placeholder_precedence():
    html = """
    <div class="product-grid">
        <div class="item">
            <h3 class="name">Product 1</h3>
            <img class="lazy" data-src="https://cdn.example.com/real-image-1.jpg" src="/images/placeholder.gif" alt="P1"/>
        </div>
        <div class="item">
            <h3 class="name">Product 2</h3>
            <img class="lazy" data-lazy-src="https://cdn.example.com/real-image-2.jpg" src="data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=" alt="P2"/>
        </div>
        <div class="item">
            <h3 class="name">Product 3</h3>
            <img class="lazy" data-original="https://cdn.example.com/real-image-3.jpg" src="/spacer.gif" alt="P3"/>
        </div>
    </div>
    """
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t_lazy",
        objective="Extract products",
        target_urls=["https://store.example.com/products"],
        fields=["name", "image"],
    )
    result = await engine.extract_async(
        raw_content=RawPage(url="https://store.example.com/products", html=html),
        task=task,
    )
    records = result.records
    assert len(records) == 3
    assert records[0]["image"] == "https://cdn.example.com/real-image-1.jpg"
    assert records[1]["image"] == "https://cdn.example.com/real-image-2.jpg"
    assert records[2]["image"] == "https://cdn.example.com/real-image-3.jpg"

@pytest.mark.asyncio
async def test_css_background_image_extraction():
    html = """
    <div class="listing">
        <div class="card" style="background-image: url('https://cdn.example.com/hero1.jpg');">
            <h3 class="title">Luxury Villa</h3>
            <span class="price">$1,200,000</span>
        </div>
        <div class="card" style="background-image: url('/media/hero2.png');">
            <h3 class="title">Modern Apartment</h3>
            <span class="price">$450,000</span>
        </div>
    </div>
    """
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t_bg",
        objective="Extract properties",
        target_urls=["https://realestate.example.com/listings"],
        fields=["title", "price", "image"],
    )
    result = await engine.extract_async(
        raw_content=RawPage(url="https://realestate.example.com/listings", html=html),
        task=task,
    )
    records = result.records
    assert len(records) == 2
    assert records[0]["image"] == "https://cdn.example.com/hero1.jpg"
    assert records[1]["image"] == "https://realestate.example.com/media/hero2.png"

@pytest.mark.asyncio
async def test_html_entity_unescaping():
    html = """
    <div class="catalog">
        <div class="item">
            <h3 class="title">Tom &amp; Jerry &quot;Classic&quot; Edition</h3>
            <span class="price">19.99 &euro;</span>
        </div>
        <div class="item">
            <h3 class="title">Rock &apos;n&apos; Roll Guitar</h3>
            <span class="price">&pound;299.00</span>
        </div>
    </div>
    """
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t_entities",
        objective="Extract items",
        target_urls=["https://store.example.com/items"],
        fields=["title", "price"],
    )
    result = await engine.extract_async(
        raw_content=RawPage(url="https://store.example.com/items", html=html),
        task=task,
    )
    records = result.records
    assert len(records) == 2
    assert records[0]["title"] == 'Tom & Jerry "Classic" Edition'
    assert "€" in records[0]["price"] or "19.99" in records[0]["price"]
    assert records[1]["title"] == "Rock 'n' Roll Guitar"
    assert "£" in records[1]["price"]
