# Autonomous Goal-Driven Web Navigation & Deep Crawling Subsystem — Technical Design

## 1. Overview
The goal of this subsystem is to evolve `Scrape_the_Verse` from a direct static URL scraper into an **Autonomous Goal-Driven Web Navigator and Deep Crawler**. Given a site root (e.g. `https://www.flipkart.com`, `https://www.amazon.com`) or a natural language query with implicit search requirements, the system will autonomously locate search interfaces, submit queries, apply category/faceted filters, harvest item detail page links, and perform parallel bounded crawls to extract full product specifications and reviews.

---

## 2. Architecture & LangGraph State Machine

### 2.1 State Graph Workflow
The LangGraph state machine will integrate `NavigationAgent` as an intelligent pre-crawl routing node:

```
[START] ──► [planner] ──► [should_navigate?]
                              /            \
                       YES (Search/Deep)   NO (Direct URL)
                             /                \
                       [navigation]       [scraper]
                            │                 │
                            └────────►────────┘
                                      │
                                [extraction]
                                      │
                                [validation]
                                      │
                               [should_repair?]
                                 /          \
                         NO (Healthy)     YES (Degraded/Broken)
                             /                  \
                          [END]              [diagnosis]
                                                 │
                                              [healing] ──► [END]
```

### 2.2 Routing Criteria (`should_navigate`)
* If `state["task"].is_search` is `True` OR `state["task"].deep_crawl` is `True`: Route to `navigation_node`.
* Otherwise: Route directly to `scraper_node` (preserving 100% backward-compatibility for direct URL scrapes).

---

## 3. Component Breakdown

### 3.1 Agents & Sub-Agents
1. **`NavigationAgent`** ([`app/agents/navigation.py`](file:///c:/Projects/Scrape_the_Verse/app/agents/navigation.py)):
   * Parent agent responsible for executing navigation goals, coordinating search interactions, managing pagination cycles, and aggregating target URLs for deep crawling.
2. **`NavigationPlanner`** ([`app/crawler/navigation_planner.py`](file:///c:/Projects/Scrape_the_Verse/app/crawler/navigation_planner.py)):
   * Sub-agent using LLM/heuristics to parse navigation goals, search terms, and filter rules from user queries (e.g., `brand="Redmi"`, `sort="price_low_to_high"`).

### 3.2 Deterministic Sub-Engines
1. **`InteractiveNavigatorEngine`** ([`app/crawler/navigator.py`](file:///c:/Projects/Scrape_the_Verse/app/crawler/navigator.py)):
   * Locates search input fields using a prioritized selector strategy:
     1. `input[type="search"]`, `input[name*="q"]`, `input[name*="search"]`, `input[placeholder*="search" i]`
     2. `#twotabsearchtextbox`, `.nav-search-input`, `input.Pke_EE`, `input._3704LK`
     3. Fallback: Vision/LLM agent inspection if DOM heuristics fail.
   * Types search terms with natural typing delay, dismisses autocomplete popups, and triggers submission via `Enter` key or search button click.
2. **`LinkHarvesterEngine`** ([`app/crawler/link_harvester.py`](file:///c:/Projects/Scrape_the_Verse/app/crawler/link_harvester.py)):
   * Inspects catalog/search results pages to harvest canonical item detail URLs (`/p/itm...`, `/dp/...`, `/product/...`, `/item/...`, `a[data-id]`).
   * Normalizes relative URLs to absolute HTTP/HTTPS links and deduplicates results.
3. **`PaginationWalkerEngine`** ([`app/crawler/pagination_walker.py`](file:///c:/Projects/Scrape_the_Verse/app/crawler/pagination_walker.py)):
   * Traverses pagination via "Next" button detection (`a[rel="next"]`, `.pagination .next`, `button:has-text("Next")`, `a:has-text("Next")`) or dynamic scroll-to-bottom for infinite scrolling catalogs until target count (`max_detail_pages`) is met.

---

## 4. Data Models & State Schema

### 4.1 `ScrapingTask` Extensions ([`app/models/schemas.py`](file:///c:/Projects/Scrape_the_Verse/app/models/schemas.py))
```python
class ScrapingTask(BaseModel):
    task_id: str
    objective: str
    target_urls: list[str]
    fields: list[str]
    is_list: bool = True
    # New Navigation & Deep Crawl Fields:
    is_search: bool = False
    search_keyword: Optional[str] = None
    deep_crawl: bool = False
    max_detail_pages: int = 20
    filters: dict[str, Any] = Field(default_factory=dict)
```

### 4.2 `ScrapingGraphState` Extensions ([`app/graph/state.py`](file:///c:/Projects/Scrape_the_Verse/app/graph/state.py))
```python
class ScrapingGraphState(TypedDict, total=False):
    task_id: str
    original_user_query: str
    target_urls: list[str]
    task_plan: Optional[ScrapingTask]
    navigation_result: Optional[dict[str, Any]]
    raw_pages: list[RawPage]
    extracted_data: Optional[ExtractionResult]
    validation_result: Optional[ValidationResult]
    ...
```

---

## 5. End-to-End Execution Flow

1. **User Query Input**:
   `"Search redmi on flipkart and provide name, price, specifications, and reviews for top 10 items"`
2. **`ScrapingPlannerAgent`**:
   * Extracts site root: `https://www.flipkart.com`
   * Sets `is_search = True`, `search_keyword = "redmi"`, `deep_crawl = True`, `max_detail_pages = 10`.
   * Sets fields: `["product_name", "price", "specifications", "rating", "reviews"]`.
3. **`NavigationAgent`**:
   * Opens `https://www.flipkart.com` with `playwright-stealth`.
   * `InteractiveNavigatorEngine` finds the search bar, types `"redmi"`, presses Enter.
   * Waits for search results grid to render.
   * `LinkHarvesterEngine` collects 10 product detail URLs (`https://www.flipkart.com/redmi-.../p/itm...`).
4. **`ScraperAgent`**:
   * Scrapes all 10 product detail pages concurrently using `asyncio.Semaphore(10)`.
5. **`ExtractionEngine`**:
   * Extracts deep specifications, title, price, and customer reviews from each product detail page.
6. **`ValidationAgent`**:
   * Validates field coverage (100% on detail pages), verifies types, and returns clean structured dataset.

---

## 6. Verification & Testing Strategy

### Unit Tests ([`tests/test_navigation_and_deep_crawling.py`](file:///c:/Projects/Scrape_the_Verse/tests/test_navigation_and_deep_crawling.py))
1. `test_interactive_navigator_finds_search_input`: Mock DOM with search inputs, verify correct selector matching.
2. `test_link_harvester_extracts_product_links`: Mock catalog HTML, verify canonical product URLs extracted.
3. `test_pagination_walker_advances_pages`: Verify next button clicking logic.
4. `test_navigation_agent_end_to_end`: Verify planner ➔ navigation ➔ link harvest flow in graph.
5. Full regression test across test suite (`pytest tests/ -v`).
