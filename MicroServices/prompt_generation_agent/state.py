from typing import Any, TypedDict


class PromptGenerationState(TypedDict):
    company_name: str
    normalized_name: str
    seo_report_path: str | None
    business_report_path: str | None
    seo_data: dict[str, Any]
    business_data: dict[str, Any]
    website_intelligence: dict[str, Any]
    business_intelligence: dict[str, Any]
    website_exists: bool
    prompt_type: str | None
    prompt_context: dict[str, Any]
    generated_prompt: str | None
    structured_output: dict[str, Any] | None
    validation_errors: list[str]
    validation_warnings: list[str]
    errors: list[str]
    warnings: list[str]
    repair_attempts: int
