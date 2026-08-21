import os
import sys

sys.path.insert(0, os.path.abspath("."))

from bs4 import BeautifulSoup
from app.extraction.grid_cards import GridCardExtractor

html = """
<html>
<body>
<nav class="sidebar">
  <div class="filter-header">Price</div>
  <div class="price-option">Min</div>
  <div class="price-option">₹5,000</div>
</nav>

<div class="main-content">
  <div class="cPHDOP col-12-12" data-id="MOBG123">
    <div class="tUxRFH">
      <div class="KzDlHZ">REDMI 13C (Starshine Green, 128 GB)</div>
      <div class="Nx9bqj _4b5DiR">₹7,499</div>
      <ul class="G4BRas">
        <li class="J+K0re">4 GB RAM | 128 GB ROM</li>
      </ul>
      <a class="CGtC5Q" href="/redmi-13c-starshine-green-128-gb/p/itm123">View</a>
    </div>
  </div>

  <div class="cPHDOP col-12-12" data-id="MOBG456">
    <div class="tUxRFH">
      <div class="KzDlHZ">REDMI Note 13 5G (Prism Gold, 256 GB)</div>
      <div class="Nx9bqj _4b5DiR">₹15,999</div>
      <ul class="G4BRas">
        <li class="J+K0re">8 GB RAM | 256 GB ROM</li>
      </ul>
      <a class="CGtC5Q" href="/redmi-note-13-5g-prism-gold-256-gb/p/itm456">View</a>
    </div>
  </div>
</div>
</body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")
extractor = GridCardExtractor()
attr_elements = soup.find_all(attrs={"data-id": True})
print(f"attr_elements count: {len(attr_elements)}")

score = extractor._score_item_candidates(attr_elements)
print(f"score for data-id elements: {score}")

rec = extractor._extract_card_fields(attr_elements[0], ["name", "price", "details"])
print(f"extracted card 0: {rec}")

records = extractor.extract(html, target_fields=["name", "price", "details"])
print(f"Full extract records: {records}")
