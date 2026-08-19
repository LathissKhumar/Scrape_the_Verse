import re
from typing import Any
from app.extraction.schema import ExtractionSchema, RawPage

COMMON_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE),
    "phone": re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    "price": re.compile(r"(?:[\$\€\£\₹]|USD|EUR)\s?\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR)"),
    "url": re.compile(r"https?://[^\s,;\"'<>()\[\]{}]+", re.IGNORECASE),
    "date": re.compile(
        r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    ),
}


class RegexExtractor:
    """Deterministic regular-expression based extraction for pattern fields."""

    def extract(
        self,
        content: str | RawPage,
        schema: ExtractionSchema,
    ) -> list[dict[str, Any]]:
        """Extract matching structured records using pattern matching."""
        text_str = content.get_primary_content() if isinstance(content, RawPage) else str(content)
        if not text_str or not text_str.strip():
            return []

        field_matches: dict[str, list[str]] = {}

        for field_rule in schema.fields:
            pattern = None
            if field_rule.regex_pattern:
                try:
                    pattern = re.compile(field_rule.regex_pattern, re.IGNORECASE)
                except Exception:
                    pass

            if not pattern:
                # Check for standard known field names
                f_lower = field_rule.name.lower()
                for key, std_pat in COMMON_PATTERNS.items():
                    if key in f_lower:
                        pattern = std_pat
                        break

            if pattern:
                matches = pattern.findall(text_str)
                # Deduplicate and clean
                cleaned_matches = []
                for m in matches:
                    val = m[0] if isinstance(m, tuple) else m
                    s = str(val).strip().rstrip(".,;)")
                    if s and s not in cleaned_matches:
                        cleaned_matches.append(s)
                field_matches[field_rule.name] = cleaned_matches
            else:
                field_matches[field_rule.name] = []

        # Find maximum matches length to create list of records
        max_rows = max([len(v) for v in field_matches.values()] or [0])
        if max_rows == 0:
            return []

        records: list[dict[str, Any]] = []
        for i in range(max_rows):
            row: dict[str, Any] = {}
            has_val = False
            for field_rule in schema.fields:
                vals = field_matches.get(field_rule.name, [])
                if i < len(vals):
                    row[field_rule.name] = vals[i]
                    has_val = True
                else:
                    row[field_rule.name] = field_rule.default_value
            if has_val:
                records.append(row)

        return records
