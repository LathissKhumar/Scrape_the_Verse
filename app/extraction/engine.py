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

        # Normalize content to RawPage or string
        if isinstance(raw_content, list) and raw_content:
            first_item = raw_content[0]
            page = first_item if isinstance(first_item, RawPage) else RawPage(
                url=first_item.get("url") if isinstance(first_item, dict) else None,
                html=first_item.get("html") if isinstance(first_item, dict) else (str(first_item) if isinstance(first_item, str) else None),
                text=first_item.get("text") if isinstance(first_item, dict) else None,
                raw_payload=first_item,
            )
        else:
            page = raw_content if isinstance(raw_content, RawPage) else RawPage(
                html=raw_content.get("html") if isinstance(raw_content, dict) else (str(raw_content) if isinstance(raw_content, str) else None),
                text=raw_content.get("text") if isinstance(raw_content, dict) else None,
                raw_payload=raw_content,
            )

        # 2. Try CSS / XPath if base selector exists
        if effective_schema.base_selector:
            if effective_schema.base_selector.startswith("/") or effective_schema.base_selector.startswith(".//"):
                logger.info("Attempting deterministic XPath extraction")
                records = self.xpath_extractor.extract(page, effective_schema)
                if records:
                    deduped = self.deduplicator.deduplicate(records)
                    conformed = self._enforce_task_schema(deduped, task)
                    return ExtractionResult(
                        records=conformed,
                        strategy_used=ExtractionStrategyEnum.XPATH.value,
                        fallback_used=False,
                        metadata={"record_count": len(conformed)},
                    )
            else:
                logger.info("Attempting deterministic CSS extraction")
                records = self.css_extractor.extract(page, effective_schema)
                if records:
                    deduped = self.deduplicator.deduplicate(records)
                    conformed = self._enforce_task_schema(deduped, task)
                    return ExtractionResult(
                        records=conformed,
                        strategy_used=ExtractionStrategyEnum.CSS.value,
                        fallback_used=False,
                        metadata={"record_count": len(conformed)},
                    )

        # 3. Check for HTML Table Extraction
        table_records = self.table_extractor.extract(page, effective_schema)
        if table_records:
            logger.info(f"Deterministic Table extractor extracted {len(table_records)} record(s)")
            deduped = self.deduplicator.deduplicate(table_records)
            conformed = self._enforce_task_schema(deduped, task)
            return ExtractionResult(
                records=conformed,
                strategy_used=ExtractionStrategyEnum.TABLE.value,
                fallback_used=False,
                metadata={"record_count": len(conformed)},
            )

        # 4. Try Regex Extraction for pattern fields
        regex_records = self.regex_extractor.extract(page, effective_schema)
        if regex_records:
            logger.info(f"Deterministic Regex extractor extracted {len(regex_records)} record(s)")
            deduped = self.deduplicator.deduplicate(regex_records)
            conformed = self._enforce_task_schema(deduped, task)
            return ExtractionResult(
                records=conformed,
                strategy_used=ExtractionStrategyEnum.REGEX.value,
                fallback_used=False,
                metadata={"record_count": len(conformed)},
            )

        # 5. LLM Extraction Fallback with Qwen3:8b
        if self.llm_extractor:
            logger.info("Cascading to LLM extraction strategy (Qwen3:8b)")
            llm_records = await self.llm_extractor.extract_async(page, task, effective_schema)
            deduped = self.deduplicator.deduplicate(llm_records)
            conformed = self._enforce_task_schema(deduped, task)
            return ExtractionResult(
                records=conformed,
                strategy_used=ExtractionStrategyEnum.LLM.value,
                fallback_used=True,
                metadata={"record_count": len(conformed)},
            )

        # Default empty result
        return ExtractionResult(
            records=[],
            strategy_used="none",
            fallback_used=False,
            metadata={"record_count": 0},
        )
