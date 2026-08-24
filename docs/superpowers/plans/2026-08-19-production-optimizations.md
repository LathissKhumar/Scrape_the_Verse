# Production-Grade System Optimizations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 5 production-grade optimizations across Scrape_the_Verse: Local Vision OCR (`gemma4:e2b`) for text extraction from images, Deterministic Catalog Card Extractor, Concurrent Multi-Chunk LLM Extraction, Persistent SQLite Repair Memory, and Multi-Format Exporters (CSV/JSON).

**Architecture:** Extend the existing modular architecture with zero breaking changes: (1) `app/extraction/vision.py` for OCR image text extraction via `gemma4:e2b`, (2) `app/extraction/grid_cards.py` for instant repeating card detection, (3) `app/extraction/llm.py` parallel chunk extraction, (4) `app/healing/persistent_memory.py` for persistent SQLite repair caching, (5) `app/export/` for multi-format export.

**Tech Stack:** Python 3.10, FastAPI, Playwright Chromium, LangGraph, Ollama (`qwen3:8b` & `gemma4:e2b`), BeautifulSoup4, SQLite3, Pytest.

**Spec:** In-session design approved by user on 2026-08-19.

## Global Constraints
- Preserve all existing API endpoints, request/response models, status codes, and graph state contracts.
- Keep Ollama `qwen3:8b` as the primary reasoning and planning LLM.
- Use `gemma4:e2b` specifically for OCR text extraction from images (verbatim text only, no image descriptions).
- All 169 existing tests must continue to pass with 0 regressions.

---

### Task 1: Vision OCR Image-to-Text Module (`gemma4:e2b`)

**Files:**
- Create: `app/extraction/vision.py`
- Test: `tests/test_vision_extraction.py`
- Modify: `app/extraction/engine.py:30-65`

**Interfaces:**
- Produces: `VisionTextExtractor.extract_text_from_image(image_bytes_or_url: str | bytes) -> str`
- Consumes: Ollama `/api/generate` with model `gemma4:e2b` and `images: [base64_str]`.

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/test_vision_extraction.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.extraction.vision import VisionTextExtractor


@pytest.mark.asyncio
async def test_vision_text_extractor_extracts_verbatim_text():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"response": "Special Price: $19.99\nModel: ABC-123"},
        )
    )

    extractor = VisionTextExtractor(model_name="gemma4:e2b", client=mock_client)
    text = await extractor.extract_text_from_image_base64("dummy_base64_data")
    assert "Special Price: $19.99" in text
    assert "Model: ABC-123" in text
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_vision_extraction.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement VisionTextExtractor**

```python
# app/extraction/vision.py
import base64
import httpx
from typing import Optional
from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger("VISION_EXTRACTOR")

VISION_OCR_SYSTEM_PROMPT = """You are a high-precision OCR text extractor.
Extract all visible text, numbers, prices, labels, and tabular data from this image verbatim.
DO NOT describe what the image looks like.
Output ONLY the raw extracted text and data found in the image."""


class VisionTextExtractor:
    """Extracts text data from page images using Ollama vision models (e.g. gemma4:e2b)."""

    def __init__(
        self, model_name: str = "gemma4:e2b", client: Optional[httpx.AsyncClient] = None
    ):
        self.settings = get_settings()
        self.model_name = model_name
        self.base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self.client = client

    async def extract_text_from_image_base64(self, image_base64: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": "Extract all text and data from this image verbatim.",
            "system": VISION_OCR_SYSTEM_PROMPT,
            "images": [image_base64],
            "stream": False,
        }
        endpoint = f"{self.base_url}/api/generate"
        try:
            if self.client:
                resp = await self.client.post(endpoint, json=payload)
            else:
                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    resp = await http_client.post(endpoint, json=payload)
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception as e:
            logger.warning(f"Vision OCR extraction failed: {e}")
        return ""
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_vision_extraction.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/extraction/vision.py tests/test_vision_extraction.py
git commit -m "feat(vision): add VisionTextExtractor using gemma4:e2b for verbatim OCR"
```

