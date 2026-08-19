"""DOM structural fingerprinting and change detection for early website layout drift identification."""

import hashlib
from collections import Counter
from typing import Any
from bs4 import BeautifulSoup
from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger("DOM_FINGERPRINTER")


class DOMFingerprinter:
    """Computes compact structural fingerprints of DOM trees to quantify structural drift over time."""

    def __init__(self):
        self.settings = get_settings()

    def generate_fingerprint(self, html: str) -> dict[str, Any]:
        """Compute a compact, deterministic fingerprint of an HTML document."""
        if not html:
            return {"tag_counts": {}, "depth": 0, "hash": "empty"}

        soup = BeautifulSoup(html[:25000], "html.parser")
        tags = [tag.name for tag in soup.find_all(True) if tag.name not in ("script", "style", "meta", "link")]
        counts = Counter(tags)

        # Compute max DOM depth
        def get_depth(elem, cur_depth=0):
            if not hasattr(elem, "children"):
                return cur_depth
            children = [c for c in elem.children if hasattr(c, "children")]
            if not children:
                return cur_depth
            return max(get_depth(c, cur_depth + 1) for c in children)

        max_depth = get_depth(soup)
        structural_str = f"{sorted(counts.items())}:{max_depth}"
        fp_hash = hashlib.sha256(structural_str.encode("utf-8")).hexdigest()[:16]

        return {
            "tag_counts": dict(counts),
            "depth": max_depth,
            "total_tags": len(tags),
            "hash": fp_hash,
        }

    def compute_drift_score(self, fp1: dict[str, Any], fp2: dict[str, Any]) -> float:
        """Compute normalized structural drift between two DOM fingerprints [0.0 = identical, 1.0 = completely different]."""
        if not fp1 or not fp2 or fp1.get("hash") == "empty" or fp2.get("hash") == "empty":
            return 1.0

        if fp1.get("hash") == fp2.get("hash"):
            return 0.0

        tc1 = fp1.get("tag_counts", {})
        tc2 = fp2.get("tag_counts", {})

        all_tags = set(tc1.keys()).union(set(tc2.keys()))
        if not all_tags:
            return 0.0

        diff_sum = 0
        total_sum = 0
        for tag in all_tags:
            c1 = tc1.get(tag, 0)
            c2 = tc2.get(tag, 0)
            diff_sum += abs(c1 - c2)
            total_sum += max(c1, c2)

        tag_drift = diff_sum / max(1, total_sum)
        depth_drift = abs(fp1.get("depth", 0) - fp2.get("depth", 0)) / max(1, max(fp1.get("depth", 1), fp2.get("depth", 1)))

        drift = round((0.75 * tag_drift) + (0.25 * depth_drift), 3)
        return min(1.0, max(0.0, drift))

    def is_significant_drift(self, fp1: dict[str, Any], fp2: dict[str, Any]) -> bool:
        """Check if structural drift exceeds the configured threshold."""
        score = self.compute_drift_score(fp1, fp2)
        thresh = getattr(self.settings, "STRUCTURAL_DRIFT_THRESHOLD", 0.35)
        is_drift = score > thresh
        if is_drift:
            logger.warning(f"Significant structural DOM drift detected: {score:.3f} > {thresh:.3f}")
        return is_drift
