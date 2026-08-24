"""Navigation agent orchestrating on-site search, pagination traversal, and detail link harvesting."""

import logging

from leadfinder.agents.base import BaseAgent
from leadfinder.crawler.browser_manager import BrowserManager
from leadfinder.crawler.link_harvester import LinkHarvesterEngine
from leadfinder.crawler.navigation_planner import NavigationPlanner
from leadfinder.crawler.navigator import InteractiveNavigatorEngine
from leadfinder.crawler.pagination_walker import PaginationWalkerEngine
from leadfinder.models.schemas import ScrapingTask

logger = logging.getLogger("NAVIGATION_AGENT")


class NavigationAgent(BaseAgent):
    """Orchestrates autonomous on-site searching, faceted navigation, and detail link harvesting."""

    def __init__(
        self,
        browser_manager: BrowserManager | None = None,
        navigator_engine: InteractiveNavigatorEngine | None = None,
        link_harvester: LinkHarvesterEngine | None = None,
        pagination_walker: PaginationWalkerEngine | None = None,
        planner: NavigationPlanner | None = None,
    ):
        self.browser_manager = browser_manager or BrowserManager()
        self.navigator_engine = navigator_engine or InteractiveNavigatorEngine()
        self.link_harvester = link_harvester or LinkHarvesterEngine()
        self.pagination_walker = pagination_walker or PaginationWalkerEngine()
        self.planner = planner or NavigationPlanner()

    async def run(self, task: ScrapingTask) -> list[str]:
        """Execute autonomous navigation to search, traverse pagination, and harvest detail URLs."""
        if not task.is_search and not task.deep_crawl:
            logger.info(
                f"Direct crawl request. Bypassing navigation for {len(task.target_urls)} URL(s)."
            )
            return list(task.target_urls)

        nav_plan = self.planner.plan_navigation(task)
        root_url = nav_plan["root_url"]
        search_query = nav_plan["search_keyword"]
        max_links = nav_plan["max_links"]
        max_pages = nav_plan["max_pagination_pages"]

        logger.info(
            f"Starting navigation session on '{root_url}' (search='{search_query}', target_links={max_links})..."
        )

        context = await self.browser_manager.create_isolated_context()
        page = await context.new_page()

        harvested_urls: list[str] = []
        try:
            # 1. Navigate to Root Site
            logger.debug(f"Opening root URL: {root_url}")
            await page.goto(
                root_url,
                wait_until="domcontentloaded",
                timeout=self.browser_manager.config.timeout_ms,
            )

            # Allow dynamic JS content to hydrate
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(1000)

            # 2. Perform On-Site Search if specified
            if task.is_search and search_query:
                search_success = await self.navigator_engine.search(
                    page, query=search_query
                )
                if not search_success:
                    logger.warning(
                        f"On-site search for '{search_query}' did not locate search bar. Proceeding with current page."
                    )

            # 3. Harvest links with pagination loop
            for page_idx in range(max_pages):
                current_html = await page.content()
                current_url = page.url

                new_links = self.link_harvester.harvest_detail_links(
                    html=current_html,
                    base_url=current_url,
                    max_links=max_links,
                )

                for link in new_links:
                    if link not in harvested_urls:
                        harvested_urls.append(link)
                        if len(harvested_urls) >= max_links:
                            break

                logger.info(
                    f"Navigation Page {page_idx + 1}: Accumulated {len(harvested_urls)} / {max_links} detail URLs."
                )

                if len(harvested_urls) >= max_links:
                    break

                # Advance pagination if more links needed
                advanced = await self.pagination_walker.advance_page(page)
                if not advanced:
                    logger.info("Pagination exhausted or no Next control found.")
                    break

        except Exception as e:
            logger.error(f"Error during navigation execution on '{root_url}': {e}")
        finally:
            await context.close()

        # If navigation found no detail links, fall back to root URL
        if not harvested_urls:
            logger.warning(
                f"Navigation harvested 0 links. Falling back to original target URLs: {task.target_urls}"
            )
            return list(task.target_urls)

        logger.info(
            f"Navigation completed successfully. Yielding {len(harvested_urls)} detail page(s) for scraping."
        )
        return harvested_urls