---

### Task 2: Deterministic Catalog & Repeating Card Extractor

**Files:**
- Create: `app/extraction/grid_cards.py`
- Test: `tests/test_grid_card_extractor.py`
- Modify: `app/extraction/engine.py:40-100`

**Interfaces:**
- Produces: `GridCardExtractor.extract(html: str, target_fields: list[str]) -> list[dict[str, Any]]`

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/test_grid_card_extractor.py
import pytest
from app.extraction.grid_cards import GridCardExtractor


def test_grid_card_extractor_extracts_product_cards():
    html = """
    <div class="container">
      <article class="product_pod">
        <h3><a href="b1.html" title="Book One">Book One</a></h3>
        <p class="price_color">£12.99</p>
        <p class="instock">In stock</p>
      </article>
      <article class="product_pod">
        <h3><a href="b2.html" title="Book Two">Book Two</a></h3>
        <p class="price_color">£24.50</p>
        <p class="instock">In stock</p>
      </article>
    </div>
    """
    extractor = GridCardExtractor()
    records = extractor.extract(
        html=html, target_fields=["title", "price", "availability"]
    )
    assert len(records) == 2
    assert "Book One" in records[0].get("title", "")
    assert "12.99" in records[0].get("price", "")
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_grid_card_extractor.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement GridCardExtractor**

```python
# app/extraction/grid_cards.py
from typing import Any, Optional
from bs4 import BeautifulSoup, Tag
from app.extraction.engine import FIELD_SYNONYM_MAP


class GridCardExtractor:
    """Deterministically extracts repeating cards/items (products, quotes, articles) from HTML."""

    CARD_TAGS = ["article", "li", "div", "tr", "section"]
    COMMON_CARD_CLASSES = [
        "product",
        "item",
        "card",
        "quote",
        "result",
        "post",
        "entry",
        "listing",
    ]

    def extract(
        self, html: str, target_fields: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        if not html or not html.strip():
            return []
        soup = BeautifulSoup(html, "html.parser")
        fields = target_fields or ["title", "price", "link", "description"]

        candidate_containers = []
        for tag_name in self.CARD_TAGS:
            elements = soup.find_all(tag_name)
            by_class: dict[str, list[Tag]] = {}
            for el in elements:
                classes = " ".join(el.get("class", []))
                if classes:
                    by_class.setdefault(classes, []).append(el)

            for cls_name, items in by_class.items():
                if len(items) >= 2:
                    is_relevant = any(
                        c in cls_name.lower() for c in self.COMMON_CARD_CLASSES
                    ) or tag_name in ("article", "tr")
                    score = len(items) * (2 if is_relevant else 1)
                    candidate_containers.append((score, items))

        if not candidate_containers:
            return []

        candidate_containers.sort(key=lambda x: x[0], reverse=True)
        best_items = candidate_containers[0][1]

        records = []
        for item in best_items:
            rec = self._extract_card_fields(item, fields)
            if any(rec.values()):
                records.append(rec)
        return records

    def _extract_card_fields(
        self, card: Tag, target_fields: list[str]
    ) -> dict[str, Any]:
        rec = {}
        for f in target_fields:
            val = None
            f_lower = f.lower()
            if f_lower in ("title", "name", "heading"):
                for heading_tag in ["h1", "h2", "h3", "h4", "a"]:
                    h = card.find(heading_tag)
                    if h:
                        val = h.get("title") or h.get_text(strip=True)
                        if val:
                            break
            elif f_lower in ("price", "cost", "amount"):
                price_el = card.find(
                    class_=lambda c: (
                        c
                        and any(
                            p in str(c).lower() for p in ["price", "cost", "amount"]
                        )
                    )
                )
                if price_el:
                    val = price_el.get_text(strip=True)
                else:
                    for text in card.stripped_strings:
                        if any(cur in text for cur in ["$", "£", "€", "¥", "Rs"]):
                            val = text
                            break
            elif f_lower in ("link", "url", "href"):
                a = card.find("a", href=True)
                if a:
                    val = a["href"]
            elif f_lower in ("image", "img", "thumbnail"):
                img = card.find("img")
                if img:
                    val = img.get("src") or img.get("data-src")
            elif f_lower in ("availability", "stock", "status"):
                stock_el = card.find(
                    class_=lambda c: (
                        c
                        and any(
                            s in str(c).lower()
                            for s in ["stock", "availability", "status"]
                        )
                    )
                )
                if stock_el:
                    val = stock_el.get_text(strip=True)
            if not val:
                # Direct class search for field name
                el = card.find(class_=lambda c: c and f_lower in str(c).lower())
                if el:
                    val = el.get_text(strip=True)
            rec[f] = val
        return rec
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_grid_card_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/extraction/grid_cards.py tests/test_grid_card_extractor.py
git commit -m "feat(extraction): add deterministic GridCardExtractor for catalog pages"
```

