import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from leadfinder.config.settings import Settings
from leadfinder.llm.base import LLMClient
from leadfinder.main import app
from leadfinder.models.schemas import ScrapingRequest


class MockLLMClient(LLMClient):
    """Mock LLM client returning configurable responses."""

    def __init__(self, response_text: str | None = None, model: str = "qwen3:8b"):
        self._model = model
        self.response_text = response_text or json.dumps(
            {
                "objective": "Scrape product catalog for pricing and ratings",
                "target_urls": ["https://example.com/products"],
                "fields": ["product_name", "price", "rating"],
                "output_schema": {
                    "product_name": "string",
                    "price": "string",
                    "rating": "number",
                },
                "max_records": 50,
                "constraints": ["Extract in-stock items only"],
                "source_requirements": ["JavaScript rendering needed"],
            }
        )
        self.invoked_prompts: list[str] = []

    @property
    def model_name(self) -> str:
        return self._model

    async def invoke(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        self.invoked_prompts.append(prompt)
        return self.response_text

    def invoke_sync(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        self.invoked_prompts.append(prompt)
        return self.response_text

    async def check_health(self) -> dict[str, Any]:
        return {
            "available": True,
            "model_name": self._model,
            "model_installed": True,
            "available_models": [self._model],
        }


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        OLLAMA_BASE_URL="http://localhost:11434",
        OLLAMA_MODEL="qwen3:8b",
        OLLAMA_TIMEOUT_SECONDS=10.0,
        BRIGHTDATA_API_KEY=None,
        BRIGHTDATA_COLLECTOR_ID=None,
        APP_ENV="test",
        LOG_LEVEL="DEBUG",
    )


@pytest.fixture
def mock_llm_client() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture
def sample_scraping_request() -> ScrapingRequest:
    return ScrapingRequest(
        query="Scrape products from https://example.com/products and extract name, price and rating",
        max_records=50,
        target_urls=["https://example.com/products"],
    )


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)
