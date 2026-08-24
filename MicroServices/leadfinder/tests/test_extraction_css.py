from leadfinder.extraction.css import CSSExtractor
from leadfinder.extraction.schema import ExtractionSchema, FieldRule


def test_css_extraction_with_base_selector():
    html = """
    <div class="products-list">
        <div class="product-card">
            <h2 class="title">Wireless Mouse</h2>
            <span class="price">$25.99</span>
            <a class="link" href="https://example.com/item/1">View</a>
        </div>
        <div class="product-card">
            <h2 class="title">Mechanical Keyboard</h2>
            <span class="price">$89.00</span>
            <a class="link" href="https://example.com/item/2">View</a>
        </div>
    </div>
    """
    schema = ExtractionSchema(
        base_selector=".product-card",
        fields=[
            FieldRule(name="product_name", selector=".title"),
            FieldRule(name="price", selector=".price"),
            FieldRule(name="product_url", selector=".link", attribute="href"),
        ],
    )

    extractor = CSSExtractor()
    records = extractor.extract(html, schema)

    assert len(records) == 2
    assert records[0]["product_name"] == "Wireless Mouse"
    assert records[0]["price"] == "$25.99"
    assert records[0]["product_url"] == "https://example.com/item/1"
    assert records[1]["product_name"] == "Mechanical Keyboard"


def test_css_extraction_single_container():
    html = """
    <html>
        <body>
            <h1 id="headline">Breaking Tech News</h1>
            <p class="author">By Jane Doe</p>
        </body>
    </html>
    """
    schema = ExtractionSchema(
        fields=[
            FieldRule(name="title", selector="#headline"),
            FieldRule(name="author", selector=".author"),
        ]
    )

    extractor = CSSExtractor()
    records = extractor.extract(html, schema)

    assert len(records) == 1
    assert records[0]["title"] == "Breaking Tech News"
    assert records[0]["author"] == "By Jane Doe"
