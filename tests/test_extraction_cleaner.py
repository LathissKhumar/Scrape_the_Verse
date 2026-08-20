"""Unit tests for HTMLCleaner, RawPage content extraction, and entity consolidation."""

import pytest
from app.extraction.cleaner import HTMLCleaner, clean_html
from app.extraction.schema import RawPage
from app.extraction.llm import LLMExtractor
from tests.conftest import MockLLMClient
from app.models.schemas import ScrapingTask


def test_html_cleaner_strips_scripts_styles_and_nav():
    sample_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Sample Page</title>
        <style>.hide { display: none; }</style>
        <script>console.log("tracking");</script>
      </head>
      <body>
        <nav><ul><li><a href="/">Home</a></li></ul></nav>
        <header><h1>Site Header</h1></header>
        <main>
          <h1>The Avengers</h1>
          <p>The Avengers are a fictional team of superheroes appearing in MCU films.<sup class="reference">[1]</sup></p>
          <h2>Key Members</h2>
          <ul>
            <li>Iron Man (Tony Stark)</li>
            <li>Captain America (Steve Rogers)</li>
          </ul>
        </main>
        <aside class="sidebar">Ads and Sidebar Content</aside>
        <div class="reflist"><ol><li>Reference 1: Retrieved May 2021</li></ol></div>
        <footer>Site Footer and Copyright 2026</footer>
      </body>
    </html>
    """
    cleaner = HTMLCleaner()
    cleaned = cleaner.clean_html_to_text(sample_html)

    # Core content must be preserved
    assert "The Avengers" in cleaned
    assert "fictional team of superheroes" in cleaned
    assert "Iron Man (Tony Stark)" in cleaned
    assert "Captain America (Steve Rogers)" in cleaned

    # Boilerplate and noise must be stripped
    assert "console.log" not in cleaned
    assert ".hide" not in cleaned
    assert "Site Header" not in cleaned
    assert "Site Footer" not in cleaned
    assert "Ads and Sidebar Content" not in cleaned
    assert "Retrieved May 2021" not in cleaned
    assert "[1]" not in cleaned


def test_raw_page_get_primary_content_cleans_html():
    raw_html = """
    <div>
      <script>var x = 1;</script>
      <p>Clean paragraph text for extraction.</p>
      <footer class="reflist">Footer citation</footer>
    </div>
    """
    page = RawPage(url="https://example.com", html=raw_html)
    cleaned_text = clean_html(page.get_primary_content())

    assert "Clean paragraph text for extraction." in cleaned_text
    assert "var x = 1;" not in cleaned_text
    assert "Footer citation" not in cleaned_text


def test_llm_extractor_consolidates_entity_records():
    mock_llm = MockLLMClient(response_text='[{"summary": "Mock summary"}]')
    extractor = LLMExtractor(llm_client=mock_llm)

    # Simulated chunk extractions where one chunk extracted summary, and another extracted members & filmography
    chunk_records = [
        {"summary": "The Avengers are a team of superheroes.", "members": None, "filmography": None},
        {"summary": None, "members": "Iron Man, Thor, Hulk", "filmography": "Avengers (2012)"},
        {"summary": "Short note", "members": None, "filmography": "Avengers: Endgame (2019)"},
    ]
    fields = ["summary", "members", "filmography"]

    consolidated = extractor._consolidate_entity_records(chunk_records, fields)

    assert len(consolidated) == 1
    rec = consolidated[0]
    assert rec["summary"] == "The Avengers are a team of superheroes."
    assert rec["members"] == "Iron Man, Thor, Hulk"
    assert rec["filmography"] in ("Avengers (2012)", "Avengers: Endgame (2019)")


@pytest.mark.asyncio
async def test_llm_extractor_single_entity_mode():
    mock_llm = MockLLMClient(response_text='[{"summary": "Assembled superhero team.", "members": "Iron Man, Captain America"}]')
    extractor = LLMExtractor(llm_client=mock_llm)

    task = ScrapingTask(
        task_id="entity_test",
        objective="Get details about the Avengers",
        target_urls=["https://en.wikipedia.org/wiki/Avengers"],
        fields=["summary", "members"],
        is_list=False,
    )

    page = RawPage(
        url="https://en.wikipedia.org/wiki/Avengers",
        html="<p>The Avengers are an assembled superhero team featuring Iron Man and Captain America.</p>",
    )

    results = await extractor.extract_async(page, task)
    assert len(results) == 1
    assert results[0]["summary"] == "Assembled superhero team."
    assert results[0]["members"] == "Iron Man, Captain America"


def test_llm_extractor_sanitizes_price_slogans():
    extractor = LLMExtractor(llm_client=MockLLMClient())
    records = [
        {"product_name": "Scooty A", "price": "सही दाम पर"},
        {"product_name": "Scooty B", "price": "free"},
        {"product_name": "Scooty C", "price": "₹ 97,000"},
    ]
    sanitized = extractor._sanitize_records(records, ["product_name", "price"])
    assert sanitized[0]["price"] is None
    assert sanitized[1]["price"] is None
    assert sanitized[2]["price"] == "₹ 97,000"


def test_html_cleaner_strips_carousel_and_recommendation_widgets():
    html = """
    <main>
      <h1>Main Laptop Results</h1>
      <div class="product">Dell XPS 15 - ₹1,40,000</div>
      <div class="recommendations-carousel" data-widget="carousel">
        <div class="carousel-title">Similar Laptops You May Like</div>
        <div class="card">Asus Vivobook - ₹45,000</div>
      </div>
      <div class="sponsored-banner" data-widget="banner">
        <span>Sponsored Product - ₹12,000</span>
      </div>
    </main>
    """
    cleaner = HTMLCleaner()
    cleaned = cleaner.clean_html_to_text(html)
    assert "Dell XPS 15" in cleaned
    assert "Similar Laptops" not in cleaned
    assert "Asus Vivobook" not in cleaned
    assert "Sponsored Product" not in cleaned

