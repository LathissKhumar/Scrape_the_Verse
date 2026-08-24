"""Link harvester engine extracting canonical product/item detail URLs from search results."""

import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger("CRAWLER_LINK_HARVESTER")


class LinkHarvesterEngine:
    """Discovers and extracts canonical product/item detail URLs from search and catalog listing pages."""

    DETAIL_URL_PATTERNS = [
        re.compile(r"/p/itm[a-zA-Z0-9]+", re.IGNORECASE),  # Flipkart
        re.compile(r"/dp/[A-Z0-9]+", re.IGNORECASE),  # Amazon
        re.compile(r"/gp/product/[A-Z0-9]+", re.IGNORECASE),  # Amazon alt
        re.compile(r"/ip/[a-zA-Z0-9_-]+/\d+", re.IGNORECASE),  # Walmart
        re.compile(r"/product[s]?/[a-zA-Z0-9_-]+", re.IGNORECASE),  # Generic / Shopify
        re.compile(r"/item/[a-zA-Z0-9_-]+", re.IGNORECASE),  # Generic
        re.compile(r"/pd/[a-zA-Z0-9_-]+", re.IGNORECASE),  # Generic
        re.compile(r"/proddetail/[a-zA-Z0-9_-]+", re.IGNORECASE),  # IndiaMART
        re.compile(
            r"/catalogue/[a-zA-Z0-9_-]+_\d+/index\.html", re.IGNORECASE
        ),  # BooksToScrape
    ]

    EXCLUDE_PATTERNS = [
        re.compile(
            r"/(account|login|signup|signin|cart|checkout|help|contact|about|privacy|terms|cookie)",
            re.IGNORECASE,
        ),
        re.compile(r"\.(pdf|png|jpg|jpeg|gif|webp|svg|css|js|ico)$", re.IGNORECASE),
    ]

    def harvest_detail_links(
        self,
        html: str,
        base_url: str,
        max_links: int = 20,
    ) -> list[str]:
        """Parse HTML, locate candidate product detail URLs, normalize to absolute URLs, and deduplicate."""
        if not html or not html.strip():
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Strip header, footer, and navigation noise
        for noise in soup.find_all(["nav", "footer", "header", "script", "style"]):
            noise.decompose()

        discovered: list[str] = []
        seen_urls: set[str] = set()

        base_domain = urlparse(base_url).netloc.lower()

        # 1. First pass: Explicit product pattern matching on all anchor links
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Restrict to same host/domain
            if (
                parsed.netloc.lower() != base_domain
                and not parsed.netloc.lower().endswith("." + base_domain)
            ):
                continue

            # Check exclusions
            if any(exc.search(parsed.path) for exc in self.EXCLUDE_PATTERNS):
                continue

            # Check pattern match
            is_detail = any(
                pattern.search(parsed.path) for pattern in self.DETAIL_URL_PATTERNS
            )

            # Additional heuristic: anchor is inside a card/listing container with data attributes
            if not is_detail:
                parent_card = a.find_parent(attrs={"data-id": True}) or a.find_parent(
                    attrs={"data-asin": True}
                )
                if (
                    parent_card
                    and len(parsed.path) > 5
                    and not any(
                        exc.search(parsed.path) for exc in self.EXCLUDE_PATTERNS
                    )
                ):
                    is_detail = True

            if is_detail and full_url not in seen_urls:
                seen_urls.add(full_url)
                discovered.append(full_url)
                if len(discovered) >= max_links:
                    break

        logger.info(
            f"Harvested {len(discovered)} product detail links from '{base_url}' (limit={max_links})"
        )
        return discovered
