import re
from typing import Any

import httpx

from leadfinder.config.logging import get_logger
from leadfinder.config.settings import Settings, get_settings
from leadfinder.llm.base import LLMClient
from leadfinder.llm.exceptions import (
    LLMConnectionError,
    LLMInvocationError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)

logger = get_logger("LLM")


def clean_markdown_fences(content: str) -> str:
    """Strip markdown code block fences (```json ... ``` or ``` ... ```) from output."""
    trimmed = content.strip()
    # Match ```json ... ``` or ``` ... ```
    fence_pattern = re.compile(r"^```(?:json)?\s*\n?([\s\S]*?)\n?```$", re.IGNORECASE)
    match = fence_pattern.match(trimmed)
    if match:
        return match.group(1).strip()
    return trimmed


class OllamaClient(LLMClient):
    """Ollama implementation of LLMClient using httpx."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._base_url = self._settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = self._settings.OLLAMA_MODEL
        self._timeout = self._settings.OLLAMA_TIMEOUT_SECONDS

    @property
    def model_name(self) -> str:
        return self._model

    async def invoke(
        self,
        prompt: str | None = None,
        system: str | None = None,
        json_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        """Asynchronously generate a completion from Ollama."""
        prompt_text = prompt or kwargs.get("user_prompt") or ""
        system_text = system or kwargs.get("system_prompt")

        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt_text,
            "stream": False,
            "options": kwargs.get("options")
            or {
                "temperature": 0.1,
                "num_predict": 400,
            },
        }
        if system_text:
            payload["system"] = system_text
        if json_mode:
            payload["format"] = "json"

        endpoint = f"{self._base_url}/api/generate"
        logger.debug(f"Invoking Ollama model '{self._model}' via {endpoint}")

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(endpoint, json=payload)
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama at {self._base_url}: {e}")
            raise LLMConnectionError(
                f"Cannot connect to Ollama service at {self._base_url}. Ensure Ollama is running."
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out after {self._timeout} seconds")
            raise LLMTimeoutError(
                f"Ollama invocation timed out after {self._timeout}s."
            ) from e
        except httpx.RequestError as e:
            logger.error(f"HTTP request error when calling Ollama: {e}")
            raise LLMInvocationError(
                f"HTTP error communicating with Ollama: {e}"
            ) from e

        return self._process_response(response)

    def invoke_sync(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        """Synchronously generate a completion from Ollama."""
        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        if json_mode:
            payload["format"] = "json"

        endpoint = f"{self._base_url}/api/generate"
        logger.debug(
            f"Invoking Ollama model '{self._model}' synchronously via {endpoint}"
        )

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(endpoint, json=payload)
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama at {self._base_url}: {e}")
            raise LLMConnectionError(
                f"Cannot connect to Ollama service at {self._base_url}. Ensure Ollama is running."
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out after {self._timeout} seconds")
            raise LLMTimeoutError(
                f"Ollama invocation timed out after {self._timeout}s."
            ) from e
        except httpx.RequestError as e:
            logger.error(f"HTTP request error when calling Ollama: {e}")
            raise LLMInvocationError(
                f"HTTP error communicating with Ollama: {e}"
            ) from e

        return self._process_response(response)

    def _process_response(self, response: httpx.Response) -> str:
        """Validate and clean the raw Ollama HTTP response."""
        if response.status_code == 404:
            raise LLMModelNotFoundError(
                f"Model '{self._model}' was not found on Ollama server. Pull it using 'ollama pull {self._model}'."
            )
        elif response.status_code != 200:
            raise LLMInvocationError(
                f"Ollama returned HTTP error {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except Exception as e:
            raise LLMInvocationError(
                f"Malformed JSON response from Ollama: {response.text}"
            ) from e

        raw_response = data.get("response", "")
        cleaned = clean_markdown_fences(raw_response)
        return cleaned

    async def check_health(self) -> dict[str, Any]:
        """Check Ollama connectivity and whether the configured model is installed."""
        endpoint = f"{self._base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=min(self._timeout, 10.0)) as client:
                response = await client.get(endpoint)
        except httpx.ConnectError:
            return {
                "available": False,
                "model_name": self._model,
                "model_installed": False,
                "error": f"Cannot connect to Ollama at {self._base_url}",
            }
        except httpx.TimeoutException:
            return {
                "available": False,
                "model_name": self._model,
                "model_installed": False,
                "error": f"Ollama health check timed out at {self._base_url}",
            }
        except Exception as e:
            return {
                "available": False,
                "model_name": self._model,
                "model_installed": False,
                "error": str(e),
            }

        if response.status_code != 200:
            return {
                "available": False,
                "model_name": self._model,
                "model_installed": False,
                "error": f"Ollama returned status code {response.status_code}",
            }

        try:
            data = response.json()
            models = data.get("models", [])
            installed_models = [
                m.get("name") for m in models if isinstance(m, dict) and "name" in m
            ]
            # Match model name either exact (e.g. qwen3:8b) or prefix (qwen3:8b without tags)
            target = self._model.lower()
            model_installed = any(
                target == m.lower() or target == m.lower().split(":")[0]
                for m in installed_models
                if m
            )
            return {
                "available": True,
                "model_name": self._model,
                "model_installed": model_installed,
                "available_models": installed_models,
            }
        except Exception as e:
            return {
                "available": True,
                "model_name": self._model,
                "model_installed": False,
                "error": f"Failed to parse Ollama tags: {e}",
            }
