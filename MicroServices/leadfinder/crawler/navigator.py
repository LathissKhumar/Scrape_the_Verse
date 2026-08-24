"""Interactive navigator engine for autonomous on-site searching, form entry, and action execution."""

import logging

from playwright.async_api import Page

logger = logging.getLogger("CRAWLER_NAVIGATOR")


class InteractiveNavigatorEngine:
    """Locates search interfaces on arbitrary websites, types queries, and submits searches."""

    SEARCH_INPUT_SELECTORS = [
        "input[type='search']",
        "input[name='q']",
        "input[name='query']",
        "input[name='search']",
        "input[name='field-keywords']",
        "input[placeholder*='search' i]",
        "input[placeholder*='find' i]",
        "input[placeholder*='explore' i]",
        "#twotabsearchtextbox",
        "input.Pke_EE",
        "input._3704LK",
        "input[data-testid*='search']",
        "input[aria-label*='search' i]",
        "input.nav-search-input",
        "textarea[name='q']",
    ]

    SEARCH_BUTTON_SELECTORS = [
        "button[type='submit']",
        "input[type='submit']",
        "#nav-search-submit-button",
        "button._2iLD__",
        "button[aria-label*='search' i]",
        "button:has(svg)",
    ]

    async def search(
        self,
        page: Page,
        query: str,
        submit_via: str = "enter",
        wait_timeout_ms: int = 5000,
    ) -> bool:
        """Locate search input on the page, fill query, and submit search."""
        if not query or not query.strip():
            return False

        logger.info(f"Navigating search input for query='{query}'...")

        # 1. Locate search input element
        search_input = None
        for selector in self.SEARCH_INPUT_SELECTORS:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    search_input = elem
                    logger.debug(f"Found search input matching selector: '{selector}'")
                    break
            except Exception as e:
                logger.debug(f"Selector query failed for '{selector}': {e}")

        if not search_input:
            logger.warning("Could not find a valid search input on the page.")
            return False

        try:
            # 2. Focus and fill query
            if hasattr(search_input, "click"):
                try:
                    await search_input.click(timeout=2000)
                except Exception:
                    pass

            if hasattr(search_input, "fill"):
                await search_input.fill(query)
            elif hasattr(search_input, "type"):
                await search_input.type(query)

            # 3. Submit search
            if submit_via.lower() == "button":
                submitted = False
                for btn_sel in self.SEARCH_BUTTON_SELECTORS:
                    try:
                        btn = await page.query_selector(btn_sel)
                        if btn:
                            await btn.click(timeout=2000)
                            submitted = True
                            break
                    except Exception:
                        pass
                if not submitted and hasattr(search_input, "press"):
                    await search_input.press("Enter")
            else:
                if hasattr(search_input, "press"):
                    await search_input.press("Enter")

            # 4. Wait for search results DOM update
            if hasattr(page, "wait_for_load_state"):
                try:
                    await page.wait_for_load_state(
                        "domcontentloaded", timeout=wait_timeout_ms
                    )
                except Exception:
                    pass

            if hasattr(page, "wait_for_timeout"):
                try:
                    await page.wait_for_timeout(1000)
                except Exception:
                    pass

            logger.info(f"Successfully submitted search for '{query}'.")
            return True

        except Exception as e:
            logger.error(f"Error while interacting with search input: {e}")
            return False
