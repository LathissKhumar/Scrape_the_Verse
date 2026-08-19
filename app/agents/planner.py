import json
import re
from typing import Any, Optional
from uuid import uuid4

from app.agents.base import BaseAgent
from app.llm.base import LLMClient
from app.llm.exceptions import LLMInvocationError
from app.models.schemas import ScrapingRequest, ScrapingTask, validate_http_url

PLANNER_SYSTEM_PROMPT = """You are a scraping task planner.
Convert the user's plain-language scraping request into a structured scraping task.

The user may provide:
- URLs (either explicitly in the target_urls list or inside the query text)
- scraping objective
- fields to extract
- record limits
- constraints
- source requirements

Strict Rules:
1. Never invent URLs. Only use URLs provided by the user.
2. Never invent facts.
3. Never search the web.
4. Never perform scraping.
5. Preserve user-provided URLs verbatim.
6. When a user asks to find or extract an item/product (e.g. 'Find the phone with price X'), always include the product/item name (e.g. 'product_name' or 'title') along with the requested attributes (e.g. 'price').
7. Preserve requested fields accurately.
8. Do not add unrelated fields unless requested.
9. Do not guess missing information.
9. Never invent generic constraints: Do NOT add 'respect robots.txt', 'follow terms of service', or legal rules unless the user explicitly requested them. If none requested, constraints must be [].
10. Never invent source requirements: Do NOT add 'user-agent header required' or headers unless the user explicitly requested them. If none requested, source_requirements must be [].
11. Never invent max_records: Set max_records to null unless the user explicitly specified a record limit.
12. Return valid JSON only.
13. Create an output_schema when field types are obvious (e.g. {"field1": "string", "price": "string", "rating": "number"}).
14. Do NOT include a task_id field in your JSON output.

Your output must be a single JSON object with the following format:
{
  "objective": "Clear description of the user's scraping objective",
  "target_urls": ["https://example.com/page"],
  "fields": ["field1", "field2"],
  "output_schema": {"field1": "string", "field2": "string"},
  "max_records": null,
  "constraints": [],
  "source_requirements": []
}"""

URL_REGEX = re.compile(r"https?://[^\s,;\"'<>()\[\]{}]+", re.IGNORECASE)

GENERIC_HALLUCINATIONS = [
    "respect robots.txt",
    "robots.txt",
    "terms of service",
    "user-agent header",
    "user-agent header required",
    "follow website terms",
]


def extract_urls_from_text(text: str) -> list[str]:
    """Extract valid HTTP/HTTPS URLs from plain text."""
    found = URL_REGEX.findall(text)
    valid_urls: list[str] = []
    for u in found:
        cleaned = u.rstrip(".,;:)")
        try:
            valid = validate_http_url(cleaned)
            if valid not in valid_urls:
                valid_urls.append(valid)
        except ValueError:
            continue
    return valid_urls


def sanitize_constraints(items: list[str], user_query: str) -> list[str]:
    """Filter out hallucinated boilerplate constraints not mentioned in the user query."""
    user_lower = user_query.lower()
    cleaned = []
    for item in items:
        if not isinstance(item, str):
            continue
        item_lower = item.lower().strip()
        # If it's a known generic boilerplate hallucination and not in query, drop it
        if any(h in item_lower for h in GENERIC_HALLUCINATIONS) and item_lower not in user_lower:
            continue
        if item.strip():
            cleaned.append(item.strip())
    return cleaned


