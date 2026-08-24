from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from leadfinder.config.logging import get_logger
from leadfinder.crawler.url_validator import UrlSecurityValidator

logger = get_logger("LINK_DISCOVERY")


class LinkDiscoveryEngine:
    """Discovers, scores, and filters sub-links from rendered page HTML."""

    def __init__(self, security_validator: UrlSecurityValidator | None = None):
        self.security_validator = security_validator or UrlSecurityValidator()

    def extract_candidate_links(
        self,
        html: str,
        base_url: str,
        query_keywords: list[str] | None = None,
        max_links: int = 5,
        same_domain_only: bool = True,
    ) -> list[str]:
        """Extract and rank candidate sub-links from HTML based on query keyword relevance."""
        if not html or not base_url:
            return []

        base_parsed = urlparse(base_url)
        base_netloc = base_parsed.netloc.lower()

        keywords = [k.lower().strip() for k in (query_keywords or []) if k.strip()]
        # Common informative words
        generic_relevant_words = {
            "spec",
            "specs",
            "specification",
            "specifications",
            "detail",
            "details",
            "feature",
            "features",
            "overview",
            "product",
        }
        all_keywords = set(keywords).union(generic_relevant_words)

        soup = BeautifulSoup(html, "html.parser")
        candidate_map: dict[str, float] = {}

        for a_tag in soup.find_all("a", href=True):
            raw_href = a_tag["href"].strip()
            link_text = a_tag.get_text(strip=True).lower()

            if (
                not raw_href
                or raw_href.startswith("#")
                or raw_href.startswith("javascript:")
                or raw_href.startswith("mailto:")
                or raw_href.startswith("tel:")
            ):
                continue

            absolute_url = urljoin(base_url, raw_href)
            parsed = urlparse(absolute_url)

            # Protocol check
            if parsed.scheme not in ("http", "https"):
                continue

            # Same domain check
            if same_domain_only and parsed.netloc.lower() != base_netloc:
                continue

            # SSRF validation check
            if not self.security_validator.is_safe_url(absolute_url):
                continue

            # Skip self/root duplicate
            if absolute_url.rstrip("/") == base_url.rstrip("/"):
                continue

            # Score calculation
            score = 0.0
            href_lower = raw_href.lower()

            for kw in all_keywords:
                if kw in link_text:
                    score += 3.0
                if kw in href_lower:
                    score += 2.0

            # Penalize utility links
            utility_words = [
                "login",
                "signin",
                "signup",
                "cart",
                "checkout",
                "privacy",
                "terms",
                "help",
                "faq",
                "contact",
                "about",
            ]
            if any(u in href_lower or u in link_text for u in utility_words):
                score -= 5.0

            # Store max score for deduplicated URL
            clean_url = absolute_url.split("#")[0]
            if clean_url not in candidate_map or score > candidate_map[clean_url]:
                candidate_map[clean_url] = score

        # Sort by score descending
        sorted_links = sorted(
            [url for url, score in candidate_map.items() if score >= -2.0],
            key=lambda u: candidate_map[u],
            reverse=True,
        )

        return sorted_links[:max_links]
