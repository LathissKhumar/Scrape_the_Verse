"""
Unified LLM Factory for Lead Manager.
"""

import json
from typing import Any, Dict, List, Optional
import httpx
from ..config.logging import get_logger
from ..config.settings import Settings, get_settings

logger = get_logger("LLMFactory")


class LLMClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.ollama_url = f"{self.settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        self.ollama_model = self.settings.OLLAMA_MODEL
        self.timeout = self.settings.OLLAMA_TIMEOUT_SECONDS
        self.gemini_key = self.settings.GEMINI_API_KEY
        self.gemini_model = self.settings.GEMINI_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # 1. Try local Ollama
        try:
            payload: Dict[str, Any] = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
            }
            if system_prompt:
                payload["system"] = system_prompt

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.ollama_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                logger.warning(f"Ollama returned HTTP {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Ollama call failed ({e}). Attempting fallback if configured...")

        # 2. Try Gemini Cloud Fallback
        if self.gemini_key:
            try:
                gemini_url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.gemini_model}:generateContent?key={self.gemini_key}"
                )
                gemini_payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt or ''}\n\n{prompt}"}]}]
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(gemini_url, json=gemini_payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        candidates = res_json.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                    logger.warning(f"Gemini API returned HTTP {resp.status_code}: {resp.text}")
            except Exception as ge:
                logger.error(f"Gemini fallback failed: {ge}")

        return ""

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        full_system = (system_prompt or "") + "\nYou MUST return valid, parseable JSON with no extra markdown formatting or backticks."
        raw = await self.generate(prompt=prompt, system_prompt=full_system)
        if not raw:
            return None

        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

        try:
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e} | Raw: {raw[:200]}")
            return None
