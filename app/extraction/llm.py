import json
from typing import Any, Optional

from app.config.logging import get_logger
from app.extraction.chunking import ContentChunker
from app.extraction.schema import ExtractionSchema, RawPage
from app.extraction.semantic import SemanticFilter
from app.llm.base import LLMClient
from app.llm.ollama_client import clean_markdown_fences
from app.models.schemas import ScrapingTask

logger = get_logger("EXTRACTION_LLM")

LLM_EXTRACTION_SYSTEM_PROMPT = """You are an expert data extraction assistant.
Extract structured records from the provided content strictly conforming to the requested schema.

Rules:
1. Return a single JSON array containing objects matching the requested fields.
2. Only extract information explicitly stated in the content.
3. If a field value is missing or not found, set its value to null.
4. Do NOT hallucinate or infer missing facts.
5. Do NOT include markdown code blocks or explanations outside the JSON array.
6. Preserve exact field names requested.
"""


class LLMExtractor:
    """LLM-driven structured entity and table extraction using Qwen3:8b."""

    def __init__(
        self,
        llm_client: LLMClient,
        chunker: Optional[ContentChunker] = None,
        semantic_filter: Optional[SemanticFilter] = None,
    ):
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
        prompt_lines.append("\nExtract the matching structured records as a JSON array of objects:")
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
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON records: {e}")
            return []

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

        all_records: list[dict[str, Any]] = []

        for chunk_text in selected_chunks:
            prompt = self._build_prompt(chunk_text, task, schema)
            try:
                raw_response = await self.llm_client.invoke(
                    prompt=prompt,
                    system=LLM_EXTRACTION_SYSTEM_PROMPT,
                    json_mode=True,
                )
                records = self._parse_llm_records(raw_response)
                all_records.extend(records)
            except Exception as e:
                logger.error(f"Error during LLM chunk extraction: {e}")

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
            except Exception as e:
                logger.error(f"Error during sync LLM chunk extraction: {e}")

        return all_records
