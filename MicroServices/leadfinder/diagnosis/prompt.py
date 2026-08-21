import json
from typing import Any

DIAGNOSIS_SYSTEM_PROMPT = """You are an expert web scraping failure diagnostic agent.
Your objective is to diagnose the root cause of a scraping/extraction degradation and recommend an adaptive repair strategy.

Allowed Values:
- root_cause: ["SELECTOR_DRIFT", "DOM_STRUCTURE_CHANGE", "SCRAPER_OUTPUT_MISSING", "EXTRACTION_DEGRADATION", "SCHEMA_MISMATCH", "PAGINATION_FAILURE", "RENDERING_FAILURE", "CONTENT_FILTER_FAILURE", "REGEX_PATTERN_FAILURE", "TABLE_STRUCTURE_CHANGE", "LLM_EXTRACTION_FAILURE", "SOURCE_DATA_QUALITY", "UNKNOWN"]
- affected_stage: ["scraper_execution", "css_extraction", "xpath_extraction", "regex_extraction", "table_extraction", "llm_extraction", "schema_validation", "source_page", "unknown"]
- repair_strategy: ["RETRY_SAME_CONFIGURATION", "REPAIR_CSS_SELECTORS", "REPAIR_XPATH_SELECTORS", "REPAIR_REGEX_PATTERN", "REPAIR_TABLE_SCHEMA", "REPAIR_EXTRACTION_SCHEMA", "SWITCH_EXTRACTION_STRATEGY", "REGENERATE_LLM_EXTRACTION_SCHEMA", "ADJUST_CONTENT_CHUNKING", "ADJUST_SEMANTIC_FILTERING", "RECHECK_RAW_CONTENT", "ESCALATE"]
- recommended_action: ["REPAIR_EXTRACTION_SCHEMA", "RETRY_SCRAPER", "FALLBACK_TO_LLM_EXTRACTION", "FALLBACK_TO_TABLE_EXTRACTION", "UPDATE_SOURCE_EXPECTATIONS", "MANUAL_INSPECTION", "NONE"]

Rules:
1. Base your diagnosis strictly on the provided evidence. Do NOT invent DOM elements, class names, or selectors not present in the evidence.
2. If the page content is intact but the requested field is legitimately absent from the source page, select root_cause="SOURCE_DATA_QUALITY".
3. If page structure/classes changed or fields are missing due to selector mismatch, select root_cause="SELECTOR_DRIFT".
4. Assign a numerical confidence score between 0.0 and 1.0.
5. Return ONLY a valid JSON object matching the requested schema. No markdown fences or explanations outside the JSON object.
"""


def build_diagnosis_prompt(evidence: dict[str, Any]) -> str:
    """Construct the formatted LLM diagnostic prompt from the evidence package."""
    evidence_json = json.dumps(evidence, indent=2)
    return f"""Analyze the following scraping and validation failure evidence and provide a structured diagnosis:

Failure Evidence:
{evidence_json}

Return a single JSON object with the following fields:
{{
  "diagnosis_status": "diagnosed",
  "root_cause": "SELECTOR_DRIFT | DOM_STRUCTURE_CHANGE | ...",
  "confidence": 0.90,
  "failure_category": "EXTRACTION_DEGRADATION",
  "affected_stage": "css_extraction | ...",
  "affected_fields": ["field_name"],
  "evidence": ["bullet point 1", "bullet point 2"],
  "repair_strategy": "REPAIR_CSS_SELECTORS | SWITCH_EXTRACTION_STRATEGY | ...",
  "repair_targets": ["target_1", "target_2"],
  "recommended_action": "REPAIR_EXTRACTION_SCHEMA | FALLBACK_TO_LLM_EXTRACTION | ..."
}}
"""
