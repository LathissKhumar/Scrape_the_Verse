# Playwright Web Crawling Robustness Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, compliant web crawling robustness layer in `app/crawler/` using async Playwright, rate limiting, circuit breaking, block detection, SSRF protection, and declarative action plans.

**Architecture:** A modular crawling subsystem under `app/crawler/` that validates URLs against SSRF, enforces domain rate/circuit policies, executes sandboxed Playwright Chromium contexts with human-compatible viewports and declarative action plans, detects block/challenge conditions with `BlockDetector`, and integrates into `ScraperAgent` and LangGraph self-healing.

**Tech Stack:** Python 3.10+, Playwright (async API), Pydantic v2, pytest, pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-08-19-playwright-crawler-robustness-layer-design.md`

## Global Constraints
- Do NOT implement CAPTCHA bypass, security challenge bypass, or deceptive fingerprint spoofing.
- Strict action execution allowlist (no arbitrary code execution from LLMs).
- Block private IPv4/IPv6 ranges and metadata endpoints (SSRF security).
- Respect HTTP 429 Retry-After headers and domain circuit breaking.
- Maintain full compatibility with existing Phases 1–5 test suites.

---

### Task 1: Environment & URL Security Validator

**Files:**
- Create: `app/crawler/url_validator.py`
- Modify: `requirements.txt`
- Test: `tests/test_url_validator.py`

**Interfaces:**
- Produces: `UrlSecurityValidator.validate_url(url: str, allow_private: bool = False) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_url_validator.py
import pytest
from app.crawler.url_validator import UrlSecurityValidator, SSRFSecurityError

def test_valid_public_urls():
    validator = UrlSecurityValidator()
    assert validator.validate_url("https://example.com/page") == "https://example.com/page"
    assert validator.validate_url("http://books.toscrape.com") == "http://books.toscrape.com"

def test_block_invalid_schemes():
    validator = UrlSecurityValidator()
    with pytest.raises(SSRFSecurityError, match="Invalid scheme"):
        validator.validate_url("ftp://example.com/file")
    with pytest.raises(SSRFSecurityError, match="Invalid scheme"):
        validator.validate_url("file:///etc/passwd")

def test_block_private_ips_and_localhost():
    validator = UrlSecurityValidator()
    with pytest.raises(SSRFSecurityError, match="Private or loopback IP blocked"):
        validator.validate_url("http://127.0.0.1:8000/secret")
    with pytest.raises(SSRFSecurityError, match="Private or loopback IP blocked"):
        validator.validate_url("http://localhost:8080")
    with pytest.raises(SSRFSecurityError, match="Private or loopback IP blocked"):
        validator.validate_url("http://169.254.169.254/metadata")
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_url_validator.py`

- [ ] **Step 3: Implement `UrlSecurityValidator` and install Playwright**
Create `app/crawler/url_validator.py` with DNS resolution, IPv4/IPv6 range checks (`ipaddress` module), scheme allowlist, and custom `SSRFSecurityError`. Update `requirements.txt` with `playwright>=1.40.0`.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_url_validator.py`

- [ ] **Step 5: Commit**
`git add requirements.txt app/crawler/url_validator.py tests/test_url_validator.py`
`git commit -m "feat(crawler): add url security validator for ssrf protection"`

---

### Task 2: Models & Declarative Action Framework

**Files:**
- Create: `app/crawler/result_models.py`
- Create: `app/crawler/action_models.py`
- Create: `app/crawler/action_executor.py`
- Test: `tests/test_action_executor.py`

**Interfaces:**
- Produces: `BlockType`, `CrawlResult`, `CrawlerAction`, `ActionPlan`, `ActionPlanExecutor`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_action_executor.py
import pytest
from app.crawler.action_models import ActionPlan, WaitForAction, ScrollAction, ExtractAction
from app.crawler.action_executor import ActionPlanExecutor

def test_action_plan_validation():
    plan = ActionPlan(
        url="https://example.com",
        actions=[
            WaitForAction(selector=".product-item", timeout_ms=5000),
            ScrollAction(max_iterations=3),
            ExtractAction(fields={"title": "h1", "price": ".price"})
        ]
    )
    assert len(plan.actions) == 3
    assert plan.actions[0].action_type == "wait_for"

def test_disallow_arbitrary_code():
    with pytest.raises(ValueError):
        ActionPlan(url="https://example.com", actions=[{"action_type": "eval_arbitrary_code", "code": "alert(1)"}])
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_action_executor.py`

- [ ] **Step 3: Implement `result_models.py`, `action_models.py`, and `action_executor.py`**
Implement Pydantic models for `BlockType` enum, `CrawlResult`, declarative action hierarchy with type discriminator, and `ActionPlanExecutor` with allowlisted action dispatching.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_action_executor.py`

- [ ] **Step 5: Commit**
`git add app/crawler/result_models.py app/crawler/action_models.py app/crawler/action_executor.py tests/test_action_executor.py`
`git commit -m "feat(crawler): add action models, result models, and action executor"`

---

### Task 3: Block Detector & Failure Classifier

**Files:**
- Create: `app/crawler/block_detector.py`
- Test: `tests/test_block_detector.py`

