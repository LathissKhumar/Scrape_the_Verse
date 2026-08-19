# Conditional Fallback Link Crawling Design Specification

## 1. Goal
When a primary target URL does not contain all desired fields or yields low field coverage / empty records, the system conditionally discovers relevant candidate sub-links from the primary page's rendered DOM, crawls the top matching child pages in parallel, and merges the missing attributes into the final structured output.

## 2. Architecture & Data Flow

```
[Primary URL Scraping] (Playwright Chromium)
         │
         ▼
[Initial Structured Extraction] (Regex / Table / LLM)
         │
         ├──► Field Coverage >= 0.85 & Validated
         │       └──► Return complete records (Fast & Zero sub-link overhead)
         │
         └──► Coverage Incomplete (e.g. specifications=None or missing fields)
                 │
                 ▼
         [LinkDiscoveryEngine] (app/crawler/link_discovery.py)
            - Extracts <a href="..."> from primary page HTML
            - Resolves relative URLs to absolute URLs
            - Filters for same-domain relevance & keyword matching (spec, detail, product)
            - Drops noise links (/login, /cart, /privacy, #, mailto:)
                 │
                 ▼
         [Parallel Child Crawls] (Playwright Chromium)
            - Executes async child page crawls via BrowserExecutor
                 │
                 ▼
         [Unified Child Field Extraction & Record Merging]
            - Extracts missing fields from child pages
            - Merges parent + child fields into complete structured records
```

## 3. Key Components

### 3.1 `LinkDiscoveryEngine` (`app/crawler/link_discovery.py`)
* `extract_candidate_links(html: str, base_url: str, query_keywords: list[str], max_links: int = 5) -> list[str]`
* Scores and ranks links based on keyword relevance (`spec`, `detail`, `tech`, `features`, product slug matching).
* Enforces domain boundaries (SSRF and domain pinning).

### 3.2 `ScraperAgent` & `ExtractionEngine` Conditional Deep Crawl Hook
* In `ScraperAgent.execute(task)` or `ExtractionEngine.extract_async(...)`:
* When initial extraction has missing fields (`has_coverage is False` or `ValidationResult` degraded):
  * Invokes `LinkDiscoveryEngine` on the raw primary page.
  * If candidate child URLs are found, launches parallel crawls for top child links.
  * Feeds child pages to `ExtractionEngine` to extract and merge missing fields.

## 4. Verification Plan
* Automated unit tests for `LinkDiscoveryEngine` link resolution, domain scoping, and relevance ranking.
* Automated integration test verifying primary page + child page field fusion.
* Live CLI test on real pages.
