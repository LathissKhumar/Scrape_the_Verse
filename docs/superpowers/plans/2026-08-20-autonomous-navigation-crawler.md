# Autonomous Goal-Driven Web Navigation & Deep Crawling Subsystem Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous goal-driven web navigation, on-site search, and deep detail-page crawling layer integrated into the LangGraph state machine with deterministic sub-engines and sub-agents.

**Architecture:** A LangGraph state machine with an intelligent `navigation_node` between `planner` and `scraper`. `NavigationAgent` coordinates on-site search (`InteractiveNavigatorEngine`), link harvesting (`LinkHarvesterEngine`), and pagination traversal (`PaginationWalkerEngine`), feeding harvested item detail URLs into `ScraperAgent` for parallel extraction.

**Tech Stack:** Python 3.10+, Playwright Async, BeautifulSoup4, LangGraph, Pydantic v2, Pytest.

**Spec:** [`docs/superpowers/specs/2026-08-20-autonomous-navigation-crawler-design.md`](file:///c:/Projects/Scrape_the_Verse/docs/superpowers/specs/2026-08-20-autonomous-navigation-crawler-design.md)

## Global Constraints
- Must preserve 100% backward compatibility for direct URL scraping queries.
- Bounded concurrency using existing `CrawlerConfig.max_concurrency` semaphore (default 10).
- All 219 existing unit tests must continue to pass without regressions.
- No new external heavyweight frameworks or breaking API changes.

---

### Task 1: Extend Data Schemas & Graph State

**Files:**
- Modify: `app/models/schemas.py`
- Modify: `app/graph/state.py`
- Test: `tests/test_navigation_schemas.py`

**Interfaces:**
- Consumes: `ScrapingTask`, `ScrapingGraphState`
- Produces: `is_search: bool`, `search_keyword: Optional[str]`, `deep_crawl: bool`, `max_detail_pages: int`, `filters: dict[str, Any]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_navigation_schemas.py
from app.models.schemas import ScrapingTask
from app.graph.state import ScrapingGraphState


def test_scraping_task_navigation_fields():
    task = ScrapingTask(
        task_id="t_nav_1",
        objective="Search redmi phones on flipkart",
        target_urls=["https://www.flipkart.com"],
        fields=["name", "price", "specs"],
        is_search=True,
        search_keyword="redmi",
        deep_crawl=True,
        max_detail_pages=15,
        filters={"brand": "Redmi"},
    )
    assert task.is_search is True
    assert task.search_keyword == "redmi"
    assert task.deep_crawl is True
    assert task.max_detail_pages == 15
    assert task.filters == {"brand": "Redmi"}
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_navigation_schemas.py -v`
Expected: FAIL with `extra fields not permitted` or missing attributes.

- [ ] **Step 3: Implement schema extensions**
Update `ScrapingTask` in `app/models/schemas.py` and `ScrapingGraphState` in `app/graph/state.py` with `is_search`, `search_keyword`, `deep_crawl`, `max_detail_pages`, and `filters`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_navigation_schemas.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/models/schemas.py app/graph/state.py tests/test_navigation_schemas.py
git commit -m "feat(schema): add navigation and deep crawl fields to ScrapingTask and state"
```

---

### Task 2: Build `InteractiveNavigatorEngine` (On-Site Search Sub-Engine)

**Files:**
- Create: `app/crawler/navigator.py`
- Test: `tests/test_navigator_engine.py`

**Interfaces:**
- Consumes: Playwright `Page`, `search_query: str`
- Produces: `async def search(page: Page, query: str, wait_timeout_ms: int = 5000) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_navigator_engine.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.crawler.navigator import InteractiveNavigatorEngine


@pytest.mark.asyncio
async def test_navigator_finds_and_types_search():
    mock_page = MagicMock()
    mock_input = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=mock_input)
    mock_page.wait_for_load_state = AsyncMock()

    navigator = InteractiveNavigatorEngine()
    success = await navigator.search(mock_page, query="redmi 13c")
    assert success is True
    mock_input.fill.assert_called_once_with("redmi 13c")
    mock_input.press.assert_called_once_with("Enter")
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_navigator_engine.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.crawler.navigator'`

