import json
import logging
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("prompt_generation_agent")
    logger.setLevel(getattr(logging, level.upper()))
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logging()


def normalize_string(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[_\-\s\.\,\;]+", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def load_json_file(filepath: str) -> tuple[dict[str, Any] | None, str | None]:
    path = Path(filepath)
    if not path.exists():
        return None, f"File not found: {filepath}"

    if path.stat().st_size == 0:
        return None, f"File is empty: {filepath}"

    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                data = json.load(f)
            return data, None
        except json.JSONDecodeError:
            continue
        except Exception:
            continue

    return None, f"Failed to parse JSON with any encoding: {filepath}"


def find_json_files(directory: str) -> list[str]:
    path = Path(directory)
    if not path.exists():
        return []
    return [str(f) for f in path.rglob("*.json") if f.is_file()]


def extract_domain_from_url(url: str) -> str:
    if not url:
        return ""
    match = re.search(r"https?://([^/]+)", url)
    if match:
        domain = match.group(1)
        domain = domain.replace("www.", "")
        return domain
    return ""


def get_filename_stem(filepath: str) -> str:
    return Path(filepath).stem


def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"


def format_issue_summary(findings: list[dict[str, Any]], max_items: int = 10) -> str:
    if not findings:
        return "None"
    lines = []
    for i, f in enumerate(findings[:max_items]):
        severity = f.get("severity", "unknown").upper()
        title = f.get("title", "Unknown Issue")
        url = f.get("url", "")
        lines.append(f"  [{severity}] {title} ({url})")
    if len(findings) > max_items:
        lines.append(f"  ... and {len(findings) - max_items} more issues")
    return "\n".join(lines)


def count_findings_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        severity = f.get("severity", "").lower()
        if severity in counts:
            counts[severity] += 1
    return counts