class ScrapingPlannerAgent(BaseAgent):
    """Planner Agent that converts plain-language requests into structured ScrapingTasks."""

    def __init__(self, llm_client: LLMClient):
        super().__init__(name="PLANNER")
        self.llm_client = llm_client

    def _build_user_prompt(self, request: ScrapingRequest, known_urls: list[str]) -> str:
        prompt_lines = [
            f"User Query: {request.query}",
        ]
        if known_urls:
            urls_str = json.dumps(known_urls)
            prompt_lines.append(f"User Supplied Target URLs: {urls_str}")
        if request.max_records is not None:
            prompt_lines.append(f"Requested Max Records: {request.max_records}")
        prompt_lines.append("\nGenerate the structured JSON task representation.")
        return "\n".join(prompt_lines)

    def _merge_and_validate_urls(
        self,
        request: ScrapingRequest,
        llm_urls: list[str],
        query_urls: list[str],
    ) -> list[str]:
        """Merge URLs from request, query, and LLM output, preserving verbatim and filtering invalid/invented."""
        merged: list[str] = []

        allowed_user_urls = list(request.target_urls)
        for u in query_urls:
            if u not in allowed_user_urls:
                allowed_user_urls.append(u)

        for u in allowed_user_urls:
            if u not in merged:
                merged.append(u)

        for u in llm_urls:
            if isinstance(u, str):
                cleaned = u.strip().rstrip(".,;:)")
                if cleaned in allowed_user_urls and cleaned not in merged:
                    merged.append(cleaned)

        return merged

    def _parse_llm_json(self, raw_output: str) -> dict[str, Any]:
        """Parse raw LLM output into a dictionary."""
        try:
            data = json.loads(raw_output)
            if not isinstance(data, dict):
                raise ValueError(f"LLM JSON root is not an object: {type(data)}")
            return data
        except Exception as e:
            self.logger.error(f"Failed to parse LLM JSON: {raw_output}")
            raise LLMInvocationError(f"Planner LLM returned invalid JSON: {e}") from e

    async def plan_async(
        self,
        request: ScrapingRequest,
        task_id: Optional[str] = None,
    ) -> ScrapingTask:
        """Asynchronously plan and generate a ScrapingTask from a ScrapingRequest."""
        effective_task_id = task_id or str(uuid4())
        self.logger.info(f"Planning scraping task for task_id: {effective_task_id}")

        query_urls = extract_urls_from_text(request.query)
        known_urls = list(request.target_urls)
        for u in query_urls:
            if u not in known_urls:
                known_urls.append(u)

        user_prompt = self._build_user_prompt(request, known_urls)

        raw_output = await self.llm_client.invoke(
            prompt=user_prompt,
            system=PLANNER_SYSTEM_PROMPT,
            json_mode=True,
        )

        parsed_data = self._parse_llm_json(raw_output)

        llm_urls = parsed_data.get("target_urls", [])
        if not isinstance(llm_urls, list):
            llm_urls = []
        final_urls = self._merge_and_validate_urls(request, llm_urls, query_urls)

        # Prioritize request.max_records; if not specified in request, check if mentioned in query
        max_records = request.max_records
        if max_records is None:
            # Only use LLM parsed max_records if a number or limit keyword was in query
            candidate = parsed_data.get("max_records")
            if isinstance(candidate, int) and candidate > 0:
                if any(char.isdigit() for char in request.query):
                    max_records = candidate

        objective = parsed_data.get("objective") or request.query.strip()
        fields = parsed_data.get("fields") or []
        output_schema = parsed_data.get("output_schema") or None

        raw_constraints = parsed_data.get("constraints") or []
        raw_source_reqs = parsed_data.get("source_requirements") or []
        constraints = sanitize_constraints(raw_constraints, request.query)
        source_requirements = sanitize_constraints(raw_source_reqs, request.query)

        task = ScrapingTask(
            task_id=effective_task_id,
            objective=objective,
            target_urls=final_urls,
            fields=fields,
            output_schema=output_schema,
            max_records=max_records,
            constraints=constraints,
            source_requirements=source_requirements,
        )

        self.logger.info(
            f"Successfully generated ScrapingTask {task.task_id} with {len(task.target_urls)} URLs and {len(task.fields)} fields"
        )
        return task

    def plan(
        self,
        request: ScrapingRequest,
        task_id: Optional[str] = None,
    ) -> ScrapingTask:
        """Synchronously plan and generate a ScrapingTask from a ScrapingRequest."""
        effective_task_id = task_id or str(uuid4())
        self.logger.info(f"Planning scraping task synchronously for task_id: {effective_task_id}")

        query_urls = extract_urls_from_text(request.query)
        known_urls = list(request.target_urls)
        for u in query_urls:
            if u not in known_urls:
                known_urls.append(u)

        user_prompt = self._build_user_prompt(request, known_urls)

        raw_output = self.llm_client.invoke_sync(
            prompt=user_prompt,
            system=PLANNER_SYSTEM_PROMPT,
            json_mode=True,
        )

        parsed_data = self._parse_llm_json(raw_output)

        llm_urls = parsed_data.get("target_urls", [])
        if not isinstance(llm_urls, list):
            llm_urls = []
        final_urls = self._merge_and_validate_urls(request, llm_urls, query_urls)

        max_records = request.max_records
        if max_records is None:
            candidate = parsed_data.get("max_records")
            if isinstance(candidate, int) and candidate > 0:
                if any(char.isdigit() for char in request.query):
                    max_records = candidate

        objective = parsed_data.get("objective") or request.query.strip()
        fields = parsed_data.get("fields") or []
        output_schema = parsed_data.get("output_schema") or None

        raw_constraints = parsed_data.get("constraints") or []
        raw_source_reqs = parsed_data.get("source_requirements") or []
        constraints = sanitize_constraints(raw_constraints, request.query)
        source_requirements = sanitize_constraints(raw_source_reqs, request.query)

        task = ScrapingTask(
            task_id=effective_task_id,
            objective=objective,
            target_urls=final_urls,
            fields=fields,
            output_schema=output_schema,
            max_records=max_records,
            constraints=constraints,
            source_requirements=source_requirements,
        )

        self.logger.info(
            f"Successfully generated ScrapingTask {task.task_id} with {len(task.target_urls)} URLs and {len(task.fields)} fields"
        )
        return task
