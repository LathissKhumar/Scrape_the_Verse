"""Pagination walker engine advancing search and catalog pages via Next buttons or dynamic scroll."""

import asyncio
import logging
from typing import Optional
from playwright.async_api import Page

logger = logging.getLogger("CRAWLER_PAGINATION_WALKER")


class PaginationWalkerEngine:
    """Detects and advances pagination controls on search/catalog pages."""

    NEXT_BUTTON_SELECTORS = [
        "a[rel='next']",
        "a.s-pagination-next",
        "a._1LKTO3:has-text('Next')",
        "a._9QVEST:has-text('Next')",
        ".pagination .next a",
        ".pagination-next a",
        "li.next a",
        "a[aria-label*='next' i]",
        "button[aria-label*='next' i]",
        "a:has-text('Next')",
        "button:has-text('Next')",
        "a:has-text('›')",
        "a:has-text('»')",
    ]

    async def advance_page(
        self,
        page: Page,
        wait_timeout_ms: int = 4000,
    ) -> bool:
        """Locate Next button and click, or fall back to infinite scroll down."""
        logger.debug("Attempting to advance pagination...")

        # 1. Look for explicit Next Page button/link
        next_button = None
        for sel in self.NEXT_BUTTON_SELECTORS:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    next_button = elem
                    logger.info(f"Found Next page button matching: '{sel}'")
                    break
            except Exception:
                pass

        if next_button:
            try:
                if hasattr(next_button, "scroll_into_view_if_needed"):
                    await next_button.scroll_into_view_if_needed(timeout=2000)
                await next_button.click(timeout=3000)
                
                if hasattr(page, "wait_for_load_state"):
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=wait_timeout_ms)
                    except Exception:
                        pass
                if hasattr(page, "wait_for_timeout"):
                    await page.wait_for_timeout(1000)
                return True
            except Exception as e:
                logger.debug(f"Clicking next button failed: {e}")

        # 2. Fallback to dynamic scroll (infinite scroll catalogs)
        try:
            if hasattr(page, "evaluate"):
                await page.evaluate("window.scrollBy(0, window.innerHeight * 2);")
                if hasattr(page, "wait_for_timeout"):
                    await page.wait_for_timeout(1500)
                return True
        except Exception as e:
            logger.debug(f"Scroll fallback failed: {e}")

        return False
