"""Async Playwright browser instance manager with context isolation and proper lifecycle control."""

import asyncio
import logging
from typing import Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright
from app.crawler.config import CrawlerConfig
from app.crawler.proxy_provider import ProxyProvider

logger = logging.getLogger("CRAWLER_BROWSER_MANAGER")


class BrowserManager:
    """Manages the lifecycle of async Playwright Chromium instances and isolated contexts."""

    def __init__(
        self,
        config: Optional[CrawlerConfig] = None,
        proxy_provider: Optional[ProxyProvider] = None,
    ):
        self.config = config or CrawlerConfig()
        self.proxy_provider = proxy_provider
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

    async def get_browser(self) -> Browser:
        """Get or initialize the shared Chromium browser instance safely."""
        async with self._lock:
            if self._browser is None or not self._browser.is_connected():
                if self._playwright is None:
                    self._playwright = await async_playwright().start()

                proxy_cfg = self.proxy_provider.get_proxy() if self.proxy_provider else None
                logger.info(f"Launching Playwright Chromium (headless={self.config.headless})...")
                self._browser = await self._playwright.chromium.launch(
                    headless=self.config.headless,
                    proxy=proxy_cfg,  # type: ignore
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-infobars",
                        "--disable-background-timer-throttling",
                        "--disable-backgrounding-occluded-windows",
                        "--disable-renderer-backgrounding",
                    ],
                )
            return self._browser

    async def create_isolated_context(self) -> BrowserContext:
        """Create an isolated browser context with anti-bot stealth, viewport, locale, and headers."""
        browser = await self.get_browser()
        context = await browser.new_context(
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            user_agent=self.config.user_agent,
            locale=self.config.locale,
            timezone_id=self.config.timezone_id,
            ignore_https_errors=False,
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        # Inject anti-bot evasion scripts
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """
        )
        context.set_default_timeout(self.config.timeout_ms)
        return context

    async def close(self) -> None:
        """Close browser and playwright session cleanly."""
        async with self._lock:
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None

            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None
            logger.info("Playwright browser instance closed cleanly.")
