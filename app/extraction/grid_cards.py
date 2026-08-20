import re
from typing import Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
from app.config.logging import get_logger

logger = get_logger("GRID_CARD_EXTRACTOR")


class GridCardExtractor:
    """Deterministically extracts repeating cards/items (products, quotes, articles) from HTML with robust e-commerce support."""

    CARD_TAGS = ["article", "li", "div", "tr", "section"]
    COMMON_CARD_CLASSES = [
        "product",
        "item",
        "card",
        "quote",
        "result",
        "post",
        "entry",
        "listing",
        "box",
        "row",
        "cphdop",
        "tuxrfh",
        "col-12-12",
        "s-result-item",
    ]

    def extract(
        self,
        html: str,
        target_fields: Optional[list[str]] = None,
        base_url: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Identify repeating card elements and extract structured records."""
        if not html or not html.strip():
            return []

        soup = BeautifulSoup(html, "html.parser")
        
        # Remove noisy sidebar filters, navigation menus, header, and footer
        for noise in soup.find_all(["nav", "aside", "header", "footer", "script", "style", "noscript"]):
            noise.decompose()

        fields = target_fields or ["title", "price", "link", "description"]
        candidate_containers: list[tuple[float, list[Tag]]] = []

        # 1. High-priority: Check explicit e-commerce item attributes (data-id, data-asin, data-item-id, data-component-type)
        for attr in ["data-id", "data-asin", "data-item-id", "data-pid"]:
            attr_elements = soup.find_all(attrs={attr: True})
            if len(attr_elements) >= 2:
                score = self._score_item_candidates(attr_elements)
                candidate_containers.append((score, attr_elements))

        # 2. Check elements grouped by tag and class
        for tag_name in self.CARD_TAGS:
            elements = soup.find_all(tag_name)
            by_class: dict[str, list[Tag]] = {}
            for el in elements:
                classes = " ".join(el.get("class", []))
                if classes:
                    by_class.setdefault(classes, []).append(el)

            for cls_name, items in by_class.items():
                if len(items) >= 2:
                    score = self._score_item_candidates(items, cls_name=cls_name, tag_name=tag_name)
                    candidate_containers.append((score, items))

        if not candidate_containers:
            return []

        # Pick highest scoring container group
        candidate_containers.sort(key=lambda x: x[0], reverse=True)
        best_items = candidate_containers[0][1]

        records: list[dict[str, Any]] = []
        for item in best_items:
            rec = self._extract_card_fields(item, fields, base_url=base_url)
            # Only accept card if at least one meaningful target field has content
            if any(v is not None and str(v).strip() for v in rec.values()):
                records.append(rec)

        return records

    def _score_item_candidates(self, items: list[Tag], cls_name: str = "", tag_name: str = "") -> float:
        """Score candidate card groups based on presence of prices, links, images, and titles."""
        cls_lower = cls_name.lower()
        base_score = float(len(items))

        if any(c in cls_lower for c in self.COMMON_CARD_CLASSES) or tag_name in ("article", "tr"):
            base_score *= 2.0

        currency_symbols = ("$", "£", "€", "¥", "Rs", "₹", "rs.")
        items_with_price = 0
        items_with_title = 0
        items_with_link = 0
        items_with_image = 0

        # Sample up to 10 items for content quality check
        sample = items[:10]
        for it in sample:
            text = it.get_text()
            if any(cur in text for cur in currency_symbols):
                items_with_price += 1
            if it.find(["h1", "h2", "h3", "h4", "h5"]) or it.find("img", alt=True):
                items_with_title += 1
            if it.find("a", href=True):
                items_with_link += 1
            if it.find("img"):
                items_with_image += 1

        sample_len = len(sample)
        if sample_len > 0:
            price_ratio = items_with_price / sample_len
            title_ratio = items_with_title / sample_len
            link_ratio = items_with_link / sample_len
            img_ratio = items_with_image / sample_len

            # Heavy boost if candidate items contain both prices and titles/images (real product cards)
            if price_ratio >= 0.5 and (title_ratio >= 0.5 or img_ratio >= 0.5):
                base_score += len(items) * 25.0
            elif title_ratio >= 0.5 and link_ratio >= 0.5:
                base_score += len(items) * 15.0

        return base_score

    def _extract_card_fields(
        self, card: Tag, target_fields: list[str], base_url: Optional[str] = None
    ) -> dict[str, Any]:
        rec: dict[str, Any] = {}
        for f in target_fields:
            val: Optional[str] = None
            f_lower = f.lower()

            if f_lower in ("title", "name", "heading", "booktitle", "productname", "product_name"):
                # 1. Heading tags (h1-h5)
                for heading_tag in ["h1", "h2", "h3", "h4", "h5"]:
                    h = card.find(heading_tag)
                    if h:
                        t = h.get("title") or h.get_text(strip=True)
                        if t and len(t) > 3 and not any(g in t.lower() for g in ["view", "buy now", "add to cart"]):
                            val = t
                            break

                # 2. Dedicated product title classes in div or span (e.g. Flipkart .KzDlHZ, ._4rR01T, Amazon .a-size-medium)
                if not val:
                    for tag in card.find_all(["div", "span", "p"]):
                        tag_cls = " ".join(tag.get("class", [])).lower()
                        if any(k in tag_cls for k in ["title", "name", "heading", "kzdlhz", "4rr01t", "product", "a-size-medium", "a-size-base-plus"]):
                            txt = tag.get_text(strip=True)
                            if len(txt) > 5 and not any(c in txt for c in ["$", "₹", "£", "€", "Rs", "rs."]):
                                val = txt
                                break

                # 3. Product image alt attribute (extremely consistent on Flipkart, Amazon, Walmart)
                if not val:
                    img = card.find("img", alt=True)
                    if img and img.get("alt"):
                        alt_txt = str(img["alt"]).strip()
                        if len(alt_txt) > 5 and not any(g in alt_txt.lower() for g in ["placeholder", "logo", "icon", "star", "rating", "image"]):
                            val = alt_txt

                # 4. Descriptive product link (must be > 6 chars and not generic action verb)
                if not val:
                    for a in card.find_all("a"):
                        a_title = a.get("title") or a.get_text(strip=True)
                        if a_title and len(a_title) > 6:
                            a_lower = a_title.lower()
                            if not any(g in a_lower for g in ["view", "buy now", "add to cart", "learn more", "details", "click here", "read more"]):
                                val = a_title
                                break

            elif f_lower in ("price", "cost", "amount", "pricing", "current_price"):
                # 1. Dedicated price classes
                price_el = card.find(
                    class_=lambda c: c
                    and any(p in str(c).lower() for p in ["price", "cost", "amount", "nx9bqj", "30jeq3", "a-price-whole"])
                )
                raw_price = price_el.get_text(strip=True) if price_el else ""
                
                # 2. Search for currency symbols in strings
                if not raw_price:
                    for text in card.stripped_strings:
                        if any(cur in text for cur in ["$", "£", "€", "¥", "Rs", "₹", "rs."]):
                            raw_price = text
                            break
                            
                if raw_price:
                    match = re.search(r"([$£€¥₹\u00A3\u20B9]\s*[\d,]+(?:\.\d{1,2})?|Rs\.?\s*[\d,]+(?:\.\d{1,2})?)", raw_price)
                    val = match.group(1).strip() if match else raw_price

            elif f_lower in ("details", "description", "specifications", "specs", "features", "summary"):
                # 1. Feature / specification bullet lists (e.g. Flipkart <ul class="G4BRas">)
                ul = card.find(["ul", "ol"])
                if ul:
                    bullets = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
                    if bullets:
                        val = " | ".join(bullets)

                # 2. Paragraph or description div
                if not val:
                    desc_el = card.find(
                        class_=lambda c: c
                        and any(d in str(c).lower() for d in ["spec", "desc", "detail", "feature", "summary", "g4bras", "1xgfaf"])
                    )
                    if desc_el:
                        val = desc_el.get_text(" | ", strip=True)

                if not val:
                    p = card.find("p")
                    if p:
                        p_text = p.get_text(strip=True)
                        if len(p_text) > 15:
                            val = p_text

            elif f_lower in ("quote", "text", "quotetext", "content", "statement"):
                text_el = card.find(
                    class_=lambda c: c
                    and any(t in str(c).lower() for t in ["text", "quote", "content"])
                )
                if text_el:
                    val = text_el.get_text(strip=True)

            elif f_lower in ("author", "creator", "writer", "by"):
                author_el = card.find(
                    class_=lambda c: c
                    and any(a in str(c).lower() for a in ["author", "creator", "writer", "user"])
                )
                if author_el:
                    val = author_el.get_text(strip=True)
                else:
                    small = card.find("small")
                    if small:
                        val = small.get_text(strip=True)

            elif f_lower in ("link", "url", "href", "producturl", "pageurl"):
                a = card.find("a", href=True)
                if a:
                    raw_href = a["href"]
                    val = urljoin(base_url, raw_href) if base_url else raw_href

            elif f_lower in ("image", "img", "thumbnail", "picture", "image_url", "imageurl", "imagesrc"):
                img = card.find("img")
                if img:
                    raw_src = None
                    lazy_attrs = ["data-src", "data-lazy-src", "data-original", "data-srcset"]
                    for attr in lazy_attrs:
                        attr_val = img.get(attr)
                        if attr_val and isinstance(attr_val, str) and not any(p in attr_val.lower() for p in ["placeholder", "blank.gif", "spacer.gif", "data:image/svg"]):
                            raw_src = attr_val.split(",")[0].strip().split(" ")[0]
                            break

                    if not raw_src:
                        source = card.find("source")
                        if source and source.get("srcset"):
                            raw_src = source["srcset"].split(",")[0].strip().split(" ")[0]

                    if not raw_src and img.get("src"):
                        raw_src = img["src"]

                    if raw_src:
                        val = urljoin(base_url, raw_src) if base_url else raw_src

                # Fallback to CSS background-image on card or child styled elements
                if not val:
                    for elem in [card] + card.find_all(attrs={"style": True}):
                        style_attr = elem.get("style", "")
                        bg_match = re.search(r"background(?:-image)?\s*:\s*[^;]*url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", style_attr, re.IGNORECASE)
                        if bg_match:
                            bg_url = bg_match.group(1).strip()
                            if bg_url and not bg_url.startswith("data:"):
                                val = urljoin(base_url, bg_url) if base_url else bg_url
                                break

            elif f_lower in ("availability", "stock", "status", "instock"):
                stock_el = card.find(
                    class_=lambda c: c
                    and any(s in str(c).lower() for s in ["stock", "availability", "status"])
                )
                if stock_el:
                    val = stock_el.get_text(strip=True)

            elif f_lower in ("rating", "stars", "score", "review_rating"):
                rating_el = card.find(
                    class_=lambda c: c and any(r in str(c).lower() for r in ["rating", "star", "review", "score", "x1dtvi", "5_whn1"])
                )
                if rating_el:
                    val = rating_el.get_text(strip=True)

            if not val:
                # Direct class matching fallback
                el = card.find(class_=lambda c: c and f_lower in str(c).lower())
                if el:
                    val = el.get_text(strip=True)

            rec[f] = val

        return rec
