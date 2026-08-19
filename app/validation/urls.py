import re
from typing import Any, Optional
from urllib.parse import urlparse
from app.validation.schemas import UrlMetric

URL_SCHEMES = {"http", "https"}


class URLValidator:
    """Validates structural and syntactic validity of URL fields without network requests."""

    def is_valid_url(self, val: Any) -> bool:
        """Check if value is a syntactically valid HTTP/HTTPS URL."""
        if not isinstance(val, str) or not val.strip():
            return False

        trimmed = val.strip()
        try:
            parsed = urlparse(trimmed)
            if parsed.scheme.lower() not in URL_SCHEMES:
                return False
            if not parsed.netloc or len(parsed.netloc.split(".")) < 2:
                return False
            return True
        except Exception:
            return False

    def evaluate_urls(
        self,
        records: list[dict[str, Any]],
        url_fields: Optional[list[str]] = None,
    ) -> UrlMetric:
        """Evaluate URL validity across all records for identified URL fields."""
        if not records:
            return UrlMetric()

        # If url_fields not provided, detect fields containing 'url', 'link', 'href', 'website'
        effective_fields = url_fields
        if not effective_fields:
            sample = records[0]
            effective_fields = [
                k for k in sample.keys()
                if any(sub in k.lower() for sub in ["url", "link", "href", "website", "domain"])
            ]

        if not effective_fields:
            return UrlMetric(total_urls=0, valid_urls=0, invalid_urls=0, valid_rate=1.0)

        total_urls = 0
        valid_urls = 0
        invalid_urls = 0

        for r in records:
            for f in effective_fields:
                val = r.get(f)
                if val is not None and str(val).strip():
                    total_urls += 1
                    if self.is_valid_url(val):
                        valid_urls += 1
                    else:
                        invalid_urls += 1

        valid_rate = round(valid_urls / total_urls, 4) if total_urls > 0 else 1.0

        return UrlMetric(
            total_urls=total_urls,
            valid_urls=valid_urls,
            invalid_urls=invalid_urls,
            valid_rate=valid_rate,
        )
