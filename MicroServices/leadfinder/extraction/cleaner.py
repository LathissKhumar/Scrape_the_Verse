"""DOM cleaner and structured content extractor for converting raw HTML to noise-free article text."""

import re
from typing import Optional
from bs4 import BeautifulSoup, Comment

NOISE_TAGS = [
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "svg",
    "button",
    "iframe",
    "canvas",
]

NOISE_SELECTORS = [
    ".reflist",
    ".reference",
    "sup.reference",
    ".mw-jump-link",
    ".mw-editsection",
    "#mw-navigation",
    "#mw-panel",
    "#mw-head",
    "#footer",
    ".vector-menu",
    ".sidebar",
    ".navbox",
    ".catlinks",
    ".portal",
    ".noprint",
    ".infobox-navbar",
    ".mw-empty-elt",
    # Carousels, recommendation widgets, sponsored banners & ads
    "div[class*='carousel']",
    "div[class*='slider']",
    "div[class*='recommend']",
    "div[class*='similar']",
    "div[class*='sponsored']",
    "div[data-widget*='carousel']",
    "div[data-widget*='recommendation']",
    "div[data-widget*='banner']",
    ".frequently-bought-together",
]

_MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n{3,}")


class HTMLCleaner:
    """Cleans raw HTML by removing boilerplate, navigation, scripts, and citations to extract readable text."""

    def __init__(self, remove_citations: bool = True) -> None:
        self.remove_citations = remove_citations

    def clean_html_to_text(self, html: str, base_url: Optional[str] = None) -> str:
        """Parse raw HTML and extract clean, structured plain text/markdown without boilerplate."""
        if not html or not html.strip():
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # 1. Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. Remove standard noise tags
        for tag_name in NOISE_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 3. Remove CSS selector noise (citations, wiki navigation, headers/footers)
        for selector in NOISE_SELECTORS:
            for el in soup.select(selector):
                el.decompose()

        # 4. Target main content area if present (e.g. Wikipedia #bodyContent, article, main)
        main_content = (
            soup.find("div", {"id": "bodyContent"})
            or soup.find("main")
            or soup.find("article")
            or soup.find("div", {"class": "mw-parser-output"})
            or soup.body
            or soup
        )

        lines: list[str] = []

        for elem in main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "tr"]):
            text = elem.get_text(separator=" ", strip=True)
            if not text:
                continue

            # Format headings
            if elem.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(elem.name[1])
                lines.append(f"\n{'#' * level} {text}\n")
            elif elem.name == "li":
                lines.append(f"- {text}")
            elif elem.name == "tr":
                cells = [td.get_text(" ", strip=True) for td in elem.find_all(["td", "th"])]
                if cells:
                    lines.append(" | ".join(cells))
            else:
                lines.append(f"\n{text}\n")

        cleaned_text = "\n".join(lines)
        # Normalize multiple newlines and whitespace
        cleaned_text = _MULTIPLE_NEWLINES_PATTERN.sub("\n\n", cleaned_text).strip()

        # If tag-based extraction yielded very little text, fallback to get_text
        if len(cleaned_text) < 100:
            cleaned_text = main_content.get_text(separator="\n", strip=True)
            cleaned_text = _MULTIPLE_NEWLINES_PATTERN.sub("\n\n", cleaned_text).strip()

        return cleaned_text


_default_cleaner = HTMLCleaner()


def clean_html(html: str) -> str:
    """Convenience helper to clean HTML to structured text using default settings."""
    return _default_cleaner.clean_html_to_text(html)

