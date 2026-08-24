"""Deterministic CSS selector-based structured extraction."""

from typing import Any

from bs4 import BeautifulSoup

from leadfinder.extraction.schema import ExtractionSchema, RawPage


class CSSExtractor:
    """Deterministic CSS selector-based structured extraction."""

    def extract(
        self,
        content: str | RawPage,
        schema: ExtractionSchema,
    ) -> list[dict[str, Any]]:
        """Extract structured records from HTML content using CSS selectors defined in schema."""
        html_str = content.html if isinstance(content, RawPage) else str(content)
        if not html_str or not html_str.strip():
            return []

        soup = BeautifulSoup(html_str, "html.parser")
        containers = [soup]

        if schema.base_selector:
            matched = soup.select(schema.base_selector)
            if matched:
                containers = matched
            else:
                # Stale or drifted base selector: discover repeating card containers from field selectors
                discovered_containers: list[Any] = []
                for field_rule in schema.fields:
                    if field_rule.selector:
                        for elem in soup.select(field_rule.selector):
                            parent = elem.find_parent(
                                ["article", "li", "tr", "section", "div"]
                            )
                            if parent and parent not in discovered_containers:
                                discovered_containers.append(parent)
                containers = discovered_containers if discovered_containers else [soup]

        records: list[dict[str, Any]] = []

        for container in containers:
            record: dict[str, Any] = {}
            has_valid_field = False

            for field_rule in schema.fields:
                field_name = field_rule.name
                val = field_rule.default_value

                if field_rule.selector:
                    elem = container.select_one(field_rule.selector)
                    if elem:
                        if field_rule.attribute:
                            attr_val = elem.get(field_rule.attribute)
                            if attr_val is not None:
                                val = str(attr_val).strip()
                                has_valid_field = True
                        else:
                            text_val = elem.get_text(separator=" ", strip=True)
                            if text_val:
                                val = text_val
                                has_valid_field = True
                record[field_name] = val

            if has_valid_field:
                records.append(record)

        return records
