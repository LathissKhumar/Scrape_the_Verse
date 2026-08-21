import asyncio
import base64
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from playwright.async_api import async_playwright
from app.extraction.vision import VisionTextExtractor

async def test_vision():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Create an HTML banner with clear text, price, and specs
        html_content = """
        <html>
        <body style="margin:0; background:white; font-family:sans-serif;">
            <div id="banner" style="width:400px; padding:20px; border:2px solid black; background:#f0f8ff;">
                <h1 style="color:#333; margin:0 0 10px 0;">NVIDIA RTX 4090 OC</h1>
                <p style="font-size:18px; margin:5px 0;"><strong>Price:</strong> $1,599.99</p>
                <p style="font-size:14px; margin:5px 0;"><strong>Memory:</strong> 24GB GDDR6X</p>
                <p style="font-size:14px; margin:5px 0;"><strong>Status:</strong> In Stock - Ready to Ship</p>
                <p style="font-size:12px; color:#666; margin:5px 0;">SKU: GPU-NV-4090-24G</p>
            </div>
        </body>
        </html>
        """
        await page.set_content(html_content)
        banner_element = await page.query_selector("#banner")
        screenshot_bytes = await banner_element.screenshot()
        await browser.close()

        img_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        print(f"[INFO] Captured screenshot: {len(img_b64)} b64 chars")

        # Let's test standard prompt directly via Ollama
        import httpx
        payload = {
            "model": "gemma4:e2b",
            "prompt": "What text is written in this image?",
            "images": [img_b64],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post("http://localhost:11434/api/generate", json=payload)
            print("Direct Ollama response:", resp.json().get("response"))

if __name__ == "__main__":
    asyncio.run(test_vision())