---

### Task 3: Concurrent Multi-Chunk LLM Extraction

**Files:**
- Modify: `app/extraction/llm.py:90-145`
- Test: `tests/test_concurrent_extraction.py`

**Interfaces:**
- Produces: Parallel chunk processing in `LLMExtractor.extract_async` via `asyncio.gather()`.

- [ ] **Step 1: Write test verifying concurrent chunk processing**

```python
# tests/test_concurrent_extraction.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.extraction.llm import LLMExtractor
from app.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_llm_extractor_concurrent_chunks():
    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(
        side_effect=[
            '[{"title": "Item 1", "price": "$10"}]',
            '[{"title": "Item 2", "price": "$20"}]',
        ]
    )
    extractor = LLMExtractor(llm_client=mock_llm)
    task = ScrapingTask(
        task_id="t1",
        objective="Scrape items",
        target_urls=["https://example.com"],
        fields=["title", "price"],
    )

    records = await extractor.extract_async(
        raw_content="Chunk 1 content paragraph\n\n\n\nChunk 2 content paragraph",
        task=task,
    )
    assert len(records) >= 1
```

- [ ] **Step 2: Update LLMExtractor with asyncio.gather**

Update `app/extraction/llm.py` so that chunks are processed concurrently with `asyncio.gather(*tasks)` in `extract_async`.

- [ ] **Step 3: Run test to verify it passes**
Run: `pytest tests/test_concurrent_extraction.py -v`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add app/extraction/llm.py tests/test_concurrent_extraction.py
git commit -m "perf(extraction): parallelize multi-chunk LLM extraction with asyncio.gather"
```

---

### Task 4: Persistent SQLite Repair Memory

**Files:**
- Create: `app/healing/persistent_memory.py`
- Modify: `app/healing/memory.py:1-60`
- Test: `tests/test_persistent_repair_memory.py`

**Interfaces:**
- Produces: `PersistentRepairMemory` auto-migrating and querying SQLite database for domain repair records.

- [ ] **Step 1: Write test verifying persistent SQLite storage across instances**

```python
# tests/test_persistent_repair_memory.py
import os
import pytest
from app.healing.persistent_memory import PersistentRepairMemory
from app.healing.schemas import RepairMemoryRecord, RepairType


