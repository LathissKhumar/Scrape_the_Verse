# Conditional Fallback Link Crawling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement conditional fallback link crawling to discover, crawl, and extract missing data from child links when a primary URL does not contain all desired fields.

**Architecture:** A `LinkDiscoveryEngine` parses `<a href>` links from rendered primary pages, filters by domain and keyword relevance, and conditionally fetches child pages via parallel Playwright contexts to fuse missing fields.

**Tech Stack:** Python 3.10, BeautifulSoup4, Playwright, Pydantic, pytest.

**Spec:** `docs/superpowers/specs/2026-08-19-conditional-fallback-link-crawling-design.md`

## Global Constraints
- Enforce domain boundary: never crawl outside the primary target domain unless explicitly enabled.
- SSRF prevention: pass all discovered URLs through `UrlSecurityValidator`.
- Zero overhead when primary page already satisfies all fields.

---

### Task 1: Link Discovery Engine (`app/crawler/link_discovery.py`)

**Files:**
- Create: `app/crawler/link_discovery.py`
- Test: `tests/test_link_discovery.py`

- [ ] **Step 1: Write the failing unit tests for `LinkDiscoveryEngine`**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `LinkDiscoveryEngine` with URL resolution and relevance scoring**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 2: Conditional Child Crawl & Field Fusion Integration

**Files:**
- Modify: `app/agents/extraction.py`
- Modify: `app/extraction/engine.py`
- Modify: `app/agents/scraper.py`
- Test: `tests/test_conditional_crawling.py`

- [ ] **Step 1: Write integration tests for missing-field child link crawling**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement conditional child link crawl and record field fusion**
- [ ] **Step 4: Run full test suite to verify 100% pass**
- [ ] **Step 5: Commit**