**Interfaces:**
- Produces: `BlockDetector.detect_block(status_code: int, headers: dict, html: str, url: str) -> tuple[bool, BlockType, dict]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_block_detector.py
import pytest
from app.crawler.block_detector import BlockDetector
from app.crawler.result_models import BlockType

def test_detect_http_status_blocks():
    detector = BlockDetector()
    blocked, b_type, diag = detector.detect_block(429, {}, "Too Many Requests", "https://example.com")
    assert blocked is True
    assert b_type == BlockType.RATE_LIMITED

    blocked, b_type, diag = detector.detect_block(403, {}, "Access Denied", "https://example.com")
    assert blocked is True
    assert b_type == BlockType.ACCESS_DENIED

def test_detect_captcha_and_challenge_in_html():
    detector = BlockDetector()
    html_cf = "<html><body><h1>Attention Required! | Cloudflare</h1><div>Please complete security check</div></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html_cf, "https://example.com")
    assert blocked is True
    assert b_type == BlockType.SECURITY_CHALLENGE

    html_fk = "<html><body><h1>Are you a human?</h1><p>Flipkart reCAPTCHA Confirming...</p></body></html>"
    blocked, b_type, diag = detector.detect_block(200, {}, html_fk, "https://flipkart.com")
    assert blocked is True
    assert b_type == BlockType.CAPTCHA
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_block_detector.py`

- [ ] **Step 3: Implement `BlockDetector`**
Implement signature matching for HTTP 403/429/401/407, Cloudflare/Akamai/PerimeterX challenge signatures, CAPTCHA/reCAPTCHA DOM patterns, and empty/broken response analysis.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_block_detector.py`

- [ ] **Step 5: Commit**
`git add app/crawler/block_detector.py tests/test_block_detector.py`
`git commit -m "feat(crawler): add block detector and challenge classifier"`

---

### Task 4: Rate Limiter, Circuit Breaker & Proxy Provider

**Files:**
- Create: `app/crawler/rate_limiter.py`
- Create: `app/crawler/circuit_breaker.py`
- Create: `app/crawler/proxy_provider.py`
- Test: `tests/test_rate_limiter.py`
- Test: `tests/test_circuit_breaker.py`

**Interfaces:**
- Produces: `DomainRateLimiter`, `DomainCircuitBreaker`, `ProxyProvider`

- [ ] **Step 1: Write failing tests**
Write tests for token-bucket delay calculations, concurrency throttling, exponential backoff with jitter on 429 Retry-After, and circuit breaker trip/reset states.

- [ ] **Step 2: Run tests to verify failure**
Run: `pytest tests/test_rate_limiter.py tests/test_circuit_breaker.py`

- [ ] **Step 3: Implement `rate_limiter.py`, `circuit_breaker.py`, `proxy_provider.py`**
Implement async token-bucket per-domain limiter with semaphore concurrency control, domain circuit breaker, and legitimate network proxy provider.

- [ ] **Step 4: Run tests to verify passing**
Run: `pytest tests/test_rate_limiter.py tests/test_circuit_breaker.py`

- [ ] **Step 5: Commit**
`git add app/crawler/rate_limiter.py app/crawler/circuit_breaker.py app/crawler/proxy_provider.py tests/test_rate_limiter.py tests/test_circuit_breaker.py`
`git commit -m "feat(crawler): add rate limiter, domain circuit breaker, and proxy provider"`

---

### Task 5: Playwright Browser Manager & Browser Executor

**Files:**
- Create: `app/crawler/browser_manager.py`
- Create: `app/crawler/browser_executor.py`
- Create: `app/crawler/config.py`
- Test: `tests/test_browser_executor.py`

**Interfaces:**
- Produces: `BrowserManager`, `BrowserExecutor.crawl(url: str, actions: ActionPlan | None = None) -> CrawlResult`

- [ ] **Step 1: Write integration and unit tests**
Test browser lifecycle, isolated context initialization, navigation, timeout handling, and HTML capture.

- [ ] **Step 2: Run tests to verify failure**
Run: `pytest tests/test_browser_executor.py`

- [ ] **Step 3: Implement `browser_manager.py`, `browser_executor.py`, and `config.py`**
Implement async Playwright browser pool, context isolation, standard viewport (1920x1080), locale (`en-US`), realistic non-deceptive User-Agent, action execution hook, and `BlockDetector` integration.

- [ ] **Step 4: Run tests to verify passing**
Run: `pytest tests/test_browser_executor.py`

- [ ] **Step 5: Commit**
`git add app/crawler/browser_manager.py app/crawler/browser_executor.py app/crawler/config.py tests/test_browser_executor.py`
`git commit -m "feat(crawler): implement async playwright browser manager and executor"`

---

### Task 6: ScraperAgent & LangGraph Self-Healing Integration

**Files:**
- Modify: `app/agents/scraper.py`
- Modify: `app/graph/workflow.py`
- Modify: `app/config/settings.py`
- Test: `tests/test_crawler_integration.py`

**Interfaces:**
- `ScraperAgent` seamlessly supports `SCRAPER_PROVIDER="browser"` / `"local"` / `"brightdata"` / `"auto"`.
- `workflow.py` routes `BlockType` failure gracefully to Self-Healing Orchestrator for compliant fallbacks.

- [ ] **Step 1: Write integration tests**
Test full scraping workflow dispatching to `BrowserExecutor`, validating results, and handling blocked status cleanly.

- [ ] **Step 2: Run test to verify failure**
Run: `pytest tests/test_crawler_integration.py`

- [ ] **Step 3: Integrate `BrowserExecutor` into `ScraperAgent` and `workflow.py`**
Update `ScraperAgent` to use `BrowserExecutor` for browser-based crawls and update settings with `CRAWLER_HEADLESS`, `CRAWLER_TIMEOUT_MS`, and `SCRAPER_PROVIDER`.

- [ ] **Step 4: Run full test suite across all phases**
Run: `pytest`

- [ ] **Step 5: Commit**
`git add app/agents/scraper.py app/graph/workflow.py app/config/settings.py tests/test_crawler_integration.py`
`git commit -m "feat(crawler): integrate playwright browser executor into scraper agent and workflow"`
