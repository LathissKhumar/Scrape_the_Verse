"""LLM-driven structured entity and table extraction using local models."""

import asyncio
import json
import re
from typing import Any, Optional

from app.config.logging import get_logger
from app.extraction.chunking import ContentChunker
from app.extraction.schema import ExtractionSchema, RawPage
from app.extraction.semantic import SemanticFilter
from app.llm.base import LLMClient
from app.llm.ollama_client import clean_markdown_fences
from app.models.schemas import ScrapingTask

logger = get_logger("LLM_EXTRACTOR")

LLM_EXTRACTION_SYSTEM_PROMPT = """You are an expert data extraction assistant.
Extract structured records from the provided content strictly conforming to the requested schema.

Rules:
1. Return a single JSON array containing objects matching the requested fields.
2. Only extract information explicitly and directly stated in the Source Content.
3. If a field value is not found or not mentioned in the Source Content, set its value to null.
4. Do NOT hallucinate, invent, extrapolate, or use outside pre-trained knowledge.
5. Extract exact names, facts, and descriptions as they appear in the content.
6. For price/cost fields, extract only genuine numerical prices (e.g. '$199', '₹97,000', '19000'). Do NOT extract marketing slogans or button texts like 'free', 'get quote', 'best price', or 'सही दाम पर' as prices. If no real price is stated, return null.
7. Do NOT include markdown code blocks or explanations outside the JSON array.
8. Preserve exact field names requested.
"""

_OBJECT_REGEX = re.compile(r"\{[^{}]+\}")
_DIGIT_REGEX = re.compile(r"\d")
_NULL_STRING_VALUES = {"null", "none", "", "n/a", "unknown"}
_INVALID_PRICE_SLOGANS = {
    "free",
    "on request",
    "call for price",
    "get quote",
    "सही दाम पर",
    "best price",
    "fair price",
    "contact us",
    "ask price",
    "free quote",
    "n/a",
}


