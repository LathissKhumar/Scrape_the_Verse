import asyncio
import html
from typing import Any, Optional
from urllib.parse import urljoin
from app.config.logging import get_logger
from app.crawler.link_discovery import LinkDiscoveryEngine
from app.extraction.css import CSSExtractor
from app.extraction.dedup import RecordDeduplicator
from app.extraction.grid_cards import GridCardExtractor
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
from app.extraction.vision import VisionTextExtractor
from app.extraction.xpath import XPathExtractor
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask

logger = get_logger("EXTRACTION_ENGINE")

FIELD_SYNONYM_MAP: dict[str, list[str]] = {
    "quote": ["quotetext", "text", "quotecontent", "content", "statement", "message"],
    "title": ["productname", "producttitle", "name", "itemname", "booktitle", "heading", "titlename"],
    "price": ["cost", "priceamount", "pricing", "amount", "currentprice", "rate", "pricetaxexcl", "priceexcltax"],
    "availability": ["stock", "stockstatus", "status", "instock", "inventory"],
    "rating": ["stars", "score", "reviewrating", "customerrating"],
    "reviews": ["reviewcount", "numreviews", "numberofreviews", "totalreviews"],
    "specifications": ["specs", "technicalspecifications", "features", "details", "techspecs", "description"],
    "tags": ["taglist", "keywords", "categories", "labels", "topics", "tag"],
    "author": ["authorname", "creator", "writer", "by"],
    "image": ["image_url", "imageurl", "img", "thumbnail", "photo", "pic", "image_src", "imagesrc", "picture"],
    "image_url": ["image", "img", "thumbnail", "photo", "pic", "image_src", "imagesrc", "picture", "imageurl"],
    "upc": ["upccode", "universalproductcode", "sku", "barcode", "productcode", "isbn"],
}


