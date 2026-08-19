from typing import Any
import lxml.html
from app.extraction.schema import ExtractionSchema, RawPage


class XPathExtractor:
    """Deterministic XPath-based structured extraction using lxml."""

    def extract(
        self,
        content: str | RawPage,
        schema: ExtractionSchema,
    ) -> list[dict[str, Any]]:
        """Extract structured records from HTML content using XPath expressions."""
        html_str = content.html if isinstance(content, RawPage) else str(content)
        if not html_str or not html_str.strip():
            return []

        try:
            tree = lxml.html.fromstring(html_str)
        except Exception:
            return []

        containers = [tree]
        if schema.base_selector:
            try:
                matched = tree.xpath(schema.base_selector)
                if matched and isinstance(matched, list):
                    containers = matched
                else:
                    return []
            except Exception:
                return []

        records: list[dict[str, Any]] = []

        for container in containers:
            record: dict[str, Any] = {}
            has_valid_field = False

            for field_rule in schema.fields:
                field_name = field_rule.name
                val = field_rule.default_value

                if field_rule.selector:
                    try:
                        xpath_expr = field_rule.selector
                        # Ensure relative xpath if not already prefixed
                        if not xpath_expr.startswith(".") and not xpath_expr.startswith("/"):
                            xpath_expr = f".//{xpath_expr}"

                        results = container.xpath(xpath_expr)
                        if results:
                            target = results[0]
                            if isinstance(target, str):
                                val = target.strip()
                                has_valid_field = True
                            elif hasattr(target, "attrib") and field_rule.attribute:
                                attr_val = target.attrib.get(field_rule.attribute)
                                if attr_val:
                                    val = str(attr_val).strip()
                                    has_valid_field = True
                            elif hasattr(target, "text_content"):
                                text_val = target.text_content().strip()
                                if text_val:
                                    val = text_val
                                    has_valid_field = True
                    except Exception:
                        pass

                record[field_name] = val

            if has_valid_field:
                records.append(record)

        return records
