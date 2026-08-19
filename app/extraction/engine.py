from typing import Any, Optional
from app.config.logging import get_logger
from app.extraction.css import CSSExtractor
from app.extraction.dedup import RecordDeduplicator
from app.extraction.llm import LLMExtractor
from app.extraction.regex import RegexExtractor
from app.extraction.schema import (
    ExtractionResult,
    ExtractionSchema,
    ExtractionStrategyEnum,
    FieldRule,
    RawPage,
)
from app.extraction.tables import TableExtractor
from app.extraction.xpath import XPathExtractor
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask

logger = get_logger("EXTRACTION_ENGINE")


class ExtractionEngine:
    """Central extraction engine orchestrating deterministic and LLM strategies with fallback."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        css_extractor: Optional[CSSExtractor] = None,
        xpath_extractor: Optional[XPathExtractor] = None,
        regex_extractor: Optional[RegexExtractor] = None,
        table_extractor: Optional[TableExtractor] = None,
        llm_extractor: Optional[LLMExtractor] = None,
        deduplicator: Optional[RecordDeduplicator] = None,
    ):
        self.css_extractor = css_extractor or CSSExtractor()
        self.xpath_extractor = xpath_extractor or XPathExtractor()
        self.regex_extractor = regex_extractor or RegexExtractor()
        self.table_extractor = table_extractor or TableExtractor()
        self.deduplicator = deduplicator or RecordDeduplicator()
        self.llm_extractor = llm_extractor
        if not self.llm_extractor and llm_client:
            self.llm_extractor = LLMExtractor(llm_client=llm_client)

    def _build_default_schema(self, task: ScrapingTask) -> ExtractionSchema:
        """Construct an ExtractionSchema from a ScrapingTask."""
        field_rules = []
        for field_name in task.fields:
            field_type = "string"
            if task.output_schema and field_name in task.output_schema:
                field_type = str(task.output_schema[field_name])
            field_rules.append(FieldRule(name=field_name, field_type=field_type))

        return ExtractionSchema(
            strategy=ExtractionStrategyEnum.LLM,
            fields=field_rules,
        )

    def _enforce_task_schema(
        self,
        records: list[dict[str, Any]],
        task: ScrapingTask,
    ) -> list[dict[str, Any]]:
        """Ensure all requested task fields are present in each record, filling missing with None."""
        if not task.fields:
            return records

        conformed: list[dict[str, Any]] = []
        for rec in records:
            conformed_rec: dict[str, Any] = {}
            for field in task.fields:
                conformed_rec[field] = rec.get(field)
            # Include any other fields already present if structurally useful
            for k, v in rec.items():
                if k not in conformed_rec:
                    conformed_rec[k] = v
            conformed.append(conformed_rec)

        return conformed

    async def extract(
        self,
        raw_results: Any,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> ExtractionResult:
        """Alias for extract_async to maintain consistent interface across agent layers."""
        return await self.extract_async(raw_content=raw_results, task=task, schema=schema)

    async def extract_async(
        self,
        raw_content: Any,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> ExtractionResult:
        """Execute structured extraction asynchronously across content and task."""
        effective_schema = schema or self._build_default_schema(task)

        # 1. Check if raw_content is already a list of structured records (from Bright Data direct collector)
        if isinstance(raw_content, list) and raw_content and isinstance(raw_content[0], dict):
            first_item = raw_content[0]
            raw_keys = {"url", "html", "markdown", "text", "metadata", "raw_payload"}
            # If the item contains html or matches raw page fields, it is a raw page, not structured records
            is_raw_page = bool("html" in first_item or "markdown" in first_item or set(first_item.keys()).issubset(raw_keys))
            if not is_raw_page:
                logger.info("Raw content is already structured records. Applying passthrough normalization.")
                deduped = self.deduplicator.deduplicate(raw_content)
                conformed = self._enforce_task_schema(deduped, task)
                return ExtractionResult(
                    records=conformed,
                    strategy_used=ExtractionStrategyEnum.PASSTHROUGH.value,
                    fallback_used=False,
                    metadata={"record_count": len(conformed)},
                )

        # 2. Normalize content to list of RawPage instances
        pages: list[RawPage] = []
        if isinstance(raw_content, list):
            for item in raw_content:
                if isinstance(item, RawPage):
                    pages.append(item)
                elif isinstance(item, dict):
                    pages.append(RawPage(
                        url=item.get("url"),
                        html=item.get("html") or (str(item) if not isinstance(item, dict) else None),
                        text=item.get("text"),
                        raw_payload=item,
                    ))
                elif item:
                    pages.append(RawPage(html=str(item), raw_payload=item))
        elif isinstance(raw_content, RawPage):
            pages.append(raw_content)
        elif raw_content:
            pages.append(RawPage(
                html=raw_content.get("html") if isinstance(raw_content, dict) else str(raw_content),
                text=raw_content.get("text") if isinstance(raw_content, dict) else None,
                raw_payload=raw_content,
            ))

        if not pages:
            return ExtractionResult(records=[], strategy_used="none", fallback_used=False, metadata={"record_count": 0})

        all_extracted_records: list[dict[str, Any]] = []
        dominant_strategy = "unknown"
        any_fallback = False

        for page in pages:
            page_records: list[dict[str, Any]] = []
            page_strategy = "none"
            page_fallback = False

            # Strategy A: CSS / XPath if base selector exists
            if effective_schema.base_selector:
                if effective_schema.base_selector.startswith("/") or effective_schema.base_selector.startswith(".//"):
                    logger.info("Attempting deterministic XPath extraction")
                    records = self.xpath_extractor.extract(page, effective_schema)
                    if records:
                        page_records = records
                        page_strategy = ExtractionStrategyEnum.XPATH.value
                else:
                    logger.info("Attempting deterministic CSS extraction")
                    records = self.css_extractor.extract(page, effective_schema)
                    if records:
                        page_records = records
                        page_strategy = ExtractionStrategyEnum.CSS.value

            # Strategy B: HTML Table Extraction (if table contains requested fields)
            if not page_records:
                table_records = self.table_extractor.extract(page, effective_schema)
                if table_records:
                    has_table_coverage = all(
                        any(r.get(f) is not None for r in table_records)
                        for f in task.fields
                    )
                    if has_table_coverage or not self.llm_extractor:
                        logger.info(f"Deterministic Table extractor extracted {len(table_records)} record(s)")
                        page_records = table_records
                        page_strategy = ExtractionStrategyEnum.TABLE.value
                    else:
                        logger.info("Table extraction returned incomplete field coverage; cascading to next strategy")

            # Strategy C: Regex Extraction for pattern fields
            if not page_records:
                regex_records = self.regex_extractor.extract(page, effective_schema)
                if regex_records:
                    has_coverage = all(
                        any(r.get(f) is not None for r in regex_records)
                        for f in task.fields
                    )
                    if has_coverage or not self.llm_extractor:
                        logger.info(f"Deterministic Regex extractor extracted {len(regex_records)} record(s)")
                        page_records = regex_records
                        page_strategy = ExtractionStrategyEnum.REGEX.value
                    else:
                        logger.info("Regex extraction returned incomplete field coverage; cascading to LLM extraction")

            # Strategy D: LLM Extraction Fallback with Qwen3:8b
            if not page_records and self.llm_extractor:
                logger.info("Cascading to LLM extraction strategy (Qwen3:8b)")
                llm_records = await self.llm_extractor.extract_async(page, task, effective_schema)
                if llm_records:
                    page_records = llm_records
                    page_strategy = ExtractionStrategyEnum.LLM.value
                    page_fallback = True

            all_extracted_records.extend(page_records)
            if page_strategy != "none":
                dominant_strategy = page_strategy
            if page_fallback:
                any_fallback = True

        deduped = self.deduplicator.deduplicate(all_extracted_records)
        conformed = self._enforce_task_schema(deduped, task)

        return ExtractionResult(
            records=conformed,
            strategy_used=dominant_strategy,
            fallback_used=any_fallback,
            metadata={"record_count": len(conformed)},
        )
