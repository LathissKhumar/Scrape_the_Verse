import hashlib
import json
from typing import Any

from leadfinder.validation.schemas import DuplicateMetric

PRIMARY_KEY_CANDIDATES = [
    "url",
    "product_url",
    "link",
    "id",
    "sku",
    "email",
    "title",
    "name",
]


class DuplicateValidator:
    """Calculates duplicate rates across records without mutating the dataset."""

    def evaluate_duplicates(
        self,
        records: list[dict[str, Any]],
        key_field: str | None = None,
    ) -> DuplicateMetric:
        """Calculate duplicate metrics across records."""
        total = len(records)
        if total == 0:
            return DuplicateMetric()

        effective_key = key_field
        if not effective_key:
            sample = records[0]
            for candidate in PRIMARY_KEY_CANDIDATES:
                if sample.get(candidate):
                    effective_key = candidate
                    break

        seen_keys: set[str] = set()
        duplicate_count = 0

        for r in records:
            if not isinstance(r, dict):
                continue

            if effective_key and r.get(effective_key):
                dedup_key = f"{effective_key}:{str(r[effective_key]).strip().lower()}"
            else:
                sorted_items = sorted(
                    [(str(k), str(v).strip()) for k, v in r.items() if v is not None]
                )
                serialized = json.dumps(sorted_items, sort_keys=True)
                dedup_key = hashlib.md5(serialized.encode("utf-8")).hexdigest()

            if dedup_key in seen_keys:
                duplicate_count += 1
            else:
                seen_keys.add(dedup_key)

        unique_count = len(seen_keys)
        dup_rate = round(duplicate_count / total, 4) if total > 0 else 0.0

        return DuplicateMetric(
            total_records=total,
            unique_records=unique_count,
            duplicate_records=duplicate_count,
            duplicate_rate=dup_rate,
        )
