from typing import TypedDict, List, Dict, Optional, Any


class PromptGenerationState(TypedDict):
    company_name: str
    normalized_name: str
    seo_report_path: Optional[str]
    business_report_path: Optional[str]
    seo_data: Dict[str, Any]
    business_data: Dict[str, Any]
    website_intelligence: Dict[str, Any]
    business_intelligence: Dict[str, Any]
    website_exists: bool
    prompt_type: Optional[str]
    prompt_context: Dict[str, Any]
    generated_prompt: Optional[str]
    structured_output: Optional[Dict[str, Any]]
    validation_errors: List[str]
    validation_warnings: List[str]
    errors: List[str]
    warnings: List[str]
    repair_attempts: int