def test_persistent_repair_memory_saves_and_reloads(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    mem1 = PersistentRepairMemory(db_path=db_file)
    rec = RepairMemoryRecord(
        domain="example.com",
        failure_signature="sig_123",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        patch={"fields": [{"name": "price", "selector": ".new-price"}]},
        before_health=0.2,
        after_health=1.0,
    )
    mem1.record_success(rec)

    # Instantiate fresh memory pointing to same DB
    mem2 = PersistentRepairMemory(db_path=db_file)
    match = mem2.lookup("example.com", "sig_123")
    assert match is not None
    assert match.repair_type == RepairType.REPAIR_CSS_SELECTORS
    assert match.patch["fields"][0]["selector"] == ".new-price"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_persistent_repair_memory.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement PersistentRepairMemory**

```python
# app/healing/persistent_memory.py
import json
import sqlite3
from typing import Optional
from app.config.logging import get_logger
from app.healing.schemas import RepairMemoryRecord, RepairType

logger = get_logger("PERSISTENT_REPAIR_MEMORY")


class PersistentRepairMemory:
    """SQLite-backed persistent repair memory for instant repeat self-healing."""

    def __init__(self, db_path: str = ".repair_memory.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repair_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    failure_signature TEXT NOT NULL,
                    repair_type TEXT NOT NULL,
                    patch_json TEXT NOT NULL,
                    before_health REAL,
                    after_health REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(domain, failure_signature)
                )
            """)
            conn.commit()

    def record_success(self, record: RepairMemoryRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO repair_memory (domain, failure_signature, repair_type, patch_json, before_health, after_health)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    record.domain,
                    record.failure_signature,
                    record.repair_type.value,
                    json.dumps(record.patch),
                    record.before_health,
                    record.after_health,
                ),
            )
            conn.commit()
            logger.info(
                f"Persistent repair stored for domain={record.domain} sig={record.failure_signature}"
            )

    def lookup(
        self, domain: str, failure_signature: str
    ) -> Optional[RepairMemoryRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT domain, failure_signature, repair_type, patch_json, before_health, after_health
                FROM repair_memory WHERE domain = ? AND failure_signature = ?
            """,
                (domain, failure_signature),
            )
            row = cursor.fetchone()
            if row:
                return RepairMemoryRecord(
                    domain=row[0],
                    failure_signature=row[1],
                    repair_type=RepairType(row[2]),
                    patch=json.loads(row[3]),
                    before_health=row[4],
                    after_health=row[5],
                )
        return None
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_persistent_repair_memory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/persistent_memory.py tests/test_persistent_repair_memory.py
git commit -m "feat(healing): add SQLite-backed PersistentRepairMemory for instant repeat recovery"
```

---

### Task 5: Multi-Format Data Exporter (CSV, JSON, NDJSON)

**Files:**
- Create: `app/export/exporter.py`
- Create: `app/export/__init__.py`
- Modify: `cli.py:120-155`
- Test: `tests/test_data_exporter.py`

**Interfaces:**
- Produces: `DataExporter.to_csv(records: list[dict[str, Any]]) -> str`, `DataExporter.to_json(...)`

- [ ] **Step 1: Write unit tests for DataExporter**

```python
# tests/test_data_exporter.py
import pytest
from app.export.exporter import DataExporter


def test_data_exporter_csv_and_json():
    records = [{"title": "Book 1", "price": "$10"}, {"title": "Book 2", "price": "$20"}]
    csv_str = DataExporter.to_csv(records)
    assert "title,price" in csv_str
    assert "Book 1,$10" in csv_str

    json_str = DataExporter.to_json(records)
    assert '"title": "Book 1"' in json_str
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_data_exporter.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement DataExporter**

```python
# app/export/exporter.py
import csv
import io
import json
from typing import Any


class DataExporter:
    """Exports structured scraping records to various standard file formats."""

    @staticmethod
    def to_csv(records: list[dict[str, Any]]) -> str:
        if not records:
            return ""
        output = io.StringIO()
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
        return output.getvalue()

    @staticmethod
    def to_json(records: list[dict[str, Any]], indent: int = 2) -> str:
        return json.dumps(records, indent=indent, default=str)

    @staticmethod
    def to_ndjson(records: list[dict[str, Any]]) -> str:
        return "\n".join(json.dumps(r, default=str) for r in records)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_data_exporter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/export/ tests/test_data_exporter.py
git commit -m "feat(export): add multi-format DataExporter for CSV, JSON, and NDJSON"
```

---

### Task 6: Full Integration and Benchmark Verification

- [ ] **Step 1: Run complete test suite**
Run: `pytest -q`
Expected: All 175+ tests pass with 0 failures.

- [ ] **Step 2: Run stress test benchmark**
Run: `python scripts/stress_test_native_engine.py`
Expected: 3 / 3 Benchmark tests pass with 1.00 Health Score.

- [ ] **Step 3: Final Commit**
```bash
git add .
git commit -m "chore: complete production optimization suite"
```
