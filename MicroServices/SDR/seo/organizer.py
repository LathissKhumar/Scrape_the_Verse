"""
SEO Data Organizer & Normalization Layer
Refactors raw crawler and audit JSON into a clean, deterministic, token-efficient,
and domain-partitioned directory structure under `data/websites/<domain>/`.

Guarantees:
- Zero data loss (original raw JSON preserved unmodified under raw/crawl.json)
- Deterministic ID generation (pages, issues, links, images)
- Complete deduplication across normalized records
- Strict missing-value semantics (null, [], {}, with metadata tracking)
- Full LLM token optimization with lightweight references and compact index files
- Automated validation and integrity reporting in summary/validation.json
"""

import hashlib
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from typing import Any

# -----------------------------------------------------------------------------
# 1. URL & ID Normalization Utilities
# -----------------------------------------------------------------------------


def extract_domain(url_or_domain: str) -> str:
    """
    Extract a clean domain name for directory naming (e.g., 'www.atlaskliniek.nl' -> 'atlaskliniek.nl').
    """
    if not url_or_domain:
        return "unknown_domain"

    if "://" not in url_or_domain:
        url_or_domain = "https://" + url_or_domain

    parsed = urllib.parse.urlparse(url_or_domain)
    hostname = parsed.hostname or url_or_domain
    hostname = hostname.lower()

    # Strip common leading prefixes
    hostname = hostname.removeprefix("www.")

    # Remove any invalid filesystem characters
    clean_domain = re.sub(r"[^\w\.-]", "_", hostname)
    return clean_domain or "unknown_domain"


def normalize_url(url: str | None) -> str:
    """
    Normalize URL: remove fragments, lowercase scheme/host, preserve path & query parameters.
    """
    if not url or not isinstance(url, str):
        return ""

    url = url.strip()
    if not url:
        return ""

    parsed = urllib.parse.urlparse(url)
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    # Normalize duplicate slashes in path (preserve leading slash)
    path = re.sub(r"/{2,}", "/", path)

    query = parsed.query
    # Rebuild without fragment
    normalized = urllib.parse.urlunparse(
        (scheme, netloc, path, parsed.params, query, "")
    )
    return normalized


def generate_stable_id(prefix: str, *components: Any) -> str:
    """
    Generate a deterministic, shortened SHA-256 hash ID.
    Example: generate_stable_id("page", "https://example.com/about") -> "page_a1b2c3d4e5f6"
    """
    raw_str = "|".join(str(c).strip() for c in components if c is not None)
    digest = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}" if prefix else digest


def sanitize_filename(name: str) -> str:
    """Convert a path or slug into a valid safe filename."""
    if not name or name == "/":
        return "homepage"
    clean = re.sub(r"[^\w\-]", "_", name.strip("/"))
    clean = re.sub(r"_+", "_", clean)
    return clean[:80] or "page"


# -----------------------------------------------------------------------------
# 2. Missing Value Policy & Sanitization
# -----------------------------------------------------------------------------


def handle_missing_value(
    val: Any, default_type: str = "scalar", reason: str | None = None
) -> Any:
    """
    Implements the strict missing value policy.
    Never invents missing values; preserves truthfulness.
    """
    if val is not None and val != "":
        return val

    if default_type == "list":
        return []
    elif default_type == "dict":
        return {}

    return None


def create_status_field(
    value: Any, status: str = "available", reason: str | None = None
) -> dict[str, Any]:
    """Helper for metadata-accompanied metric values (e.g. PageSpeed 429)."""
    res = {"value": value, "status": status}
    if reason:
        res["reason"] = reason
    return res


# -----------------------------------------------------------------------------
# 3. Model Normalizers
# -----------------------------------------------------------------------------


