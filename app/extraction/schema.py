from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ExtractionStrategyEnum(str, Enum):
    CSS = "css"
    XPATH = "xpath"
    REGEX = "regex"
    TABLE = "table"
    SEMANTIC = "semantic"
    LLM = "llm"
    PASSTHROUGH = "passthrough"


class RawPage(BaseModel):
    """Container for raw scraped content retrieved from Bright Data or web transport."""

    url: Optional[str] = Field(default=None, description="Target URL of the page.")
    html: Optional[str] = Field(default=None, description="Raw HTML string if returned.")
    markdown: Optional[str] = Field(default=None, description="Raw Markdown string if returned.")
    text: Optional[str] = Field(default=None, description="Extracted plain text if returned.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Page metadata (status, headers, etc.).")
    raw_payload: Optional[Any] = Field(default=None, description="Raw underlying payload object.")

    def get_primary_content(self) -> str:
        """Return the richest available text representation."""
        if self.html and self.html.strip():
            return self.html
        if self.markdown and self.markdown.strip():
            return self.markdown
        if self.text and self.text.strip():
            return self.text
        if isinstance(self.raw_payload, str):
            return self.raw_payload
        return ""


class FieldRule(BaseModel):
    """Rule defining how a single field should be extracted."""

    name: str = Field(..., description="Target field name.")
    field_type: str = Field(default="string", description="Field type (string, number, url, email, etc.).")
    selector: Optional[str] = Field(default=None, description="CSS selector or XPath expression.")
    attribute: Optional[str] = Field(default=None, description="HTML attribute to extract (e.g. href, src, title).")
    regex_pattern: Optional[str] = Field(default=None, description="Regular expression pattern if applicable.")
    default_value: Optional[Any] = Field(default=None, description="Default value if extraction fails.")


class ExtractionSchema(BaseModel):
    """Schema configuring structured extraction for a task."""

    strategy: ExtractionStrategyEnum = Field(
        default=ExtractionStrategyEnum.LLM,
        description="Primary extraction strategy to attempt.",
    )
    base_selector: Optional[str] = Field(
        default=None,
        description="Container selector (CSS or XPath) for repeating records.",
    )
    fields: list[FieldRule] = Field(
        default_factory=list,
        description="List of field rules to extract per record.",
    )
    strict_schema: bool = Field(
        default=False,
        description="If True, drop records missing any mandatory field.",
    )


class ExtractionResult(BaseModel):
    """Result of an extraction operation."""

    records: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured extracted records.",
    )
    strategy_used: str = Field(
        ...,
        description="The strategy that produced the records (e.g. css, table, llm).",
    )
    fallback_used: bool = Field(
        default=False,
        description="True if a fallback strategy was used after an earlier strategy failed.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extraction diagnostics and statistics.",
    )
