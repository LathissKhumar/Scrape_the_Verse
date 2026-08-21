import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from leadfinder.config.settings import Settings
from leadfinder.llm.exceptions import (
    LLMConnectionError,
    LLMInvocationError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)
from leadfinder.llm.ollama_client import OllamaClient, clean_markdown_fences


def test_clean_markdown_fences():
    # JSON fence
    fenced_json = "```json\n{\"key\": \"value\"}\n```"
    assert clean_markdown_fences(fenced_json) == '{"key": "value"}'

    # Generic fence
    fenced_generic = "```\n{\"key\": \"value\"}\n```"
    assert clean_markdown_fences(fenced_generic) == '{"key": "value"}'

    # Plain text
    plain = '{"key": "value"}'
    assert clean_markdown_fences(plain) == '{"key": "value"}'


@pytest.mark.asyncio
async def test_ollama_client_invoke_success(monkeypatch):
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    mock_response = httpx.Response(
        status_code=200,
        json={"response": "```json\n{\"objective\": \"test\"}\n```"},
        request=httpx.Request("POST", "http://localhost:11434/api/generate"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await client.invoke("Test prompt", json_mode=True)
        assert result == '{"objective": "test"}'


def test_ollama_client_invoke_sync_success():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    mock_response = httpx.Response(
        status_code=200,
        json={"response": "{\"objective\": \"test_sync\"}"},
        request=httpx.Request("POST", "http://localhost:11434/api/generate"),
    )

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response
        result = client.invoke_sync("Test prompt")
        assert result == '{"objective": "test_sync"}'


@pytest.mark.asyncio
async def test_ollama_client_connection_error():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(LLMConnectionError):
            await client.invoke("Test prompt")


@pytest.mark.asyncio
async def test_ollama_client_timeout_error():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timed out")):
        with pytest.raises(LLMTimeoutError):
            await client.invoke("Test prompt")


@pytest.mark.asyncio
async def test_ollama_client_model_not_found():
    client = OllamaClient(Settings(OLLAMA_MODEL="nonexistent-model"))

    mock_response = httpx.Response(
        status_code=404,
        text="model not found",
        request=httpx.Request("POST", "http://localhost:11434/api/generate"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(LLMModelNotFoundError):
            await client.invoke("Test prompt")


@pytest.mark.asyncio
async def test_ollama_client_check_health_success():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    mock_response = httpx.Response(
        status_code=200,
        json={"models": [{"name": "qwen3:8b"}, {"name": "llama3:latest"}]},
        request=httpx.Request("GET", "http://localhost:11434/api/tags"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        health = await client.check_health()
        assert health["available"] is True
        assert health["model_installed"] is True
        assert health["model_name"] == "qwen3:8b"


@pytest.mark.asyncio
async def test_ollama_client_check_health_model_missing():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    mock_response = httpx.Response(
        status_code=200,
        json={"models": [{"name": "llama3:latest"}]},
        request=httpx.Request("GET", "http://localhost:11434/api/tags"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        health = await client.check_health()
        assert health["available"] is True
        assert health["model_installed"] is False


@pytest.mark.asyncio
async def test_ollama_client_check_health_connection_error():
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Unreachable")):
        health = await client.check_health()
        assert health["available"] is False
        assert health["model_installed"] is False
        assert "Cannot connect" in health.get("error", "")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_ollama_integration():
    """Optional integration test against live local Ollama."""
    client = OllamaClient(Settings(OLLAMA_MODEL="qwen3:8b"))
    health = await client.check_health()
    if not health.get("available"):
        pytest.skip("Local Ollama is not running.")
    assert health["available"] is True
    assert health["model_installed"] is True

    prompt = "Return a JSON object with a single field 'status' set to 'ok'."
    res = await client.invoke(prompt, json_mode=True)
    assert "status" in res