- [ ] **Step 3: Implement `InteractiveNavigatorEngine`**
Create `app/crawler/navigator.py` with prioritized search bar selectors (`input[type="search"]`, `input[name*="q"]`, `#twotabsearchtextbox`, `.Pke_EE`, etc.), autocomplete popup dismissal, and search submission.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_navigator_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/crawler/navigator.py tests/test_navigator_engine.py
git commit -m "feat(crawler): implement InteractiveNavigatorEngine for on-site search"
```

---

### Task 3: Build `LinkHarvesterEngine` (Product Detail URL Extraction Sub-Engine)

**Files:**
- Create: `app/crawler/link_harvester.py`
- Test: `tests/test_link_harvester.py`

**Interfaces:**
- Consumes: `html: str`, `base_url: str`, `max_links: int = 20`
- Produces: `def harvest_detail_links(html: str, base_url: str, max_links: int = 20) -> list[str]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_link_harvester.py
from app.crawler.link_harvester import LinkHarvesterEngine


def test_link_harvester_extracts_product_detail_links():
    html = """
    <html><body>
      <div class="product"><a href="/redmi-13c/p/itm123">Redmi 13C</a></div>
      <div class="product"><a href="/redmi-note-13/p/itm456">Redmi Note 13</a></div>
      <div class="footer"><a href="/privacy-policy">Privacy</a></div>
    </body></html>
    """
    harvester = LinkHarvesterEngine()
    links = harvester.harvest_detail_links(
        html, base_url="https://www.flipkart.com", max_links=10
    )
    assert len(links) == 2
    assert "https://www.flipkart.com/redmi-13c/p/itm123" in links
    assert "https://www.flipkart.com/redmi-note-13/p/itm456" in links
    assert "https://www.flipkart.com/privacy-policy" not in links
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_link_harvester.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `LinkHarvesterEngine`**
Create `app/crawler/link_harvester.py` with canonical e-commerce product detail path heuristics (`/p/itm`, `/dp/`, `/product/`, `/item/`, `data-id`), base URL normalization, and deduplication.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_link_harvester.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/crawler/link_harvester.py tests/test_link_harvester.py
git commit -m "feat(crawler): implement LinkHarvesterEngine for item detail link extraction"
```

---

### Task 4: Build `PaginationWalkerEngine` (Pagination & Infinite Scroll Sub-Engine)

**Files:**
- Create: `app/crawler/pagination_walker.py`
- Test: `tests/test_pagination_walker.py`

**Interfaces:**
- Consumes: Playwright `Page`
- Produces: `async def advance_page(page: Page) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pagination_walker.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.crawler.pagination_walker import PaginationWalkerEngine


@pytest.mark.asyncio
async def test_pagination_walker_clicks_next():
    mock_page = MagicMock()
    mock_btn = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=mock_btn)
    mock_page.wait_for_load_state = AsyncMock()

    walker = PaginationWalkerEngine()
    advanced = await walker.advance_page(mock_page)
    assert advanced is True
    mock_btn.click.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_pagination_walker.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `PaginationWalkerEngine`**
Create `app/crawler/pagination_walker.py` detecting next buttons (`a[rel="next"]`, `.pagination .next`, `button:has-text("Next")`, `a:has-text("Next")`) and falling back to window scrolling for infinite scroll pages.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_pagination_walker.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/crawler/pagination_walker.py tests/test_pagination_walker.py
git commit -m "feat(crawler): implement PaginationWalkerEngine"
```

---

### Task 5: Build `NavigationPlanner` & `NavigationAgent` (Sub-Agent & Parent Agent)

**Files:**
- Create: `app/crawler/navigation_planner.py`
- Create: `app/agents/navigation.py`
- Test: `tests/test_navigation_agent.py`

**Interfaces:**
- Consumes: `ScrapingTask`, `BrowserManager`
- Produces: `async def run(task: ScrapingTask) -> list[str]` (returns harvested detail URLs)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_navigation_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.navigation import NavigationAgent
from app.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_navigation_agent_executes_search_and_harvest():
    mock_browser_mgr = MagicMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_page.content = AsyncMock(
        return_value="""
    <div class="product"><a href="/phone-1/p/itm1">Phone 1</a></div>
    <div class="product"><a href="/phone-2/p/itm2">Phone 2</a></div>
    """
    )
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser_mgr.create_isolated_context = AsyncMock(return_value=mock_context)

    mock_navigator = MagicMock()
    mock_navigator.search = AsyncMock(return_value=True)

    agent = NavigationAgent(
        browser_manager=mock_browser_mgr,
        navigator_engine=mock_navigator,
    )
    task = ScrapingTask(
        task_id="t1",
        objective="Search redmi",
        target_urls=["https://www.flipkart.com"],
        fields=["name", "price"],
        is_search=True,
        search_keyword="redmi",
        deep_crawl=True,
        max_detail_pages=2,
    )
    detail_urls = await agent.run(task)
    assert len(detail_urls) == 2
    assert "https://www.flipkart.com/phone-1/p/itm1" in detail_urls
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_navigation_agent.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `NavigationPlanner` and `NavigationAgent`**
Create `app/crawler/navigation_planner.py` and `app/agents/navigation.py` orchestrating navigation, search submission, pagination loop, and link harvesting.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_navigation_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/crawler/navigation_planner.py app/agents/navigation.py tests/test_navigation_agent.py
git commit -m "feat(agents): implement NavigationAgent and NavigationPlanner"
```