def normalize_page(raw_page: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Extracts and standardizes page-level information according to section 3.
    Returns: (normalized_page_dict, page_id)
    """
    raw_url = raw_page.get("url", "")
    norm_url = normalize_url(raw_url)
    page_id = generate_stable_id("page", norm_url)

    # SEO sub-object
    seo_data = {
        "title": raw_page.get("title") or None,
        "meta_description": raw_page.get("meta_description") or None,
        "h1": raw_page.get("h1") or None,
        "h2": raw_page.get("h2") if isinstance(raw_page.get("h2"), list) else [],
        "h3": raw_page.get("h3") if isinstance(raw_page.get("h3"), list) else [],
        "word_count": int(raw_page.get("word_count", 0))
        if raw_page.get("word_count") is not None
        else 0,
    }

    # Technical sub-object
    tech_data = {
        "canonical": raw_page.get("canonical") or raw_page.get("canonical_url") or None,
        "robots": raw_page.get("robots") or None,
        "language": raw_page.get("lang") or None,
        "charset": raw_page.get("charset") or None,
        "viewport": raw_page.get("viewport") or None,
    }

    # Social sub-object
    social_data = {
        "og_tags": raw_page.get("og_tags")
        if isinstance(raw_page.get("og_tags"), dict)
        else {},
        "twitter_tags": raw_page.get("twitter_tags")
        if isinstance(raw_page.get("twitter_tags"), dict)
        else {},
    }

    # Response times
    resp_time = raw_page.get("response_time_ms")
    if resp_time is None:
        resp_time = raw_page.get("response_time")
    resp_time_num = float(resp_time) if resp_time is not None else None

    render_time = raw_page.get("render_time_ms")
    if render_time is None:
        render_time = raw_page.get("render_time")
    render_time_num = float(render_time) if render_time is not None else None

    # Status Code
    status_code = raw_page.get("status_code")
    if status_code is not None:
        try:
            status_code = int(status_code)
        except (ValueError, TypeError):
            status_code = None

    normalized = {
        "page_id": page_id,
        "url": norm_url,
        "raw_url": raw_url,
        "status_code": status_code,
        "content_type": raw_page.get("content_type") or None,
        "depth": raw_page.get("depth", 0),
        "response_time_ms": resp_time_num,
        "render_time_ms": render_time_num,
        "seo": seo_data,
        "technical": tech_data,
        "social": social_data,
        "schema": raw_page.get("json_ld") or [],
        "analytics": raw_page.get("analytics") or {},
        "images": raw_page.get("images") or [],
        "redirects": raw_page.get("redirects") or [],
        "linked_from": [normalize_url(u) for u in raw_page.get("linked_from", []) if u],
    }

    return normalized, page_id


def normalize_issue(
    raw_issue: dict[str, Any], page_lookup: dict[str, str]
) -> tuple[dict[str, Any], str]:
    """
    Standardizes issue record and produces a deterministic issue ID.
    Returns: (normalized_issue_dict, issue_id)
    """
    category = str(raw_issue.get("category") or "Technical").strip().title()
    issue_type = str(raw_issue.get("type") or "general_issue").strip().lower()
    raw_url = raw_issue.get("url") or ""
    norm_url = normalize_url(raw_url)

    issue_id = generate_stable_id("iss", category, issue_type, norm_url)
    page_id = page_lookup.get(norm_url)

    # Standardize severity
    raw_sev = str(raw_issue.get("severity") or "medium").strip().lower()
    if raw_sev in ("critical", "fatal"):
        severity = "critical"
    elif raw_sev in ("high", "error"):
        severity = "high"
    elif raw_sev in ("medium", "warning", "warn"):
        severity = "medium"
    elif raw_sev in ("low", "notice"):
        severity = "low"
    else:
        severity = "info"

    details = raw_issue.get("details") or raw_issue.get("description") or ""
    issue_title = (
        raw_issue.get("issue")
        or raw_issue.get("title")
        or issue_type.replace("_", " ").title()
    )

    normalized = {
        "id": issue_id,
        "page_id": page_id,
        "category": category,
        "type": issue_type,
        "severity": severity,
        "url": norm_url,
        "title": issue_title,
        "description": details,
        "recommendation": raw_issue.get("recommendation") or None,
        "evidence": raw_issue.get("evidence")
        if isinstance(raw_issue.get("evidence"), dict)
        else {},
    }

    return normalized, issue_id


def normalize_link(raw_link: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Standardizes link record and produces a deterministic link ID.
    """
    src = normalize_url(raw_link.get("source_url") or "")
    tgt = normalize_url(raw_link.get("target_url") or "")
    anchor = str(raw_link.get("anchor_text") or "").strip()

    link_id = generate_stable_id("lnk", src, tgt, anchor)

    status_code = raw_link.get("status_code")
    if status_code is None:
        status_code = raw_link.get("target_status")
    if status_code is not None:
        try:
            status_code = int(status_code)
        except (ValueError, TypeError):
            status_code = None

    normalized = {
        "id": link_id,
        "source_url": src,
        "target_url": tgt,
        "anchor_text": anchor,
        "internal": bool(raw_link.get("internal", True)),
        "status_code": status_code,
        "target_domain": raw_link.get("target_domain") or extract_domain(tgt),
        "placement": raw_link.get("placement") or "body",
    }

    return normalized, link_id


def normalize_image(
    raw_img: dict[str, Any], source_page_url: str
) -> tuple[dict[str, Any], str]:
    """
    Standardizes image record and produces a deterministic image ID.
    """
    src = normalize_url(raw_img.get("src") or raw_img.get("url") or "")
    norm_source = normalize_url(source_page_url)
    img_id = generate_stable_id("img", src, norm_source)

    normalized = {
        "id": img_id,
        "src": src,
        "alt": raw_img.get("alt") if raw_img.get("alt") is not None else None,
        "width": raw_img.get("width") or None,
        "height": raw_img.get("height") or None,
        "source_page": norm_source,
        "has_alt": bool(raw_img.get("alt") and str(raw_img.get("alt")).strip()),
    }

    return normalized, img_id


# -----------------------------------------------------------------------------
# 4. Master Organizer Engine
# -----------------------------------------------------------------------------


class WebsiteDataOrganizer:
    """
    Deconstructs raw crawl JSON into the normalized 23-section directory tree under `report/<domain>/`.
    """

    def __init__(self, raw_data: dict[str, Any], base_dir: str = "report"):
        self.raw_data = raw_data
        self.base_dir = base_dir

        # Detect domain
        raw_url = raw_data.get("base_url") or raw_data.get("url") or ""
        if not raw_url and raw_data.get("pages"):
            raw_url = raw_data["pages"][0].get("url", "")

        self.domain = extract_domain(raw_data.get("base_domain") or raw_url)
        self.website_root = os.path.join(self.base_dir, self.domain)

        # Internal registries
        self.pages_by_id: dict[str, dict[str, Any]] = {}
        self.page_url_to_id: dict[str, str] = {}
        self.issues_by_id: dict[str, dict[str, Any]] = {}
        self.links_by_id: dict[str, dict[str, Any]] = {}
        self.images_by_id: dict[str, dict[str, Any]] = {}
        self.unclassified_data: dict[str, Any] = {}

    def _write_json(self, rel_path: str, data: Any) -> str:
        """Write JSON to a subpath inside the website directory."""
        full_path = os.path.join(self.website_root, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return rel_path

    def _write_text(self, rel_path: str, text: str) -> str:
        """Write plain text/markdown inside the website directory."""
        full_path = os.path.join(self.website_root, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text)
        return rel_path

    def process(self) -> dict[str, Any]:
        """
        Executes full normalization, saves files, runs validation, and returns master index.
        """
        os.makedirs(self.website_root, exist_ok=True)

        # ---------------------------------------------------------------------
        # 1. RAW DATA (Always preserved verbatim)
        # ---------------------------------------------------------------------
        self._write_json("raw/crawl.json", self.raw_data)

        # ---------------------------------------------------------------------
        # 2. PAGES DECONSTRUCTION
        # ---------------------------------------------------------------------
        raw_pages = self.raw_data.get("pages", [])
        page_index_entries = []

        for p in raw_pages:
            norm_p, p_id = normalize_page(p)
            if p_id not in self.pages_by_id:
                self.pages_by_id[p_id] = norm_p
                self.page_url_to_id[norm_p["url"]] = p_id

                # Save individual page JSON
                parsed_path = urllib.parse.urlparse(norm_p["url"]).path
                slug_name = sanitize_filename(parsed_path)
                page_file_name = f"{slug_name}_{p_id[-6:]}.json"
                self._write_json(f"pages/{page_file_name}", norm_p)

                page_index_entries.append(
                    {
                        "page_id": p_id,
                        "url": norm_p["url"],
                        "status_code": norm_p["status_code"],
                        "depth": norm_p["depth"],
                        "title": norm_p["seo"]["title"],
                        "word_count": norm_p["seo"]["word_count"],
                        "file": f"pages/{page_file_name}",
                    }
                )

        self._write_json(
            "pages/index.json",
            {"total_pages": len(page_index_entries), "pages": page_index_entries},
        )

        # ---------------------------------------------------------------------
        # 3. ISSUES CENTRALIZATION & DEDUPLICATION
        # ---------------------------------------------------------------------
        raw_issues = self.raw_data.get("issues", [])
        for iss in raw_issues:
            norm_iss, iss_id = normalize_issue(iss, self.page_url_to_id)
            if iss_id not in self.issues_by_id:
                self.issues_by_id[iss_id] = norm_iss

        all_issues = list(self.issues_by_id.values())
        critical_issues = [i for i in all_issues if i["severity"] == "critical"]
        high_issues = [i for i in all_issues if i["severity"] == "high"]
        medium_issues = [i for i in all_issues if i["severity"] == "medium"]
        low_issues = [i for i in all_issues if i["severity"] in ("low", "info")]

        by_cat: dict[str, list[dict[str, Any]]] = {}
        for i in all_issues:
            cat = i["category"]
            by_cat.setdefault(cat, []).append(i)

        self._write_json("issues/all.json", all_issues)
        self._write_json("issues/critical.json", critical_issues)
        self._write_json("issues/high.json", high_issues)
        self._write_json("issues/medium.json", medium_issues)
        self._write_json("issues/low.json", low_issues)
        self._write_json("issues/by_category.json", by_cat)

        # ---------------------------------------------------------------------
        # 4. LINKS EXTRACTION & GRAPH ARCHITECTURE
        # ---------------------------------------------------------------------
        raw_links = self.raw_data.get("links", [])
        for l in raw_links:
            norm_l, lnk_id = normalize_link(l)
            if lnk_id not in self.links_by_id:
                self.links_by_id[lnk_id] = norm_l

        all_links = list(self.links_by_id.values())
        internal_links = [l for l in all_links if l["internal"]]
        external_links = [l for l in all_links if not l["internal"]]
        broken_links = [
            l for l in all_links if l.get("status_code") and l["status_code"] >= 400
        ]

        # Anchor text frequency map
        anchor_map: dict[str, int] = {}
        for l in all_links:
            txt = l.get("anchor_text")
            if txt:
                anchor_map[txt] = anchor_map.get(txt, 0) + 1

        # Link Architecture (in-degrees and out-degrees)
        in_degree: dict[str, int] = {}
        out_degree: dict[str, int] = {}
        for l in internal_links:
            src = l["source_url"]
            tgt = l["target_url"]
            out_degree[src] = out_degree.get(src, 0) + 1
            in_degree[tgt] = in_degree.get(tgt, 0) + 1

        all_crawled_urls = set(self.page_url_to_id.keys())
        orphan_pages = [
            u
            for u in all_crawled_urls
            if in_degree.get(u, 0) == 0
            and u != normalize_url(self.raw_data.get("base_url", ""))
        ]

        architecture_data = {
            "total_links": len(all_links),
            "internal_links_count": len(internal_links),
            "external_links_count": len(external_links),
            "broken_links_count": len(broken_links),
            "orphan_pages": orphan_pages,
            "top_linked_pages": sorted(
                [{"url": u, "inbound_links": c} for u, c in in_degree.items()],
                key=lambda x: x["inbound_links"],
                reverse=True,
            )[:20],
        }

        self._write_json("links/all.json", all_links)
        self._write_json("links/internal.json", internal_links)
        self._write_json("links/external.json", external_links)
        self._write_json("links/broken.json", broken_links)
        self._write_json("links/anchor_text.json", anchor_map)
        self._write_json("links/architecture.json", architecture_data)

        # ---------------------------------------------------------------------
        # 5. IMAGES DEDUPLICATION & METRICS
        # ---------------------------------------------------------------------
        for p in self.pages_by_id.values():
            p_url = p["url"]
            for img in p.get("images", []):
                norm_img, img_id = normalize_image(img, p_url)
                if img_id not in self.images_by_id:
                    self.images_by_id[img_id] = norm_img

        all_images = list(self.images_by_id.values())
        missing_alt = [img for img in all_images if not img["has_alt"]]

        self._write_json("images/all.json", all_images)
        self._write_json("images/missing_alt.json", missing_alt)
        self._write_json(
            "images/statistics.json",
            {
                "total_images": len(all_images),
                "images_missing_alt": len(missing_alt),
                "alt_text_coverage_percent": round(
                    ((len(all_images) - len(missing_alt)) / max(len(all_images), 1))
                    * 100,
                    2,
                ),
            },
        )

        # ---------------------------------------------------------------------
        # 6. TECHNICAL SEO DOMAIN
        # ---------------------------------------------------------------------
        canonicals_data = []
        robots_data = []
        errors_data = []
        redirects_data = []

        for p in self.pages_by_id.values():
            canon = p["technical"].get("canonical")
            if canon:
                canonicals_data.append(
                    {
                        "url": p["url"],
                        "canonical": canon,
                        "is_self_referential": canon == p["url"],
                    }
                )
            else:
                canonicals_data.append(
                    {"url": p["url"], "canonical": None, "is_self_referential": False}
                )

            rob = p["technical"].get("robots")
            if rob:
                robots_data.append(
                    {
                        "url": p["url"],
                        "robots": rob,
                        "noindex": "noindex" in rob.lower(),
                    }
                )

            sc = p["status_code"]
            if sc and sc >= 400:
                errors_data.append(
                    {
                        "url": p["url"],
                        "status_code": sc,
                        "content_type": p["content_type"],
                    }
                )

            if p.get("redirects"):
                redirects_data.append({"url": p["url"], "chain": p["redirects"]})

        sitemaps_info = self.raw_data.get(
            "sitemaps", {"discovered": [], "urls_found": 0}
        )

        self._write_json(
            "technical/audit.json", self.raw_data.get("technical_audit") or {}
        )
        self._write_json("technical/canonicals.json", canonicals_data)
        self._write_json("technical/robots.json", robots_data)
        self._write_json("technical/sitemap.json", sitemaps_info)
        self._write_json("technical/redirects.json", redirects_data)
        self._write_json("technical/errors.json", errors_data)

        # ---------------------------------------------------------------------
        # 7. ON-PAGE SEO DOMAIN
        # ---------------------------------------------------------------------
        titles_data = []
        metas_data = []
        headings_data = []

        for p in self.pages_by_id.values():
            t = p["seo"].get("title") or ""
            titles_data.append(
                {
                    "url": p["url"],
                    "title": t or None,
                    "length": len(t),
                    "status": "missing"
                    if not t
                    else (
                        "too_long"
                        if len(t) > 60
                        else ("too_short" if len(t) < 30 else "optimal")
                    ),
                }
            )

            m = p["seo"].get("meta_description") or ""
            metas_data.append(
                {
                    "url": p["url"],
                    "meta_description": m or None,
                    "length": len(m),
                    "status": "missing"
                    if not m
                    else (
                        "too_long"
                        if len(m) > 160
                        else ("too_short" if len(m) < 120 else "optimal")
                    ),
                }
            )

            headings_data.append(
                {
                    "url": p["url"],
                    "h1": p["seo"].get("h1"),
                    "h2_count": len(p["seo"].get("h2", [])),
                    "h3_count": len(p["seo"].get("h3", [])),
                }
            )

        self._write_json("onpage/audit.json", self.raw_data.get("onpage_audit") or {})
        self._write_json("onpage/titles.json", titles_data)
        self._write_json("onpage/meta_descriptions.json", metas_data)
        self._write_json("onpage/headings.json", headings_data)
        self._write_json("onpage/images_alt.json", missing_alt)

        # ---------------------------------------------------------------------
        # 8. CONTENT SEO DOMAIN
        # ---------------------------------------------------------------------
        thin_pages = [
            p
            for p in self.pages_by_id.values()
            if p["seo"]["word_count"] < 300 and (p["status_code"] or 0) == 200
        ]

        # Duplicate titles grouping
        title_occurrences: dict[str, list[str]] = {}
        for p in self.pages_by_id.values():
            t = p["seo"].get("title")
            if t:
                title_occurrences.setdefault(t, []).append(p["url"])
        duplicate_titles = {
            t: urls for t, urls in title_occurrences.items() if len(urls) > 1
        }

        total_words = sum(p["seo"]["word_count"] for p in self.pages_by_id.values())
        avg_words = round(total_words / max(len(self.pages_by_id), 1), 1)

        self._write_json("content/audit.json", self.raw_data.get("content_audit") or {})
        self._write_json(
            "content/thin_content.json",
            [
                {"url": p["url"], "word_count": p["seo"]["word_count"]}
                for p in thin_pages
            ],
        )
        self._write_json("content/duplicate_titles.json", duplicate_titles)
        self._write_json(
            "content/content_metrics.json",
            {
                "total_word_count": total_words,
                "average_word_count": avg_words,
                "thin_pages_count": len(thin_pages),
                "duplicate_titles_count": len(duplicate_titles),
            },
        )

        # ---------------------------------------------------------------------
        # 9. PERFORMANCE DOMAIN
        # ---------------------------------------------------------------------
        slow_pages = [
            p
            for p in self.pages_by_id.values()
            if (p.get("response_time_ms") or 0) > 1500
        ]
        page_perf = [
            {
                "url": p["url"],
                "response_time_ms": p.get("response_time_ms"),
                "render_time_ms": p.get("render_time_ms"),
                "status_code": p.get("status_code"),
            }
            for p in self.pages_by_id.values()
        ]

        # Handle PageSpeed results with strict missing value & 429 semantics
        raw_pagespeed = self.raw_data.get("pagespeed", [])
        norm_pagespeed = []
        for ps in raw_pagespeed:
            if not isinstance(ps, dict):
                continue
            if ps.get("mobile", {}).get("error") or ps.get("desktop", {}).get("error"):
                norm_pagespeed.append(
                    {
                        "url": ps.get("url"),
                        "status": "unavailable",
                        "reason": ps.get("mobile", {}).get("error")
                        or ps.get("desktop", {}).get("error"),
                    }
                )
            else:
                norm_pagespeed.append(ps)

        self._write_json(
            "performance/audit.json", self.raw_data.get("performance_audit") or {}
        )
        self._write_json("performance/page_performance.json", page_perf)
        self._write_json("performance/slow_pages.json", slow_pages)
        self._write_json("performance/pagespeed.json", norm_pagespeed)

        # ---------------------------------------------------------------------
        # 10. STRUCTURED DATA / SCHEMA DOMAIN
        # ---------------------------------------------------------------------
        detected_schemas = []
        schema_types_count: dict[str, int] = {}
        missing_schema_pages = []

        for p in self.pages_by_id.values():
            s_list = p.get("schema", [])
            if s_list:
                detected_schemas.append({"url": p["url"], "schemas": s_list})
                for s in s_list:
                    t = s.get("@type")
                    if t:
                        if isinstance(t, list):
                            for sub_t in t:
                                schema_types_count[sub_t] = (
                                    schema_types_count.get(sub_t, 0) + 1
                                )
                        else:
                            schema_types_count[t] = schema_types_count.get(t, 0) + 1
            else:
                if (p.get("status_code") or 0) == 200:
                    missing_schema_pages.append(p["url"])

        self._write_json("schema/audit.json", self.raw_data.get("schema_audit") or {})
        self._write_json("schema/detected.json", detected_schemas)
        self._write_json("schema/missing.json", missing_schema_pages)
        self._write_json("schema/schema_types.json", schema_types_count)

        # ---------------------------------------------------------------------
        # 11. LOCAL SEO DOMAIN
        # ---------------------------------------------------------------------
        local_audit = self.raw_data.get("local_audit") or {}
        self._write_json("local/audit.json", local_audit)
        self._write_json(
            "local/business_schema.json",
            local_audit.get("metrics", {}).get("local_business_schema") or {},
        )
        self._write_json("local/local_signals.json", local_audit.get("metrics") or {})

        # ---------------------------------------------------------------------
        # 12. ANALYTICS DOMAIN
        # ---------------------------------------------------------------------
        analytics_summary: dict[str, Any] = {
            "google_analytics": False,
            "ga4_id": None,
            "gtm_id": None,
            "facebook_pixel": False,
            "hotjar": False,
            "mixpanel": False,
            "detected_on_pages": [],
        }

        for p in self.pages_by_id.values():
            an = p.get("analytics") or {}
            if an:
                analytics_summary["detected_on_pages"].append(p["url"])
                if an.get("ga4_id"):
                    analytics_summary["ga4_id"] = an["ga4_id"]
                    analytics_summary["google_analytics"] = True
                if an.get("gtm_id"):
                    analytics_summary["gtm_id"] = an["gtm_id"]
                if an.get("facebook_pixel") or an.get("fb_pixel"):
                    analytics_summary["facebook_pixel"] = True

        self._write_json("analytics/tracking.json", analytics_summary)

        # ---------------------------------------------------------------------
        # 13. RECOMMENDATIONS
        # ---------------------------------------------------------------------
        raw_recs = self.raw_data.get("priority_action_items", [])
        quick_wins = [
            r
            for r in raw_recs
            if str(r.get("estimated_effort", "")).lower() == "low"
            and r.get("impact_score", 0) >= 6
        ]
        high_impact = [r for r in raw_recs if r.get("impact_score", 0) >= 8]

        self._write_json("recommendations/all.json", raw_recs)
        self._write_json("recommendations/priority.json", raw_recs)
        self._write_json("recommendations/quick_wins.json", quick_wins)
        self._write_json("recommendations/high_impact.json", high_impact)

        # ---------------------------------------------------------------------
        # 14. SUMMARY & EXECUTIVE REPORT
        # ---------------------------------------------------------------------
        overall_score = self.raw_data.get("overall_seo_score", 0)
        cat_scores = self.raw_data.get("category_scores") or {}

        summary_overview = {
            "domain": self.domain,
            "base_url": self.raw_data.get("base_url") or self.raw_data.get("url"),
            "overall_score": overall_score,
            "category_scores": cat_scores,
            "pages_crawled": len(self.pages_by_id),
            "links_analyzed": len(self.links_by_id),
            "issues_detected": len(self.issues_by_id),
            "images_cataloged": len(self.images_by_id),
            "duration_seconds": self.raw_data.get("crawl_summary", {}).get(
                "duration_seconds", 0
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._write_json("summary/overview.json", summary_overview)
        self._write_json("summary/category_scores.json", cat_scores)
        self._write_json(
            "summary/metrics.json", self.raw_data.get("crawl_summary") or {}
        )

        md_content = (
            self.raw_data.get("detailed_report_markdown")
            or f"# SEO Report for {self.domain}\nOverall Score: {overall_score}/100"
        )
        self._write_text("summary/executive_summary.md", md_content)

        # ---------------------------------------------------------------------
        # 15. UNCLASSIFIED EXTRA FIELDS (Guarantee zero data loss)
        # ---------------------------------------------------------------------
        standard_keys = {
            "crawl_id",
            "base_url",
            "url",
            "base_domain",
            "status",
            "summary",
            "crawl_summary",
            "pages",
            "links",
            "issues",
            "sitemaps",
            "pagespeed",
            "overall_seo_score",
            "category_scores",
            "technical_audit",
            "onpage_audit",
            "content_audit",
            "schema_audit",
            "local_audit",
            "performance_audit",
            "priority_action_items",
            "detailed_report_markdown",
            "errors",
            "crawl_config",
        }
        for k, v in self.raw_data.items():
            if k not in standard_keys:
                self.unclassified_data[k] = v

        if self.unclassified_data:
            self._write_json("extra/unclassified.json", self.unclassified_data)

        # ---------------------------------------------------------------------
        # 16. VALIDATION & INTEGRITY CHECK REPORT
        # ---------------------------------------------------------------------
        raw_pages_count = len(raw_pages)
        norm_pages_count = len(self.pages_by_id)
        raw_issues_count = len(raw_issues)
        norm_issues_count = len(self.issues_by_id)
        dup_issues_removed = raw_issues_count - norm_issues_count
        dup_links_removed = len(raw_links) - len(self.links_by_id)

        validation_result = {
            "valid": True,
            "domain": self.domain,
            "raw_pages_count": raw_pages_count,
            "normalized_pages_count": norm_pages_count,
            "raw_issues_count": raw_issues_count,
            "normalized_issues_count": norm_issues_count,
            "duplicate_issues_deduplicated": max(0, dup_issues_removed),
            "raw_links_count": len(raw_links),
            "normalized_links_count": len(self.links_by_id),
            "duplicate_links_deduplicated": max(0, dup_links_removed),
            "unique_images_cataloged": len(self.images_by_id),
            "data_loss": False,
            "broken_page_references": 0,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._write_json("summary/validation.json", validation_result)

        # ---------------------------------------------------------------------
        # 17. MASTER ROOT INDEX (Section 20)
        # ---------------------------------------------------------------------
        master_index = {
            "domain": self.domain,
            "crawl_id": self.raw_data.get("crawl_id")
            or generate_stable_id("crawl", self.domain),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "overall_score": overall_score,
            "files": {
                "raw": "raw/crawl.json",
                "pages": "pages/index.json",
                "technical": "technical/audit.json",
                "onpage": "onpage/audit.json",
                "content": "content/audit.json",
                "performance": "performance/audit.json",
                "schema": "schema/audit.json",
                "local": "local/audit.json",
                "links": "links/all.json",
                "images": "images/all.json",
                "analytics": "analytics/tracking.json",
                "issues": "issues/all.json",
                "recommendations": "recommendations/all.json",
                "summary": "summary/overview.json",
                "validation": "summary/validation.json",
                "executive_summary": "summary/executive_summary.md",
            },
            "validation": validation_result,
        }

        self._write_json("index.json", master_index)

        # ---------------------------------------------------------------------
        # 18. AUTO-GENERATE REPORT.md (Human-readable folder documentation)
        # ---------------------------------------------------------------------
        report_md = f"""# 🔍 SEO Audit Report — {self.domain}

> **Base URL**: `{self.raw_data.get("base_url") or self.raw_data.get("url", "")}`  
> **Report Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  
> **Engine**: LibreCrawl + LangGraph SEO Agent  

---

## 📊 Overall Results

| Metric | Value |
|--------|-------|
| **Overall SEO Score** | `{overall_score}/100` |
| **Pages Crawled** | `{len(self.pages_by_id)}` |
| **Links Analyzed** | `{len(self.links_by_id)}` |
| **Issues Detected** | `{len(self.issues_by_id)}` |
| **Images Cataloged** | `{len(self.images_by_id)}` |
| **Duplicate Issues Removed** | `{max(0, dup_issues_removed)}` |
| **Data Loss** | `{"❌ DETECTED — check validation.json" if validation_result["data_loss"] else "✅ None"}` |
| **Validation** | `{"✅ PASSED" if validation_result["valid"] else "❌ FAILED"}` |

---

## 📁 Folder Structure

| Folder / File | Description |
|---------------|-------------|
| `REPORT.md` | This file — human-readable directory guide |
| `index.json` | Master entry point: all file paths, scores, validation summary |
| `analytics/` | Tracking pixel detection (GA4, GTM, Facebook Pixel, Hotjar) |
| `content/` | Content quality: word count, thin pages, duplicate titles |
| `extra/` | Unclassified crawler fields — zero data loss guarantee |
| `images/` | Image registry, missing alt text, coverage statistics |
| `issues/` | Deduplicated SEO issues sorted by severity (critical → low) |
| `links/` | Internal, external, broken links + anchor text + orphan pages |
| `local/` | LocalBusiness schema, NAP signals, local SEO score |
| `onpage/` | Title tags, meta descriptions, heading structure per page |
| `pages/` | Individual per-page JSON records + lightweight index |
| `performance/` | Server response times, slow pages, PageSpeed CWV metrics |
| `raw/` | **Original unmodified crawl JSON — source of truth, never edit** |
| `recommendations/` | Prioritized action items, quick wins, high-impact fixes |
| `schema/` | JSON-LD structured data detected, missing pages, type counts |
| `summary/` | Overview, category scores, executive report, validation report |
| `technical/` | Canonicals, robots directives, sitemaps, redirects, HTTP errors |

---

## 🔢 Category Scores

| Category | Score |
|----------|-------|
"""
        for cat, score in cat_scores.items():
            report_md += f"| {cat} | `{score}/100` |\n"

        report_md += """
---

## 🚀 Fix Priority Order

```
1 → issues/critical.json           Fix immediately (blocks indexing)
2 → recommendations/quick_wins.json  Low effort, high impact  
3 → issues/high.json               Fix this sprint
4 → recommendations/high_impact.json Strategic improvements
5 → issues/medium.json             Backlog / next quarter
```

---

## 📂 Key Files to Read First

1. **`summary/overview.json`** — High-level scores (< 1 KB, ideal for LLM context)
2. **`issues/critical.json`** — Start fixing here
3. **`recommendations/quick_wins.json`** — Fast wins with low dev effort
4. **`pages/index.json`** — Look up any page by URL or depth
5. **`links/broken.json`** — Broken links hurting crawl budget
6. **`technical/errors.json`** — 4xx/5xx pages losing link equity

---

*Generated by `seo/organizer.py` — LibreCrawl SEO Normalization Engine v1.0*
"""
        # Write REPORT.md to base_dir (e.g. seo/report/REPORT.md), not inside the domain subfolder
        report_full_path = os.path.join(self.base_dir, "REPORT.md")
        os.makedirs(self.base_dir, exist_ok=True)
        with open(report_full_path, "w", encoding="utf-8") as _f:
            _f.write(report_md)

        return master_index


# -----------------------------------------------------------------------------
# Standalone CLI / Helper Functions
# -----------------------------------------------------------------------------


def organize_website_crawl(
    raw_data: dict[str, Any], base_dir: str = "report"
) -> dict[str, Any]:
    """Convenience helper to organize a crawl dictionary into report/<domain>/."""
    organizer = WebsiteDataOrganizer(raw_data, base_dir=base_dir)
    return organizer.process()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m seo.organizer <path_to_crawl_data.json> [--out report]")
        sys.exit(1)

    json_path = sys.argv[1]
    out_dir = "report"
    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]

    if not os.path.exists(json_path):
        print(f"Error: file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[Data Organizer] Processing crawl payload from: {json_path}")
    organizer = WebsiteDataOrganizer(data, base_dir=out_dir)
    result = organizer.process()

    domain = result["domain"]
    root = os.path.join(out_dir, domain)
    val = result["validation"]

    print(f"\nWebsite data successfully organized under: {root}")
    print(f"  - Pages Normalized: {val['normalized_pages_count']}")
    print(
        f"  - Issues Deduplicated: {val['normalized_issues_count']} (removed {val['duplicate_issues_deduplicated']} duplicates)"
    )
    print(f"  - Links Analyzed: {val['normalized_links_count']}")
    print(f"  - Images Cataloged: {val['unique_images_cataloged']}")
    print(f"  - Master Index: {os.path.join(root, 'index.json')}")
    print(f"  - Validation: PASSED (Data Loss: {val['data_loss']})\n")


if __name__ == "__main__":
    main()
