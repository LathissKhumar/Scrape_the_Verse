import json
import sys
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from utils import (
    normalize_string,
    similarity,
    find_json_files,
    load_json_file,
    extract_domain_from_url,
    get_filename_stem,
    logger,
)
from config import settings


class MatchResult:
    def __init__(
        self,
        filepath: str,
        score: float,
        match_signals: Dict[str, Any],
        json_data: Dict[str, Any],
    ):
        self.filepath = filepath
        self.score = score
        self.match_signals = match_signals
        self.json_data = json_data


def load_seo_report_metadata(filepath: str) -> Dict[str, Any]:
    data, _ = load_json_file(filepath)
    if not data or not isinstance(data, dict):
        return {}

    metadata = {
        "domain": data.get("url", ""),
        "base_url": data.get("base_url", ""),
        "domain_name": extract_domain_from_url(data.get("url", "")),
        "crawl_status": data.get("status", ""),
        "pages_crawled": data.get("raw_crawl_data", {}).get("summary", {}).get("total_pages_crawled", 0),
    }
    return metadata


def load_business_report_metadata(filepath: str) -> Dict[str, Any]:
    data, _ = load_json_file(filepath)
    if not data or not isinstance(data, dict):
        return {}

    metadata = {
        "company_name": data.get("company_name", ""),
        "website": data.get("website", ""),
        "domain_name": extract_domain_from_url(data.get("website", "")),
        "industry": data.get("industry", ""),
        "location": data.get("location", ""),
    }
    return metadata


def score_seo_match(
    company_name: str,
    normalized_company: str,
    filepath: str,
    metadata: Dict[str, Any],
) -> Tuple[float, Dict[str, Any]]:
    signals = {}
    scores = []

    filename_stem = get_filename_stem(filepath)
    normalized_filename = normalize_string(filename_stem)

    filename_sim = similarity(normalized_company, normalized_filename)
    signals["filename_similarity"] = filename_sim
    scores.append(filename_sim * 0.4)

    domain = metadata.get("domain_name", "")
    normalized_domain = normalize_string(domain)
    domain_sim = similarity(normalized_company, normalized_domain)
    signals["domain_similarity"] = domain_sim
    scores.append(domain_sim * 0.3)

    crawl_status = metadata.get("crawl_status", "")
    if crawl_status == "completed":
        signals["crawl_completed"] = True
        scores.append(0.2)
    else:
        signals["crawl_completed"] = False

    pages_crawled = metadata.get("pages_crawled", 0)
    if pages_crawled > 0:
        signals["has_pages"] = True
        scores.append(min(pages_crawled / 100, 1.0) * 0.1)

    return sum(scores), signals


def score_business_match(
    company_name: str,
    normalized_company: str,
    filepath: str,
    metadata: Dict[str, Any],
) -> Tuple[float, Dict[str, Any]]:
    signals = {}
    scores = []

    filename_stem = get_filename_stem(filepath)
    normalized_filename = normalize_string(filename_stem)

    filename_sim = similarity(normalized_company, normalized_filename)
    signals["filename_similarity"] = filename_sim
    scores.append(filename_sim * 0.35)

    biz_company = metadata.get("company_name", "")
    normalized_biz_company = normalize_string(biz_company)
    company_sim = similarity(normalized_company, normalized_biz_company)
    signals["company_name_match"] = company_sim
    scores.append(company_sim * 0.35)

    domain = metadata.get("domain_name", "")
    normalized_domain = normalize_string(domain)
    domain_sim = similarity(normalized_company, normalized_domain)
    signals["domain_similarity"] = domain_sim
    scores.append(domain_sim * 0.2)

    industry = metadata.get("industry", "")
    if industry and "dental" in industry.lower():
        signals["dental_industry"] = True
        scores.append(0.1)

    return sum(scores), signals


def discover_seo_report(company_name: str) -> Tuple[Optional[str], List[MatchResult]]:
    normalized_company = normalize_string(company_name)
    logger.info(f"Searching SEO reports in: {settings.seo_report_dir}")

    files = find_json_files(settings.seo_report_dir)
    if not files:
        logger.warning("No SEO report files found")
        return None, []

    candidates = []
    for filepath in files:
        metadata = load_seo_report_metadata(filepath)
        if not metadata:
            continue

        score, signals = score_seo_match(company_name, normalized_company, filepath, metadata)
        if score > 0.15:
            data, _ = load_json_file(filepath)
            if data:
                candidates.append(MatchResult(filepath, score, signals, data))

    candidates.sort(key=lambda x: x.score, reverse=True)

    logger.info(f"Found {len(candidates)} SEO report candidates")
    for c in candidates[:5]:
        logger.debug(f"  {c.filepath} - score: {c.score:.3f} - signals: {c.match_signals}")

    if not candidates:
        return None, []

    best = candidates[0]
    if len(candidates) > 1 and candidates[1].score > best.score * 0.8:
        logger.warning(f"Multiple SEO candidates with similar scores:")
        for i, c in enumerate(candidates[:3]):
            logger.warning(f"  {i+1}. {c.filepath} (score: {c.score:.3f})")

    return best.filepath, candidates


def discover_business_report(company_name: str) -> Tuple[Optional[str], List[MatchResult]]:
    normalized_company = normalize_string(company_name)
    logger.info(f"Searching Business Analysis reports in: {settings.business_report_dir}")

    files = find_json_files(settings.business_report_dir)
    if not files:
        logger.warning("No Business Analysis report files found")
        return None, []

    candidates = []
    for filepath in files:
        metadata = load_business_report_metadata(filepath)
        if not metadata:
            continue

        score, signals = score_business_match(company_name, normalized_company, filepath, metadata)
        if score > 0.15:
            data, _ = load_json_file(filepath)
            if data:
                candidates.append(MatchResult(filepath, score, signals, data))

    candidates.sort(key=lambda x: x.score, reverse=True)

    logger.info(f"Found {len(candidates)} Business Analysis candidates")
    for c in candidates[:5]:
        logger.debug(f"  {c.filepath} - score: {c.score:.3f} - signals: {c.match_signals}")

    if not candidates:
        return None, []

    best = candidates[0]
    if len(candidates) > 1 and candidates[1].score > best.score * 0.8:
        logger.warning(f"Multiple Business Analysis candidates with similar scores:")
        for i, c in enumerate(candidates[:3]):
            logger.warning(f"  {i+1}. {c.filepath} (score: {c.score:.3f})")

    return best.filepath, candidates


def validate_website_exists(seo_data: Dict[str, Any]) -> bool:
    crawl_status = seo_data.get("status", "")
    raw_data = seo_data.get("raw_crawl_data", {})
    summary = raw_data.get("summary", {})
    pages_crawled = summary.get("total_pages_crawled", 0)
    base_url = seo_data.get("url", "") or seo_data.get("base_url", "")

    return crawl_status == "completed" and pages_crawled > 0 and bool(base_url)


def select_best_match(
    candidates: List[MatchResult],
    report_type: str,
    company_name: str,
) -> Optional[MatchResult]:
    if not candidates:
        return None

    # Always auto-select the best match for now
    # The scoring should be reliable enough
    best = candidates[0]
    
    # Log if there are close competitors
    if len(candidates) > 1 and candidates[1].score > best.score * 0.9:
        logger.warning(f"Multiple {report_type} candidates with very similar scores:")
        for i, c in enumerate(candidates[:3]):
            logger.warning(f"  {i+1}. {Path(c.filepath).name} (score: {c.score:.3f})")
    
    return best