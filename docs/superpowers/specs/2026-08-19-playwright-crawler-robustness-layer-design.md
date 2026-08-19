# Playwright-Powered Web Crawling Robustness Layer Design Spec

**Date:** 2026-08-19  
**Status:** Approved for Implementation  
**Topic:** Compliant, Production-Grade Playwright Browser Execution & Robustness Layer inspired by Crawl4AI

---

## 1. Executive Summary & Goals

This specification defines the architecture for a production-grade, compliant web crawling robustness layer in `Scrape_the_Verse`.

### Core Goals:
1. **Real Chromium Automation**: Execute JavaScript, hydration routines, dynamic prices, and SPAs using async Playwright.
2. **Strict Compliance & Responsibility**: Respect website rate limits, concurrency bounds, HTTP 429 Retry-After, and circuit breaking.
3. **Transparent Block Detection**: Explicitly detect HTTP 403, 429, CAPTCHAs, and security challenge pages (`BlockType`), classifying failures without deceptive bypass techniques.
4. **SSRF & Security Isolation**: Validate URLs, block private/internal subnets and metadata services, restrict to `http/https`, and enforce sandboxed browser lifecycles.
5. **Action Plan Execution**: Support structured declarative actions (`wait_for`, `click`, `scroll`, `fill`, `select`, `extract`) validated against strict allowlists (no arbitrary JS execution).
6. **Seamless LangGraph Integration**: Connect directly into the Planner, Scraper, Extraction, Validation, and Self-Healing pipeline.

---

## 2. System Architecture & Components

```
                          ScrapingTask (Planner)
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     UrlSecurityValidator      │ ── SSRF / Private IP / Protocol Gate
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ DomainRateLimiter & Circuit   │ ── Token bucket per domain + Circuit Breaker
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     BrowserInstanceManager    │ ── Async Playwright Chromium Pool
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    ActionPlanExecutor         │ ── Whitelisted declarative action execution
                    │    (navigate, wait, scroll)   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        BlockDetector          │ ── Classifies HTTP 403, 429, CAPTCHA, Challenge
                    └───────┬───────────────┬───────┘
                            │               │
                     [Is Blocked?]          │
                      /           \         │
                    YES            NO       ▼
                    /                \  [CrawlResult (HTML / DOM / Timing)]
                   ▼                  ▼
       [BlockType Failure]       [Extraction Engine (CSS/XPath/LLM)]
                   │                  │
                   ▼                  ▼
     [Self-Healing Fallback /    [Validation & Health Engine]
      Bright Data Escalation]
```

---

## 3. Module Breakdown

### A. `app/crawler/url_validator.py`
- `UrlSecurityValidator`:
  - Enforces `http` and `https` schemes only.
  - Resolves domain to IP; blocks private IPv4/IPv6 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`, `::1`, link-local).
  - Configurable allowlist for local tests.

### B. `app/crawler/rate_limiter.py` & `circuit_breaker.py`
- `DomainRateLimiter`: Per-domain token bucket rate limiting (configurable requests/second, concurrency limit, and exponential backoff with jitter).
- `DomainCircuitBreaker`: Tracks consecutive failure/block counts per domain. Opens circuit if threshold is reached to prevent abusive hammering.

### C. `app/crawler/browser_manager.py` & `browser_executor.py`
- `BrowserManager`: Manages async Playwright lifecycle (singleton Chromium process, connection pooling, isolated context creation per crawl with clean storage/cookies).
- `BrowserExecutor`: Executes crawl requests in an isolated context with human-compatible viewports (1920x1080), standard locale (`en-US`), realistic non-deceptive User-Agent, and configurable timeouts.

### D. `app/crawler/action_models.py` & `action_executor.py`
- Declarative Pydantic action models: `NavigateAction`, `WaitForAction`, `ClickAction`, `FillAction`, `SelectAction`, `ScrollAction`, `ExtractAction`.
- Strict validation allowlist: rejects arbitrary JS code execution.

### E. `app/crawler/block_detector.py` & `result_models.py`
- `BlockType` Enum: `NONE`, `RATE_LIMITED`, `ACCESS_DENIED`, `CAPTCHA`, `SECURITY_CHALLENGE`, `AUTH_REQUIRED`, `ROBOTS_RESTRICTED`, `UNKNOWN`.
- `BlockDetector`: Inspects status codes, response headers, and DOM text/signatures to identify challenges, returning `CrawlResult` with diagnostic metadata.

### F. `app/crawler/proxy_provider.py`
- `ProxyProvider` interface: supports explicitly configured proxies for legitimate routing, health tracking, and non-circumvention rules.

### G. Integration with `ScraperAgent` & LangGraph
- `ScraperAgent`: Uses `BrowserExecutor` as the native dynamic engine when browser execution is needed or when static HTTP encounters dynamic rendering.
- `workflow.py`: Automatically routes `CrawlResult` block failures into the Self-Healing Orchestrator to choose compliant fallbacks (e.g. Bright Data collector, cache, or graceful escalation).

---

## 4. Testing Strategy
1. Unit tests for `UrlSecurityValidator` (SSRF checks, private IP blocking).
2. Unit tests for `BlockDetector` (403, 429, CAPTCHA DOM detection).
3. Unit tests for `DomainRateLimiter` & `DomainCircuitBreaker` (concurrency, backoff).
4. Unit tests for `ActionPlanExecutor` (valid actions vs disallowed code rejection).
5. Integration tests for `BrowserExecutor` with real async Playwright Chromium.
