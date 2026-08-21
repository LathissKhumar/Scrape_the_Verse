"""Cross-domain semantic and structural repair memory matcher."""

from collections import Counter
import math
from typing import Any
from bs4 import BeautifulSoup
from leadfinder.config.logging import get_logger
from leadfinder.healing.schemas import RepairMemoryRecord

logger = get_logger("SEMANTIC_REPAIR_MEMORY")

_IGNORED_DOM_TAGS = {"script", "style", "meta", "link", "svg", "path"}
_REPEATING_CONTAINER_KEYWORDS = ["card", "item", "product", "row", "post"]


class SemanticRepairMemory:
    """Finds structurally and semantically similar successful repairs across different domains."""

    def __init__(self) -> None:
        self._structural_records: list[dict[str, Any]] = []

    def extract_structural_skeleton(self, html: str) -> dict[str, float]:
        """Convert HTML DOM into a normalized structural bag-of-tags and container patterns."""
        if not html:
            return {}

        soup = BeautifulSoup(html[:15000], "html.parser")
        # Collect tag distribution and nesting signatures
        tags = [
            tag.name for tag in soup.find_all(True)
            if tag.name not in _IGNORED_DOM_TAGS
        ]
        counts = Counter(tags)
        total = max(1, sum(counts.values()))

        vector = {k: v / total for k, v in counts.items()}

        # Add repeated container indicators
        has_cards = len(soup.find_all(class_=lambda c: c and any(k in str(c).lower() for k in _REPEATING_CONTAINER_KEYWORDS))) > 2
        has_table = len(soup.find_all("table")) > 0

        vector["__has_cards__"] = 1.0 if has_cards else 0.0
        vector["__has_table__"] = 1.0 if has_table else 0.0

        return vector

    def compute_similarity(self, vec1: dict[str, float], vec2: dict[str, float]) -> float:
        """Compute cosine similarity between two structural vectors."""
        all_keys = set(vec1.keys()).union(set(vec2.keys()))
        if not all_keys:
            return 0.0

        dot_product = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in all_keys)
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def register_record(self, record: RepairMemoryRecord, html: str) -> None:
        """Register a verified repair with its structural DOM skeleton."""
        skeleton = self.extract_structural_skeleton(html)
        self._structural_records.append({
            "record": record,
            "skeleton": skeleton,
        })
        logger.debug(f"Registered semantic structural repair memory for {record.domain}")

    def find_cross_domain_candidates(
        self,
        html: str,
        fields: list[str],
        similarity_threshold: float = 0.75,
    ) -> list[RepairMemoryRecord]:
        """Find past successful repairs from other domains with similar DOM structures."""
        current_skeleton = self.extract_structural_skeleton(html)
        matches: list[tuple[float, RepairMemoryRecord]] = []

        for item in self._structural_records:
            sim = self.compute_similarity(current_skeleton, item["skeleton"])
            if sim >= similarity_threshold:
                rec: RepairMemoryRecord = item["record"]
                matches.append((sim, rec))

        # Sort descending by similarity
        matches.sort(key=lambda x: x[0], reverse=True)
        results = [m[1] for m in matches[:3]]
        if results:
            logger.debug(f"Discovered {len(results)} cross-domain semantic candidate priors (top similarity={matches[0][0]:.2f})")
        return results

