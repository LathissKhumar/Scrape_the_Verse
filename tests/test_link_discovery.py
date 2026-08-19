import pytest
from app.crawler.link_discovery import LinkDiscoveryEngine


def test_link_discovery_basic_resolution():
    engine = LinkDiscoveryEngine()
    html = """
    <html>
      <body>
        <a href="/specs/tech-details">Full Specifications</a>
        <a href="https://example.com/product/123">Product 123</a>
        <a href="https://external.com/ad">External Ad</a>
        <a href="javascript:void(0)">Click Here</a>
        <a href="#overview">Anchor</a>
      </body>
    </html>
    """
    links = engine.extract_candidate_links(
        html=html,
        base_url="https://example.com/item/456",
        query_keywords=["specs", "specifications", "tech"],
        max_links=5,
    )

    assert "https://example.com/specs/tech-details" in links
    assert "https://example.com/product/123" in links
    # External and javascript links should be excluded
    assert "https://external.com/ad" not in links
    assert "javascript:void(0)" not in links


def test_link_discovery_relevance_ranking():
    engine = LinkDiscoveryEngine()
    html = """
    <html>
      <body>
        <a href="/about-us">About Us</a>
        <a href="/contact">Contact</a>
        <a href="/products/mobile-specifications">Detailed Tech Specifications</a>
        <a href="/faq">FAQ</a>
      </body>
    </html>
    """
    links = engine.extract_candidate_links(
        html=html,
        base_url="https://store.example.com",
        query_keywords=["specifications", "tech", "mobile"],
        max_links=2,
    )

    assert len(links) > 0
    # Top ranked link should be the one matching keywords
    assert links[0] == "https://store.example.com/products/mobile-specifications"
