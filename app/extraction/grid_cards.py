from typing import Any, Optional
from bs4 import BeautifulSoup, Tag
from app.config.logging import get_logger

logger = get_logger("GRID_CARD_EXTRACTOR")


class GridCardExtractor:
    """Deterministically extracts repeating cards/items (products, quotes, articles) from HTML."""

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
    ]

    def extract(
        self, html: str, target_fields: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """Identify repeating card elements and extract structured records."""
        if not html or not html.strip():
            return []

        soup = BeautifulSoup(html, "html.parser")
        fields = target_fields or ["title", "price", "link", "description"]

        candidate_containers: list[tuple[int, list[Tag]]] = []
        for tag_name in self.CARD_TAGS:
            elements = soup.find_all(tag_name)
            by_class: dict[str, list[Tag]] = {}
            for el in elements:
                classes = " ".join(el.get("class", []))
                if classes:
                    by_class.setdefault(classes, []).append(el)

            for cls_name, items in by_class.items():
                if len(items) >= 2:
                    cls_lower = cls_name.lower()
                    is_relevant = (
                        any(c in cls_lower for c in self.COMMON_CARD_CLASSES)
                        or tag_name in ("article", "tr")
                    )
                    score = len(items) * (3 if is_relevant else 1)
                    candidate_containers.append((score, items))

        if not candidate_containers:
            return []

        candidate_containers.sort(key=lambda x: x[0], reverse=True)
        best_items = candidate_containers[0][1]

        records: list[dict[str, Any]] = []
        for item in best_items:
            rec = self._extract_card_fields(item, fields)
            # Only accept card if at least one target field has non-empty content
            if any(v is not None and str(v).strip() for v in rec.values()):
                records.append(rec)

        return records

    def _extract_card_fields(
        self, card: Tag, target_fields: list[str]
    ) -> dict[str, Any]:
        rec: dict[str, Any] = {}
        for f in target_fields:
            val: Optional[str] = None
            f_lower = f.lower()

            if f_lower in ("title", "name", "heading", "booktitle", "productname"):
                for heading_tag in ["h1", "h2", "h3", "h4", "a"]:
                    h = card.find(heading_tag)
                    if h:
                        val = h.get("title") or h.get_text(strip=True)
                        if val:
                            break
            elif f_lower in ("price", "cost", "amount", "pricing"):
                price_el = card.find(
                    class_=lambda c: c
                    and any(p in str(c).lower() for p in ["price", "cost", "amount"])
                )
                if price_el:
                    val = price_el.get_text(strip=True)
                else:
                    for text in card.stripped_strings:
                        if any(cur in text for cur in ["$", "£", "€", "¥", "Rs"]):
                            val = text
                            break
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
            elif f_lower in ("link", "url", "href"):
                a = card.find("a", href=True)
                if a:
                    val = a["href"]
            elif f_lower in ("image", "img", "thumbnail", "picture"):
                img = card.find("img")
                if img:
                    val = img.get("src") or img.get("data-src")
            elif f_lower in ("availability", "stock", "status", "instock"):
                stock_el = card.find(
                    class_=lambda c: c
                    and any(s in str(c).lower() for s in ["stock", "availability", "status"])
                )
                if stock_el:
                    val = stock_el.get_text(strip=True)

            if not val:
                # Direct class matching fallback
                el = card.find(class_=lambda c: c and f_lower in str(c).lower())
                if el:
                    val = el.get_text(strip=True)

            rec[f] = val

        return rec
