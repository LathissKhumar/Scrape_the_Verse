import csv
import io
import json
from typing import Any


class DataExporter:
    """Exports structured scraping records to standard interchange formats (CSV, JSON, NDJSON)."""

    @staticmethod
    def to_csv(records: list[dict[str, Any]]) -> str:
        """Serialize a list of record dicts to CSV string."""
        if not records:
            return ""

        output = io.StringIO()
        # Collect all unique fieldnames across records
        fieldnames: list[str] = []
        for r in records:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

        return output.getvalue().strip()

    @staticmethod
    def to_json(records: list[dict[str, Any]], indent: int = 2) -> str:
        """Serialize a list of record dicts to formatted JSON string."""
        return json.dumps(records, indent=indent, default=str)

    @staticmethod
    def to_ndjson(records: list[dict[str, Any]]) -> str:
        """Serialize a list of record dicts to Newline Delimited JSON string."""
        if not records:
            return ""
        return "\n".join(json.dumps(r, default=str) for r in records)
