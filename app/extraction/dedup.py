import hashlib
import json
from typing import Any, Optional

PRIMARY_KEY_CANDIDATES = ["url", "product_url", "link", "id", "sku", "email", "title", "name"]


class RecordDeduplicator:
    """Normalizes and deduplicates extracted structured records."""

    def deduplicate(
        self,
        records: list[dict[str, Any]],
        key_field: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Deduplicate records preserving insertion order."""
        if not records:
            return []

        seen_keys: set[str] = set()
        deduped: list[dict[str, Any]] = []

        # Detect primary key field if not provided
        effective_key = key_field
        if not effective_key:
            sample = records[0]
            for candidate in PRIMARY_KEY_CANDIDATES:
                if candidate in sample and sample[candidate]:
                    effective_key = candidate
                    break

        for record in records:
            if not isinstance(record, dict) or not any(record.values()):
                continue

            # Normalize values
            normalized_record: dict[str, Any] = {}
            for k, v in record.items():
                if isinstance(v, str):
                    normalized_record[k] = v.strip()
                else:
                    normalized_record[k] = v

            if effective_key and normalized_record.get(effective_key):
                dedup_key = f"{effective_key}:{str(normalized_record[effective_key]).strip().lower()}"
            else:
                # Composite hash of sorted items
                sorted_items = sorted([
                    (str(k), str(v).strip()) for k, v in normalized_record.items() if v is not None
                ])
                serialized = json.dumps(sorted_items, sort_keys=True)
                dedup_key = hashlib.md5(serialized.encode("utf-8")).hexdigest()

            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                deduped.append(normalized_record)

        return deduped
