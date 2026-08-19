from typing import Any, Optional
from bs4 import BeautifulSoup
from app.extraction.schema import ExtractionSchema, RawPage


class TableExtractor:
    """Deterministic HTML table detection, quality scoring, and structured extraction."""

    def score_table(self, table_tag) -> float:
        """Score table to determine if it is a genuine structured data table versus a layout table."""
        rows = table_tag.find_all("tr", recursive=False) or table_tag.find_all("tr")
        if not rows or len(rows) < 2:
            return 0.0

        headers = table_tag.find_all("th")
        has_explicit_headers = len(headers) > 0

        # Check column counts across rows
        col_counts = [len(r.find_all(["td", "th"])) for r in rows]
        if not col_counts or max(col_counts) == 0:
            return 0.0

        avg_cols = sum(col_counts) / len(col_counts)
        col_variance = sum(abs(c - avg_cols) for c in col_counts) / len(col_counts)

        score = 0.5
        if has_explicit_headers:
            score += 0.3
        if col_variance < 0.5:
            score += 0.2
        if avg_cols >= 2 and len(rows) >= 2:
            score += 0.1

        return min(score, 1.0)

    def extract_tables(
        self,
        content: str | RawPage,
    ) -> list[dict[str, Any]]:
        """Extract all candidate data tables with headers and rows."""
        html_str = content.html if isinstance(content, RawPage) else str(content)
        if not html_str or not html_str.strip():
            return []

        soup = BeautifulSoup(html_str, "html.parser")
        tables = soup.find_all("table")
        parsed_tables: list[dict[str, Any]] = []

        for idx, tbl in enumerate(tables):
            quality = self.score_table(tbl)
            if quality < 0.4:
                continue

            rows = tbl.find_all("tr")
            if not rows:
                continue

            headers: list[str] = []
            header_elems = rows[0].find_all(["th", "td"])
            if tbl.find("th") or len(header_elems) > 0:
                headers = [h.get_text(strip=True) for h in header_elems]
                data_rows = rows[1:]
            else:
                data_rows = rows

            extracted_rows: list[list[str]] = []
            for r in data_rows:
                cells = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
                if any(cells):
                    extracted_rows.append(cells)

            if extracted_rows:
                parsed_tables.append({
                    "table_index": idx,
                    "score": quality,
                    "headers": headers,
                    "rows": extracted_rows,
                    "metadata": {
                        "row_count": len(extracted_rows),
                        "column_count": len(headers) if headers else (len(extracted_rows[0]) if extracted_rows else 0),
                    },
                })

        return parsed_tables

    def extract(
        self,
        content: str | RawPage,
        schema: Optional[ExtractionSchema] = None,
    ) -> list[dict[str, Any]]:
        """Extract structured records from data tables mapped to requested schema fields."""
        tables = self.extract_tables(content)
        if not tables:
            return []

        # Sort tables by quality score descending
        tables.sort(key=lambda t: t["score"], reverse=True)
        best_table = tables[0]
        headers = best_table.get("headers", [])
        rows = best_table.get("rows", [])

        records: list[dict[str, Any]] = []

        target_field_names = [f.name for f in schema.fields] if schema and schema.fields else None

        for row in rows:
            record: dict[str, Any] = {}
            for col_idx, cell_value in enumerate(row):
                if headers and col_idx < len(headers) and headers[col_idx]:
                    key = headers[col_idx]
                else:
                    key = f"col_{col_idx + 1}"

                # Match key to target fields if schema provided
                if target_field_names:
                    matched_field = None
                    for tf in target_field_names:
                        if tf.lower() in key.lower() or key.lower() in tf.lower():
                            matched_field = tf
                            break
                    if matched_field:
                        record[matched_field] = cell_value
                    else:
                        record[key] = cell_value
                else:
                    record[key] = cell_value

            if record:
                records.append(record)

        return records
