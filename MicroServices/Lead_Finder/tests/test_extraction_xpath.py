from leadfinder.extraction.xpath import XPathExtractor
from leadfinder.extraction.schema import ExtractionSchema, FieldRule


def test_xpath_extraction_with_base_xpath():
    html = """
    <div id="articles">
        <article class="post">
            <h2>Python 3.12 Features</h2>
            <span class="tag">Programming</span>
            <a href="/post/12">Read More</a>
        </article>
        <article class="post">
            <h2>AI Agents in 2026</h2>
            <span class="tag">AI</span>
            <a href="/post/13">Read More</a>
        </article>
    </div>
    """
    schema = ExtractionSchema(
        base_selector="//article[@class='post']",
        fields=[
            FieldRule(name="title", selector=".//h2"),
            FieldRule(name="category", selector=".//span[@class='tag']"),
            FieldRule(name="link", selector=".//a", attribute="href"),
        ],
    )

    extractor = XPathExtractor()
    records = extractor.extract(html, schema)

    assert len(records) == 2
    assert records[0]["title"] == "Python 3.12 Features"
    assert records[0]["category"] == "Programming"
    assert records[0]["link"] == "/post/12"
    assert records[1]["title"] == "AI Agents in 2026"
