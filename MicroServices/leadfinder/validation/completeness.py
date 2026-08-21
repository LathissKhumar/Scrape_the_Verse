from typing import Any
from leadfinder.validation.schemas import FieldMetric

SUSPICIOUS_PLACEHOLDERS = {
    "n/a", "na", "n.a.", "unknown", "-", "--", "---",
    "not available", "not applicable", "null", "none",
    "[none]", "undefined", "tbd", "pending", "empty",
}


class CompletenessValidator:
    """Calculates field-level coverage, null counts, and detects suspicious placeholder values."""

    def is_placeholder(self, val: Any) -> bool:
        """Check if value is a known uninformative placeholder string."""
        if val is None:
            return False
        if isinstance(val, str):
            s = val.strip().lower()
            return s in SUSPICIOUS_PLACEHOLDERS
        return False

    def is_empty(self, val: Any) -> bool:
        """Check if value is null, whitespace, or empty collection."""
        if val is None:
            return True
        if isinstance(val, str):
            return len(val.strip()) == 0
        if isinstance(val, (list, dict, set, tuple)):
            return len(val) == 0
        return False

    def evaluate_field(self, records: list[dict[str, Any]], field_name: str) -> FieldMetric:
        """Calculate completeness and placeholder metrics for a single field across all records."""
        total = len(records)
        if total == 0:
            return FieldMetric(coverage=0.0)

        valid_count = 0
        empty_count = 0
        placeholder_count = 0

        for r in records:
            val = r.get(field_name)
            if self.is_empty(val):
                empty_count += 1
            elif self.is_placeholder(val):
                placeholder_count += 1
            else:
                valid_count += 1

        coverage = round(valid_count / total, 4)

        return FieldMetric(
            coverage=coverage,
            valid_count=valid_count,
            empty_count=empty_count,
            invalid_type_count=0,
            placeholder_count=placeholder_count,
        )

    def evaluate_all(
        self,
        records: list[dict[str, Any]],
        fields: list[str],
    ) -> dict[str, FieldMetric]:
        """Evaluate completeness metrics across all requested fields."""
        metrics: dict[str, FieldMetric] = {}
        for f in fields:
            metrics[f] = self.evaluate_field(records, f)
        return metrics