class LLMExtractor:
    """LLM-driven structured entity and table extraction using Qwen3:8b."""

    def __init__(
        self,
        llm_client: LLMClient,
        chunker: Optional[ContentChunker] = None,
        semantic_filter: Optional[SemanticFilter] = None,
    ) -> None:
        self.llm_client = llm_client
        self.chunker = chunker or ContentChunker(chunk_size=2500, chunk_overlap=200)
        self.semantic_filter = semantic_filter or SemanticFilter(top_k=3)

    def _build_prompt(
        self,
        content_snippet: str,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> str:
        fields_str = json.dumps(task.fields)
        output_schema_str = json.dumps(task.output_schema or {})

        prompt_lines = [
            f"Extraction Objective: {task.objective}",
            f"Requested Fields: {fields_str}",
        ]
        if task.output_schema:
            prompt_lines.append(f"Expected Output Schema: {output_schema_str}")

        prompt_lines.append(f"\nSource Content:\n\"\"\"\n{content_snippet}\n\"\"\"")
        prompt_lines.append(
            "\nExtract structured records strictly matching the Source Content above as a JSON array of objects. "
            "Only include facts directly stated in the text:"
        )
        return "\n".join(prompt_lines)

    def _parse_llm_records(self, raw_output: str) -> list[dict[str, Any]]:
        cleaned = clean_markdown_fences(raw_output).strip()
        if not cleaned:
            return []

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
            elif isinstance(parsed, dict):
                # If wrapped in a key like {"records": [...]}
                for val in parsed.values():
                    if isinstance(val, list):
                        return [item for item in val if isinstance(item, dict)]
                return [parsed]
            return []
        except Exception:
            # Resilient fallback 1: auto-close unclosed brackets
            for fix in ("]", "}", "}\n]", "\"]}"):
                try:
                    parsed = json.loads(cleaned + fix)
                    if isinstance(parsed, list):
                        return [item for item in parsed if isinstance(item, dict)]
                    elif isinstance(parsed, dict):
                        return [parsed]
                except Exception:
                    pass

            # Resilient fallback 2: match individual JSON objects
            extracted_objs: list[dict[str, Any]] = []
            for obj_match in _OBJECT_REGEX.finditer(cleaned):
                try:
                    obj = json.loads(obj_match.group(0))
                    if isinstance(obj, dict):
                        extracted_objs.append(obj)
                except Exception:
                    pass

            if extracted_objs:
                return extracted_objs

            logger.debug("Could not parse LLM output as structured JSON records")
            return []

    def _consolidate_entity_records(
        self,
        records: list[dict[str, Any]],
        fields: list[str],
    ) -> list[dict[str, Any]]:
        """Consolidate multiple chunk extraction outputs into a single comprehensive entity record."""
        if not records:
            return []
        if len(records) == 1:
            return records

        unified: dict[str, Any] = {}
        for f in fields:
            best_val = None
            for r in records:
                val = r.get(f)
                if val is not None and str(val).strip().lower() not in _NULL_STRING_VALUES:
                    # Choose richest non-empty value
                    if best_val is None or len(str(val)) > len(str(best_val)):
                        best_val = val
            unified[f] = best_val

        # Preserve any non-requested keys that contain rich extracted data
        for r in records:
            for k, v in r.items():
                if k not in unified and v is not None and str(v).strip().lower() not in _NULL_STRING_VALUES:
                    unified[k] = v

        return [unified]

    def _sanitize_records(
        self,
        records: list[dict[str, Any]],
        fields: list[str],
    ) -> list[dict[str, Any]]:
        """Sanitize field values, converting marketing slogans in price/cost fields into None."""
        for r in records:
            for f in fields:
                val = r.get(f)
                if val is not None and ("price" in f.lower() or "cost" in f.lower()):
                    if isinstance(val, str):
                        clean_str = val.strip().lower()
                        # If string has no digits or matches a slogan without price, nullify it
                        if not _DIGIT_REGEX.search(clean_str) or clean_str in _INVALID_PRICE_SLOGANS:
                            r[f] = None
        return records

    async def extract_async(
        self,
        content: str | RawPage,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> list[dict[str, Any]]:
        """Asynchronously extract structured records using LLM with semantic chunk filtering."""
        text_str = content.get_primary_content() if isinstance(content, RawPage) else str(content)
        if not text_str or not text_str.strip():
            return []

        # If text is raw HTML, strip boilerplate and extract clean structured text
        if "<html" in text_str.lower() or "<body" in text_str.lower() or "<div" in text_str.lower() or "<p" in text_str.lower():
            try:
                from app.extraction.cleaner import clean_html
                cleaned = clean_html(text_str)
                if cleaned and len(cleaned.strip()) > 20:
                    text_str = cleaned
            except Exception:
                pass

        chunks = self.chunker.chunk_text(text_str)
        if not chunks:
            return []

        # If multiple chunks, rank them semantically against the task objective & fields
        if len(chunks) > 1:
            query_str = f"{task.objective} {' '.join(task.fields)}"
            ranked = self.semantic_filter.rank_and_filter(chunks, query=query_str, top_k=3)
            selected_chunks = [c for c, _ in ranked] if ranked else chunks[:3]
        else:
            selected_chunks = chunks

        async def _extract_chunk(chunk_text: str) -> list[dict[str, Any]]:
            prompt = self._build_prompt(chunk_text, task, schema)
            try:
                raw_response = await self.llm_client.invoke(
                    prompt=prompt,
                    system=LLM_EXTRACTION_SYSTEM_PROMPT,
                    json_mode=True,
                )
                return self._parse_llm_records(raw_response)
            except Exception as error:
                logger.error(f"Error during LLM chunk extraction: {error}")
                return []

        chunk_results = await asyncio.gather(*[_extract_chunk(c) for c in selected_chunks])
        all_records: list[dict[str, Any]] = []
        for records in chunk_results:
            all_records.extend(records)

        # If multiple chunks were extracted for a single entity request, consolidate chunk fragments into one record
        if len(selected_chunks) > 1 and not getattr(task, "is_list", False) and (not schema or not schema.base_selector):
            all_records = self._consolidate_entity_records(all_records, task.fields)

        all_records = self._sanitize_records(all_records, task.fields)
        return all_records

    def extract(
        self,
        content: str | RawPage,
        task: ScrapingTask,
        schema: Optional[ExtractionSchema] = None,
    ) -> list[dict[str, Any]]:
        """Synchronously extract structured records using LLM."""
        text_str = content.get_primary_content() if isinstance(content, RawPage) else str(content)
        if not text_str or not text_str.strip():
            return []

        # If text is raw HTML, strip boilerplate and extract clean structured text
        if "<html" in text_str.lower() or "<body" in text_str.lower() or "<div" in text_str.lower() or "<p" in text_str.lower():
            try:
                from app.extraction.cleaner import clean_html
                cleaned = clean_html(text_str)
                if cleaned and len(cleaned.strip()) > 20:
                    text_str = cleaned
            except Exception:
                pass

        chunks = self.chunker.chunk_text(text_str)
        if not chunks:
            return []

        if len(chunks) > 1:
            query_str = f"{task.objective} {' '.join(task.fields)}"
            ranked = self.semantic_filter.rank_and_filter(chunks, query=query_str, top_k=3)
            selected_chunks = [c for c, _ in ranked] if ranked else chunks[:3]
        else:
            selected_chunks = chunks

        all_records: list[dict[str, Any]] = []

        for chunk_text in selected_chunks:
            prompt = self._build_prompt(chunk_text, task, schema)
            try:
                raw_response = self.llm_client.invoke_sync(
                    prompt=prompt,
                    system=LLM_EXTRACTION_SYSTEM_PROMPT,
                    json_mode=True,
                )
                records = self._parse_llm_records(raw_response)
                all_records.extend(records)
            except Exception as error:
                logger.error(f"Error during sync LLM chunk extraction: {error}")

        # If multiple chunks were extracted for a single entity request, consolidate chunk fragments into one record
        if len(selected_chunks) > 1 and not getattr(task, "is_list", False) and (not schema or not schema.base_selector):
            all_records = self._consolidate_entity_records(all_records, task.fields)

        all_records = self._sanitize_records(all_records, task.fields)
        return all_records

