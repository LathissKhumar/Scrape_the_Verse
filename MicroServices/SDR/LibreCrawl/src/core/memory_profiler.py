"""Per-user memory tracking with incremental accounting.

Instead of recursing every object on every call, we measure each item once
when it enters the crawler and keep a running total. The totals are per
crawler instance (i.e. per user session).
"""
import sys
import gc
import json
import threading
from collections import defaultdict


def _shallow_dict_size(d):
    """Fast approximate size of a dict and its immediate string/number values.

    Walks one level deep into the dict — enough for the flat URL-result and
    link dicts the crawler produces. Lists/dicts nested inside are measured
    by their container overhead + shallow element sizes, not full recursion.
    """
    size = sys.getsizeof(d)
    for k, v in d.items():
        size += sys.getsizeof(k)
        if isinstance(v, str):
            size += sys.getsizeof(v)
        elif isinstance(v, (int, float, bool)):
            size += sys.getsizeof(v)
        elif isinstance(v, dict):
            size += sys.getsizeof(v)
            for k2, v2 in v.items():
                size += sys.getsizeof(k2) + sys.getsizeof(v2)
        elif isinstance(v, (list, tuple)):
            size += sys.getsizeof(v)
            for item in v:
                size += sys.getsizeof(item)
        else:
            size += sys.getsizeof(v)
    return size


class UserMemoryTracker:
    """Lightweight per-user memory accumulator.

    Call ``track_url``, ``track_link``, ``track_issue`` as items are produced.
    Read ``total_bytes`` at any time — O(1), no recursion.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.url_bytes = 0
        self.link_bytes = 0
        self.issue_bytes = 0
        self.url_count = 0
        self.link_count = 0
        self.issue_count = 0

    # ------------------------------------------------------------------
    # Tracking (called from crawler hot path)
    # ------------------------------------------------------------------

    def track_url(self, result_dict):
        """Measure a single crawl-result dict and add to running total."""
        size = _shallow_dict_size(result_dict)
        with self._lock:
            self.url_bytes += size
            self.url_count += 1

    def track_links(self, links_list):
        """Measure a batch of link dicts."""
        total = 0
        count = 0
        for link in links_list:
            total += _shallow_dict_size(link)
            count += 1
        with self._lock:
            self.link_bytes += total
            self.link_count += count

    def track_issues(self, issues_list):
        """Measure a batch of issue dicts."""
        total = 0
        count = 0
        for issue in issues_list:
            total += _shallow_dict_size(issue)
            count += 1
        with self._lock:
            self.issue_bytes += total
            self.issue_count += count

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    @property
    def total_bytes(self):
        with self._lock:
            return self.url_bytes + self.link_bytes + self.issue_bytes

    @property
    def total_mb(self):
        return self.total_bytes / (1024 * 1024)

    def get_stats(self):
        """Return a dict matching the old ``get_crawler_data_size`` shape."""
        with self._lock:
            url_b = self.url_bytes
            link_b = self.link_bytes
            issue_b = self.issue_bytes
            url_c = self.url_count
            link_c = self.link_count
            issue_c = self.issue_count

        total_b = url_b + link_b + issue_b
        return {
            'crawl_results_deep_mb': round(url_b / 1024 / 1024, 2),
            'crawl_results_json_mb': 0,  # no longer computed — too expensive
            'crawl_results_count': url_c,
            'avg_per_url_kb': round(url_b / url_c / 1024, 2) if url_c else 0,

            'links_deep_mb': round(link_b / 1024 / 1024, 2),
            'links_json_mb': 0,
            'links_count': link_c,

            'issues_deep_mb': round(issue_b / 1024 / 1024, 2),
            'issues_json_mb': 0,
            'issues_count': issue_c,

            'total_deep_mb': round(total_b / 1024 / 1024, 2),
            'total_json_mb': 0,
        }

    def reset(self):
        with self._lock:
            self.url_bytes = 0
            self.link_bytes = 0
            self.issue_bytes = 0
            self.url_count = 0
            self.link_count = 0
            self.issue_count = 0


class MemoryProfiler:
    """Kept for the debug endpoint that lists object-type breakdowns."""

    @staticmethod
    def get_object_memory_breakdown():
        """Get memory usage breakdown by object type"""
        gc.collect()

        type_count = defaultdict(int)
        type_size = defaultdict(int)

        all_objects = gc.get_objects()
        for obj in all_objects:
            obj_type = type(obj).__name__
            type_count[obj_type] += 1
            try:
                type_size[obj_type] += sys.getsizeof(obj)
            except:
                pass

        sorted_types = sorted(type_size.items(), key=lambda x: x[1], reverse=True)

        breakdown = []
        for obj_type, size_bytes in sorted_types[:20]:
            breakdown.append({
                'type': obj_type,
                'count': type_count[obj_type],
                'size_mb': round(size_bytes / 1024 / 1024, 2),
                'avg_size_kb': round(size_bytes / type_count[obj_type] / 1024, 2)
            })

        return breakdown

    @staticmethod
    def get_crawler_data_size(crawl_results, links, issues):
        """Backward-compat wrapper — uses shallow measurement, no recursion."""
        url_b = sum(_shallow_dict_size(r) for r in crawl_results)
        link_b = sum(_shallow_dict_size(l) for l in links)
        issue_b = sum(_shallow_dict_size(i) for i in issues)
        total_b = url_b + link_b + issue_b

        return {
            'crawl_results_deep_mb': round(url_b / 1024 / 1024, 2),
            'crawl_results_json_mb': 0,
            'crawl_results_count': len(crawl_results),
            'avg_per_url_kb': round(url_b / len(crawl_results) / 1024, 2) if crawl_results else 0,

            'links_deep_mb': round(link_b / 1024 / 1024, 2),
            'links_json_mb': 0,
            'links_count': len(links),

            'issues_deep_mb': round(issue_b / 1024 / 1024, 2),
            'issues_json_mb': 0,
            'issues_count': len(issues),

            'total_deep_mb': round(total_b / 1024 / 1024, 2),
            'total_json_mb': 0,
        }