---

### Task 6: Update `ScrapingPlannerAgent` to Detect Search & Deep Crawl Intent

**Files:**
- Modify: `app/agents/planner.py`
- Test: `tests/test_planner_navigation_detection.py`

**Interfaces:**
- Consumes: User query string
- Produces: `ScrapingTask` with populated `is_search`, `search_keyword`, `deep_crawl`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_planner_navigation_detection.py
import pytest
from app.agents.planner import ScrapingPlannerAgent


@pytest.mark.asyncio
async def test_planner_detects_search_and_deep_crawl():
    planner = ScrapingPlannerAgent()
    task = await planner.plan_async(
        query="search redmi on flipkart and get specifications for top 10 items",
        target_urls=["https://www.flipkart.com"],
    )
    assert task.is_search is True
    assert "redmi" in (task.search_keyword or "").lower()
    assert task.deep_crawl is True
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_planner_navigation_detection.py -v`
Expected: FAIL with `assert task.is_search is True` failing.

- [ ] **Step 3: Update `ScrapingPlannerAgent`**
Enhance query parser in `app/agents/planner.py` to extract search keywords (`search X on Y`, `find X in Y`), deep crawl intentions (`specs`, `details`, `reviews`), and populate `is_search` and `deep_crawl`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_planner_navigation_detection.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/agents/planner.py tests/test_planner_navigation_detection.py
git commit -m "feat(planner): add search and deep crawl intent detection"
```

---

### Task 7: Integrate `navigation_node` into LangGraph State Machine

**Files:**
- Modify: `app/graph/workflow.py`
- Test: `tests/test_workflow_navigation_node.py`

**Interfaces:**
- Consumes: `ScrapingGraphState`
- Produces: Updated state with harvested detail URLs routed into `scraper_node`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_workflow_navigation_node.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.graph.workflow import create_scraping_workflow
from app.graph.state import ScrapingGraphState
from app.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_workflow_routes_to_navigation_node():
    mock_nav_agent = MagicMock()
    mock_nav_agent.run = AsyncMock(
        return_value=["https://example.com/p/1", "https://example.com/p/2"]
    )

    mock_planner = MagicMock()
    mock_planner.plan_async = AsyncMock(
        return_value=ScrapingTask(
            task_id="t_nav_graph",
            objective="Search products",
            target_urls=["https://example.com"],
            fields=["name", "price"],
            is_search=True,
            search_keyword="shoes",
            deep_crawl=True,
        )
    )

    wf = create_scraping_workflow(
        planner_agent=mock_planner,
        navigation_agent=mock_nav_agent,
    )
    state = {
        "task_id": "t_nav_graph",
        "original_user_query": "search shoes on example.com",
        "target_urls": ["https://example.com"],
    }
    final_state = await wf.ainvoke(state)
    mock_nav_agent.run.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_workflow_navigation_node.py -v`
Expected: FAIL with `create_scraping_workflow() got an unexpected keyword argument 'navigation_agent'`

- [ ] **Step 3: Update `app/graph/workflow.py`**
Add `navigation_node`, add `should_navigate` conditional router (`if task.is_search or task.deep_crawl: return "navigation"`), and connect graph edges: `planner -> should_navigate -> navigation -> scraper`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_workflow_navigation_node.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/graph/workflow.py tests/test_workflow_navigation_node.py
git commit -m "feat(graph): integrate navigation node into LangGraph state machine"
```

---

### Task 8: Full End-to-End Regression & Scalability Verification

**Files:**
- Create: `tests/test_navigation_e2e_integration.py`
- Test: Full Pytest Suite

- [ ] **Step 1: Write end-to-end integration test**
Verify full flow: Natural language search query ➔ Planner ➔ Navigation ➔ Search ➔ Harvest ➔ Parallel Scraper ➔ Extraction ➔ Validation.

- [ ] **Step 2: Run all tests in test suite**
Run: `pytest tests/ -v`
Expected: All 225+ tests pass with 0 errors.

- [ ] **Step 3: Final Commit**
```bash
git add tests/test_navigation_e2e_integration.py
git commit -m "test: add comprehensive end-to-end autonomous navigation tests"
```
