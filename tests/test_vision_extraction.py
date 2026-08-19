import pytest
from unittest.mock import AsyncMock, MagicMock
from app.extraction.vision import VisionTextExtractor


@pytest.mark.asyncio
async def test_vision_text_extractor_extracts_verbatim_text():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"response": "Special Price: $19.99\nModel: ABC-123"},
        )
    )

    extractor = VisionTextExtractor(model_name="gemma4:e2b", client=mock_client)
    text = await extractor.extract_text_from_image_base64("dummy_base64_data")
    assert "Special Price: $19.99" in text
    assert "Model: ABC-123" in text


@pytest.mark.asyncio
async def test_vision_text_extractor_handles_empty_or_failure():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection failed"))

    extractor = VisionTextExtractor(model_name="gemma4:e2b", client=mock_client)
    text = await extractor.extract_text_from_image_base64("bad_data")
    assert text == ""
