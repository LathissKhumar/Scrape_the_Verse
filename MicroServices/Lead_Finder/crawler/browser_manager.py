"""Async Playwright browser instance manager with context isolation, crash recovery, and lifecycle control."""

import asyncio
import logging

from leadfinder.crawler.config import CrawlerConfig
from leadfinder.crawler.proxy_provider import ProxyProvider
from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

logger = logging.getLogger("CRAWLER_BROWSER_MANAGER")


class BrowserManager:
    """Manages the lifecycle of async Playwright Chromium instances, isolated contexts, and auto-recovery."""

    def __init__(
        self,
        config: CrawlerConfig | None = None,
        proxy_provider: ProxyProvider | None = None,
    ):
        self.config = config or CrawlerConfig()
        self.proxy_provider = proxy_provider
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._lock = asyncio.Lock()
        self._pages_processed: int = 0

    async def get_browser(self) -> Browser:
        """Get or initialize the shared Chromium browser instance safely with crash detection."""
        async with self._lock:
            # Check for crash or disconnection
            is_valid = self._browser is not None
            if is_valid:
                try:
                    is_valid = self._browser.is_connected()
                except Exception:
                    is_valid = False

            if not is_valid:
                if self._browser is not None:
                    logger.warning(
                        "Chromium instance disconnected or crashed. Restarting fresh browser..."
                    )
                    try:
                        await self._browser.close()
                    except Exception:
                        pass
                    self._browser = None

                if self._playwright is None:
                    self._playwright = await async_playwright().start()

                proxy_cfg = (
                    self.proxy_provider.get_proxy() if self.proxy_provider else None
                )
                logger.debug(
                    f"Launching Playwright Chromium (headless={self.config.headless})..."
                )
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
                self._pages_processed = 0

            return self._browser

    async def create_isolated_context(
        self, block_media: bool | None = None
    ) -> BrowserContext:
        """Create an isolated browser context with anti-bot stealth, viewport, locale, and optional asset blocking."""
        # Check if periodic recycling is due
        should_recycle = False
        async with self._lock:
            self._pages_processed += 1
            if self._pages_processed > self.config.recycle_after_pages:
                should_recycle = True

        if should_recycle:
            logger.info(
                f"Recycling Playwright Chromium after {self.config.recycle_after_pages} pages to prevent memory degradation..."
            )
            await self.close()

        browser = await self.get_browser()
        context = await browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
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

        # Apply deep anti-detection evasions (Canvas, WebGL, AudioContext, permissions, navigator)
        try:
            from playwright_stealth import Stealth

            stealth = Stealth()
            await stealth.apply_stealth_async(context)
        except Exception as stealth_err:
            logger.debug(f"playwright-stealth application notice: {stealth_err}")

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

        # Optional asset route blocking (images, media, fonts) for high performance
        effective_block_media = (
            block_media if block_media is not None else self.config.block_media
        )
        if effective_block_media:
            await context.route(
                "**/*.{png,jpg,jpeg,webp,gif,svg,mp4,webm,woff,woff2,ttf,eot,ico}",
                lambda route: asyncio.create_task(route.abort()),
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
            self._pages_processed = 0
            logger.info("Playwright browser instance closed cleanly.")
