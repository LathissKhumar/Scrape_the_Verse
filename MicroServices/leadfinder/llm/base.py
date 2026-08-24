from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    """Provider-agnostic interface for Large Language Model invocations."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the configured model identifier."""

    @abstractmethod
    async def invoke(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        """Asynchronously invoke the LLM with a prompt and optional system instruction."""

    @abstractmethod
    def invoke_sync(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        """Synchronously invoke the LLM with a prompt and optional system instruction."""

    @abstractmethod
    async def check_health(self) -> dict[str, Any]:
        """Check provider connectivity and model availability without running inference."""
