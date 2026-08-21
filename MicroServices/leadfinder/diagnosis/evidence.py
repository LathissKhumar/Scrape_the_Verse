from typing import Any, Optional
from bs4 import BeautifulSoup

from leadfinder.extraction.chunking import ContentChunker
from leadfinder.extraction.semantic import SemanticFilter
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult


class DiagnosisEvidenceBuilder:
    """Assembles a compact, targeted diagnostic evidence package for the Diagnosis Agent."""

    def __init__(
        self,
        chunker: Optional[ContentChunker] = None,
        semantic_filter: Optional[SemanticFilter] = None,
    ):
        self.chunker = chunker or ContentChunker(chunk_size=1200, chunk_overlap=150)
        self.semantic_filter = semantic_filter or SemanticFilter(top_k=2)

    def extract_relevant_html_snippets(
        self,
        raw_html: str,
        affected_fields: list[str],
        objective: str,
    ) -> list[str]:
        """Extract focused HTML snippets or semantic chunks relevant to failing fields."""
        if not raw_html or not raw_html.strip():
            return []

        # If html is small, return directly
        if len(raw_html) <= 2500:
            return [raw_html]

        try:
            soup = BeautifulSoup(raw_html, "html.parser")
            # Remove scripts and styles to reduce noise
            for tag in soup(["script", "style", "svg", "noscript"]):
                tag.decompose()

            body = soup.find("body") or soup
            body_text = body.get_text(separator="\n", strip=True)

            # Chunk cleaned text
            chunks = self.chunker.chunk_text(body_text)
            if not chunks:
                return []

            query = f"{objective} {' '.join(affected_fields)}"
            ranked = self.semantic_filter.rank_and_filter(chunks, query=query, top_k=2)
            return [c for c, _ in ranked]
        except Exception:
            return [raw_html[:2000]]

    def build_evidence(
        self,
        task: ScrapingTask,
        validation_result: ValidationResult,
        raw_results: Optional[Any] = None,
        extracted_results: Optional[list[dict[str, Any]]] = None,
        scraper_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Compile a concise, structured evidence package."""
        affected_fields: list[str] = []
        for field_name, metric in validation_result.field_metrics.items():
            if metric.coverage < 0.70 or metric.placeholder_count > 0:
                affected_fields.append(field_name)

        # Inspect raw results representation
        raw_str = ""
        if isinstance(raw_results, str):
            raw_str = raw_results
        elif isinstance(raw_results, list) and raw_results and isinstance(raw_results[0], dict):
            raw_str = raw_results[0].get("html", "") or str(raw_results[0])
        elif isinstance(raw_results, dict):
            raw_str = raw_results.get("html", "") or str(raw_results)

        relevant_snippets = self.extract_relevant_html_snippets(
            raw_html=raw_str,
            affected_fields=affected_fields,
            objective=task.objective,
        )

        return {
            "task_id": task.task_id,
            "objective": task.objective,
            "target_urls": task.target_urls,
            "requested_fields": task.fields,
            "output_schema": task.output_schema,
            "validation_status": validation_result.status,
            "health_score": validation_result.health_score,
            "quality_score": validation_result.quality_score,
            "record_count": validation_result.record_count,
            "expected_record_count": validation_result.expected_record_count,
            "affected_fields": affected_fields,
            "field_coverages": {
                k: v.coverage for k, v in validation_result.field_metrics.items()
            },
            "duplicate_rate": validation_result.duplicate_metrics.duplicate_rate,
            "failures": [f.model_dump() for f in validation_result.failures],
            "anomalies": validation_result.anomalies,
            "raw_content_available": bool(raw_str.strip()),
            "raw_content_length": len(raw_str),
            "relevant_snippets": relevant_snippets,
            "sample_extracted_records": (extracted_results or [])[:3],
        }