class ExtractionEngine:
    """Central extraction engine orchestrating deterministic, card grid, vision, and LLM strategies."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        css_extractor: Optional[CSSExtractor] = None,
        xpath_extractor: Optional[XPathExtractor] = None,
        regex_extractor: Optional[RegexExtractor] = None,
        table_extractor: Optional[TableExtractor] = None,
        grid_card_extractor: Optional[GridCardExtractor] = None,
        vision_extractor: Optional[VisionTextExtractor] = None,
        llm_extractor: Optional[LLMExtractor] = None,
        deduplicator: Optional[RecordDeduplicator] = None,
        browser_executor: Optional[Any] = None,
        link_discovery: Optional[LinkDiscoveryEngine] = None,
    ):
        self.css_extractor = css_extractor or CSSExtractor()
        self.xpath_extractor = xpath_extractor or XPathExtractor()
        self.regex_extractor = regex_extractor or RegexExtractor()
        self.table_extractor = table_extractor or TableExtractor()
        self.grid_card_extractor = grid_card_extractor or GridCardExtractor()
        self.vision_extractor = vision_extractor or VisionTextExtractor()
        self.deduplicator = deduplicator or RecordDeduplicator()
        self.browser_executor = browser_executor
        self.link_discovery = link_discovery or LinkDiscoveryEngine()
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
        base_url: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Ensure all requested task fields are present in each record with intelligent synonym aliasing and absolute URL resolution."""
        if not task.fields:
            return records

        conformed: list[dict[str, Any]] = []
        for rec in records:
            conformed_rec: dict[str, Any] = {}
            rec_clean_map = {k.lower().replace("_", "").replace(" ", ""): v for k, v in rec.items()}

            for field in task.fields:
                val = rec.get(field)
                norm_field = field.lower().replace("_", "").replace(" ", "")

                if val is None:
                    val = rec_clean_map.get(norm_field)

                if val is None:
                    synonyms = (
                        FIELD_SYNONYM_MAP.get(field.lower(), [])
                        + FIELD_SYNONYM_MAP.get(norm_field, [])
                    )
                    for syn in synonyms:
                        syn_clean = syn.lower().replace("_", "").replace(" ", "")
                        if syn_clean in rec_clean_map:
                            val = rec_clean_map[syn_clean]
                            break

                # Auto-resolve relative URLs for image/link fields
                if val and isinstance(val, str):
                    val = html.unescape(val.strip())
                    if base_url:
                        is_url_field = any(u in norm_field for u in ["image", "img", "thumbnail", "picture", "url", "link", "href"])
                        if is_url_field and (val.startswith("../") or val.startswith("/") or not val.startswith("http")):
                            val = urljoin(base_url, val)

                conformed_rec[field] = val

            for k, v in rec.items():
                if k not in conformed_rec:
                    conformed_rec[k] = html.unescape(v.strip()) if isinstance(v, str) else v
            conformed.append(conformed_rec)

        return conformed

    def _filter_grounded_records(
        self,
        records: list[dict[str, Any]],
        task: ScrapingTask,
    ) -> list[dict[str, Any]]:
        """Filter out orphaned records lacking requested primary identifiers or having insufficient field grounding."""
        if not records:
            return []

        primary_identifiers = {
            "name", "title", "productname", "product_name", "producttitle", "heading",
            "booktitle", "quote", "text", "author", "authorname", "itemname", "summary"
        }
        primary_requested = [
            f for f in task.fields
            if any(pk in f.lower().replace("_", "").replace(" ", "") for pk in primary_identifiers)
        ]

        grounded: list[dict[str, Any]] = []
        for rec in records:
            # Count populated non-empty values
            populated_fields = [
                k for k, v in rec.items()
                if v is not None and str(v).strip() and str(v).strip().lower() not in ("none", "null", "n/a")
            ]

            if not populated_fields:
                continue

            # If task requested primary key(s), ensure at least one primary identifier is present and non-empty
            if primary_requested:
                has_primary = any(
                    rec.get(pk) is not None
                    and str(rec.get(pk)).strip()
                    and str(rec.get(pk)).strip().lower() not in ("none", "null", "n/a")
                    for pk in primary_requested
                )
                if not has_primary:
                    # Drop orphaned rows (e.g. solitary carousel price with missing name/title)
                    continue

            # If multiple fields requested, discard rows with only 1 solitary value (unless user only requested 1 field)
            if len(task.fields) > 1 and len(populated_fields) <= 1:
                continue

            grounded.append(rec)

        return grounded

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
                grounded = self._filter_grounded_records(conformed, task)
                return ExtractionResult(
                    records=grounded,
                    strategy_used=ExtractionStrategyEnum.PASSTHROUGH.value,
                    fallback_used=False,
                    metadata={"record_count": len(grounded)},
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

            # Strategy A: LLM if explicitly requested in schema
            if effective_schema.strategy == ExtractionStrategyEnum.LLM and self.llm_extractor:
                logger.debug("Executing LLM extraction strategy as configured in schema")
                llm_records = await self.llm_extractor.extract_async(page, task, effective_schema)
                if llm_records:
                    page_records = llm_records
                    page_strategy = ExtractionStrategyEnum.LLM.value
                    if schema is None:
                        page_fallback = True

            # Strategy B: CSS / XPath if base selector exists
            if not page_records and effective_schema.base_selector:
                if effective_schema.base_selector.startswith("/") or effective_schema.base_selector.startswith(".//"):
                    logger.debug("Attempting deterministic XPath extraction")
                    records = self.xpath_extractor.extract(page, effective_schema)
                    if records:
                        page_records = records
                        page_strategy = ExtractionStrategyEnum.XPATH.value
                else:
                    logger.debug("Attempting deterministic CSS extraction")
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
                        logger.debug(f"Deterministic Table extractor extracted {len(table_records)} record(s)")
                        page_records = table_records
                        page_strategy = ExtractionStrategyEnum.TABLE.value
                    else:
                        logger.debug("Table extraction returned incomplete field coverage; cascading to next strategy")

            # Strategy C: Deterministic Repeating Grid / Card Extractor
            if not page_records and page.html:
                card_records = self.grid_card_extractor.extract(page.html, target_fields=task.fields, base_url=page.url)
                if card_records:
                    has_card_coverage = all(
                        any(r.get(f) is not None for r in card_records)
                        for f in task.fields
                    )
                    if has_card_coverage or not self.llm_extractor:
                        logger.debug(f"Deterministic GridCard extractor extracted {len(card_records)} card record(s)")
                        page_records = card_records
                        page_strategy = "grid_card"
                    else:
                        logger.debug("GridCard extraction returned incomplete coverage; cascading to next strategy")

            # Strategy D: Regex Extraction for pattern fields
            if not page_records:
                regex_records = self.regex_extractor.extract(page, effective_schema)
                if regex_records:
                    has_coverage = all(
                        any(r.get(f) is not None for r in regex_records)
                        for f in task.fields
                    )
                    if has_coverage or not self.llm_extractor:
                        logger.debug(f"Deterministic Regex extractor extracted {len(regex_records)} record(s)")
                        page_records = regex_records
                        page_strategy = ExtractionStrategyEnum.REGEX.value
                    else:
                        logger.debug("Regex extraction returned incomplete field coverage; cascading to LLM extraction")

            # Strategy E: LLM Extraction Fallback with Qwen3:8b
            if not page_records and self.llm_extractor:
                logger.debug("Cascading to LLM extraction strategy (Qwen3:8b)")
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
        conformed = self._enforce_task_schema(
            deduped, task, base_url=pages[0].url if pages else None
        )

        # Conditional Fallback: If requested fields are missing or record count is insufficient for a listing request
        missing_fields = [
            f for f in task.fields
            if not any(r.get(f) is not None for r in conformed)
        ]
        is_insufficient_records = (
            (getattr(task, "is_list", False) or (getattr(task, "min_records", None) and task.min_records > 1))
            and len(conformed) < (getattr(task, "min_records", None) or 2)
        )

        if (missing_fields or not conformed or is_insufficient_records) and self.browser_executor and pages:
            reason = f"missing fields: {missing_fields}" if missing_fields else f"insufficient records ({len(conformed)} extracted for listing request)"
            logger.debug(
                f"Primary extraction incomplete ({reason}). "
                "Initiating conditional fallback child link discovery..."
            )
            discovered_child_urls: list[str] = []
            for p in pages:
                if p.html and p.url:
                    links = self.link_discovery.extract_candidate_links(
                        html=p.html,
                        base_url=p.url,
                        query_keywords=task.fields + ([task.objective] if task.objective else []),
                        max_links=3,
                    )
                    for link in links:
                        if link not in discovered_child_urls:
                            discovered_child_urls.append(link)

            if discovered_child_urls:
                logger.debug(
                    f"Discovered {len(discovered_child_urls)} candidate child URL(s). "
                    f"Crawling child pages in parallel: {discovered_child_urls}"
                )
                child_crawl_tasks = [self.browser_executor.crawl(url=u) for u in discovered_child_urls]
                child_results = await asyncio.gather(*child_crawl_tasks)
                child_pages = [
                    RawPage(url=cr.url, html=cr.html, text=getattr(cr, "text", None), raw_payload=getattr(cr, "extracted_data", None))
                    for cr in child_results if cr and getattr(cr, "html", None)
                ]

                if child_pages:
                    child_extracted_records: list[dict[str, Any]] = []
                    for cp in child_pages:
                        c_records: list[dict[str, Any]] = []
                        # Strategy 1: Table
                        t_records = self.table_extractor.extract(cp, effective_schema)
                        if t_records and any(any(r.get(f) is not None for r in t_records) for f in missing_fields):
                            c_records = t_records
                        # Strategy 2: Regex
                        if not c_records:
                            r_records = self.regex_extractor.extract(cp, effective_schema)
                            if r_records and any(any(r.get(f) is not None for r in r_records) for f in missing_fields):
                                c_records = r_records
                        # Strategy 3: LLM
                        if not c_records and self.llm_extractor:
                            llm_recs = await self.llm_extractor.extract_async(cp, task, effective_schema)
                            if llm_recs:
                                c_records = llm_recs
                        child_extracted_records.extend(c_records)

                    # Fuse child records into conformed records
                    if conformed and child_extracted_records:
                        if is_insufficient_records:
                            combined = conformed + child_extracted_records
                            conformed = self._enforce_task_schema(
                                self.deduplicator.deduplicate(combined),
                                task,
                                base_url=pages[0].url if pages else None,
                            )
                        else:
                            for conf_rec in conformed:
                                for ch_rec in child_extracted_records:
                                    for mf in missing_fields:
                                        if conf_rec.get(mf) is None and ch_rec.get(mf) is not None:
                                            conf_rec[mf] = ch_rec[mf]
                    elif child_extracted_records:
                        conformed = self._enforce_task_schema(
                            self.deduplicator.deduplicate(child_extracted_records),
                            task,
                            base_url=pages[0].url if pages else None,
                        )

        grounded_records = self._filter_grounded_records(conformed, task)

        return ExtractionResult(
            records=grounded_records,
            strategy_used=dominant_strategy,
            fallback_used=any_fallback,
            metadata={"record_count": len(grounded_records)},
        )

