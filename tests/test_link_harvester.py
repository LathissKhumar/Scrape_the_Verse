from app.crawler.link_harvester import LinkHarvesterEngine


def test_link_harvester_extracts_product_detail_links():
    html = """
    <html><body>
      <div class="product"><a href="/redmi-13c/p/itm123">Redmi 13C</a></div>
      <div class="product"><a href="/redmi-note-13/p/itm456">Redmi Note 13</a></div>
      <div class="footer"><a href="/privacy-policy">Privacy</a></div>
    </body></html>
    """
    harvester = LinkHarvesterEngine()
    links = harvester.harvest_detail_links(html, base_url="https://www.flipkart.com", max_links=10)
    assert len(links) == 2
    assert "https://www.flipkart.com/redmi-13c/p/itm123" in links
    assert "https://www.flipkart.com/redmi-note-13/p/itm456" in links
    assert "https://www.flipkart.com/privacy-policy" not in links


def test_link_harvester_respects_max_links():
    html = """
    <html><body>
      <div><a href="/item-1/dp/B001">Item 1</a></div>
      <div><a href="/item-2/dp/B002">Item 2</a></div>
      <div><a href="/item-3/dp/B003">Item 3</a></div>
    </body></html>
    """
    harvester = LinkHarvesterEngine()
    links = harvester.harvest_detail_links(html, base_url="https://www.amazon.com", max_links=2)
    assert len(links) == 2
    assert "https://www.amazon.com/item-1/dp/B001" in links
    assert "https://www.amazon.com/item-2/dp/B002" in links
