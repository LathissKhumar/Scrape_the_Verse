"""
Preprocess SEO and Business Analysis reports into compact intelligence files.
Run once per company to create optimized input for prompt generation.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractors import extract_website_intelligence, extract_business_intelligence
from utils import load_json_file, logger, find_json_files, normalize_string
from config import settings


def preprocess_seo_report(company_name: str, seo_report_path: str) -> dict:
    """Extract compact website intelligence from SEO report."""
    logger.info(f"Preprocessing SEO report: {seo_report_path}")
    
    seo_data, error = load_json_file(seo_report_path)
    if error:
        raise ValueError(f"Failed to load SEO report: {error}")
    
    intelligence = extract_website_intelligence(seo_data, seo_report_path)
    return intelligence.model_dump()


def preprocess_business_report(company_name: str, biz_report_path: str) -> dict:
    """Extract compact business intelligence from Business Analysis report."""
    logger.info(f"Preprocessing Business Analysis report: {biz_report_path}")
    
    biz_data, error = load_json_file(biz_report_path)
    if error:
        raise ValueError(f"Failed to load Business Analysis report: {error}")
    
    intelligence = extract_business_intelligence(biz_data, biz_report_path)
    return intelligence.model_dump()


def discover_and_preprocess(company_name: str, output_dir: Path) -> tuple:
    """Discover reports, preprocess them, and save compact intelligence files."""
    normalized = normalize_string(company_name)
    
    # Find SEO report
    seo_files = find_json_files(settings.seo_report_dir)
    seo_report_path = None
    for f in seo_files:
        if normalize_string(Path(f).stem).startswith(normalized) or "atlas_audit" in f.lower():
            seo_report_path = f
            break
    
    if not seo_report_path:
        raise FileNotFoundError(f"No SEO report found for {company_name}")
    
    # Find Business Analysis report
    biz_files = find_json_files(settings.business_report_dir)
    biz_report_path = None
    for f in biz_files:
        if normalized in normalize_string(Path(f).stem) or "atlas_kliniek" in f.lower():
            biz_report_path = f
            break
    
    if not biz_report_path:
        raise FileNotFoundError(f"No Business Analysis report found for {company_name}")
    
    # Preprocess
    seo_intel = preprocess_seo_report(company_name, seo_report_path)
    biz_intel = preprocess_business_report(company_name, biz_report_path)
    
    # Save compact files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    seo_output = output_dir / f"{normalized}_seo_intelligence.json"
    biz_output = output_dir / f"{normalized}_business_intelligence.json"
    
    with open(seo_output, "w", encoding="utf-8") as f:
        json.dump(seo_intel, f, indent=2, ensure_ascii=False)
    
    with open(biz_output, "w", encoding="utf-8") as f:
        json.dump(biz_intel, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved compact SEO intelligence: {seo_output}")
    logger.info(f"Saved compact Business intelligence: {biz_output}")
    
    return seo_output, biz_output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocess.py <company_name>")
        sys.exit(1)
    
    company_name = sys.argv[1]
    output_dir = Path(settings.output_dir) / "intelligence"
    
    try:
        seo_out, biz_out = discover_and_preprocess(company_name, output_dir)
        print(f"\n✓ Preprocessing complete!")
        print(f"  SEO Intelligence: {seo_out}")
        print(f"  Business Intelligence: {biz_out}")
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        sys.exit(1)