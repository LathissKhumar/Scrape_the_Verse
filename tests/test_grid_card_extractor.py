import pytest
from app.extraction.grid_cards import GridCardExtractor


def test_grid_card_extractor_extracts_product_cards():
    html = """
    <div class="container">
      <article class="product_pod">
        <h3><a href="b1.html" title="Book One">Book One</a></h3>
        <p class="price_color">£12.99</p>
        <p class="instock">In stock</p>
      </article>
      <article class="product_pod">
        <h3><a href="b2.html" title="Book Two">Book Two</a></h3>
        <p class="price_color">£24.50</p>
        <p class="instock">In stock</p>
      </article>
    </div>
    """
    extractor = GridCardExtractor()
    records = extractor.extract(
        html=html, target_fields=["title", "price", "availability"]
    )
    assert len(records) == 2
    assert "Book One" in str(records[0].get("title", ""))
    assert "12.99" in str(records[0].get("price", ""))
    assert "In stock" in str(records[0].get("availability", ""))


def test_grid_card_extractor_extracts_quotes():
    html = """
    <div class="quotes-container">
      <div class="quote">
        <span class="text">“Be yourself; everyone else is already taken.”</span>
        <span>by <small class="author">Oscar Wilde</small></span>
      </div>
      <div class="quote">
        <span class="text">“Two things are infinite: the universe and human stupidity.”</span>
        <span>by <small class="author">Albert Einstein</small></span>
      </div>
    </div>
    """
    extractor = GridCardExtractor()
    records = extractor.extract(html=html, target_fields=["quote", "author"])
    assert len(records) == 2
    assert "Oscar Wilde" in str(records[0].get("author", ""))
    assert "Albert Einstein" in str(records[1].get("author", ""))


def test_grid_card_extractor_empty_html():
    extractor = GridCardExtractor()
    assert extractor.extract(html="", target_fields=["title"]) == []


def test_grid_card_extractor_ignores_recommendation_carousels():
    html = """
    <div class="main-results">
      <div class="product-card" data-id="p1">
        <h2 class="title">Apple iPhone 15</h2>
        <span class="price">₹79,900</span>
      </div>
      <div class="product-card" data-id="p2">
        <h2 class="title">Apple iPhone 14</h2>
        <span class="price">₹69,900</span>
      </div>
    </div>
    <div class="similar-products-carousel" data-widget="carousel">
      <div class="product-card" data-id="c1">
        <span class="price">₹3,999</span>
      </div>
      <div class="product-card" data-id="c2">
        <span class="price">₹1,299</span>
      </div>
      <div class="product-card" data-id="c3">
        <span class="price">₹499</span>
      </div>
    </div>
    """
    extractor = GridCardExtractor()
    records = extractor.extract(html=html, target_fields=["title", "price"])
    assert len(records) == 2
    assert records[0]["title"] == "Apple iPhone 15"
    assert records[1]["title"] == "Apple iPhone 14"


