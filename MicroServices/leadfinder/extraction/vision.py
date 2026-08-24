"""Vision-based text and data extraction using multimodal models."""

import httpx

from leadfinder.config.logging import get_logger
from leadfinder.config.settings import get_settings

logger = get_logger("VISION_EXTRACTOR")

VISION_OCR_SYSTEM_PROMPT = """You are a high-precision OCR text extractor.
Extract all visible text, numbers, prices, labels, and tabular data from this image verbatim.
DO NOT describe what the image looks like.
Output ONLY the raw extracted text and data found in the image."""


class VisionTextExtractor:
    """Extracts text data from page images using Ollama vision models (e.g. gemma4:e2b)."""

    def __init__(
        self,
        model_name: str = "gemma4:e2b",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = get_settings()
        self.model_name = model_name
        self.base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self.client = client

    async def extract_text_from_image_base64(self, image_base64: str) -> str:
        """Extract text from base64-encoded image string using gemma4:e2b."""
        payload = {
            "model": self.model_name,
            "prompt": "Extract all text and data from this image verbatim.",
            "system": VISION_OCR_SYSTEM_PROMPT,
            "images": [image_base64],
            "stream": False,
        }
        endpoint = f"{self.base_url}/api/generate"
        try:
            if self.client:
                resp = await self.client.post(endpoint, json=payload)
            else:
                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    resp = await http_client.post(endpoint, json=payload)

            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as error:
            logger.warning(f"Vision OCR extraction failed: {error}")

        return ""
