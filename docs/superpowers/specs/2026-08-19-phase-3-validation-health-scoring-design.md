# Phase 3: Validation Agent & Scraper Health Scoring Design Specification

## 1. Overview & Goal
Phase 3 extends the **Scrape_the_Verse** multi-agent pipeline by implementing comprehensive, deterministic data validation and quality evaluation.
The system answers: **"Did the scraper actually produce correct and sufficiently complete data?"**

The workflow advances to:
```
START ──► [planner] ──► [scraper] ──► [extraction] ──► [validation] ──► END
```

Phase 3 is strictly diagnostic and evaluative. It **does NOT** attempt self-healing, selector repair, or autonomous retry loops (reserved for Phase 5).

---

## 2. Validation Subsystem Architecture (`app/validation/`)

```
Extracted Records + ScrapingTask + Raw Results + Optional Baseline
                                │
                                ▼
                    ┌────────────────────────┐
                    │    ValidationEngine    │
                    └───────────┬────────────┘
                                │
     ┌───────────────┬──────────┼───────────────┬───────────────┐
     ▼               ▼          ▼               ▼               ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ Schema &  │  │ Duplicate │  │    URL    │  │  Anomaly  │  │ Baseline  │
│ Complete- │  │ Detector  │  │ Validator │  │ Detector  │  │ Deviation │
│ ness      │  │           │  │           │  │           │  │ Assessor  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │              │
      └──────────────┼──────────────┼──────────────┼──────────────┘
                     │
                     ▼
       ┌───────────────────────────┐
       │       HealthScorer        │ ── Weighted Mathematical Formula
       └─────────────┬─────────────┘
                     │
                     ▼
             ValidationResult
     (health_score, quality_score, status, metrics, anomalies, failures)
```

---

## 3. Health Scoring Formula & Categories

### Weighted Mathematical Formula (Configurable):
$$\text{Health Score} = \sum (w_i \times s_i)$$

| Dimension | Default Weight | Metric Meaning |
|---|---|---|
| **Schema Validity** | `0.20` | Fraction of records conforming to required schema types & structure |
| **Field Completeness** | `0.20` | Non-empty, non-placeholder field coverage across requested fields |
| **Record Count Health** | `0.15` | Conformance with explicit `max_records` or non-zero extraction sanity |
| **Type Validity** | `0.10` | Syntactic type matching (string, number, boolean, date, email) |
| **URL Validity** | `0.10` | Valid HTTP/HTTPS format for URL-typed fields |
| **Duplicate Health** | `0.10` | `1.0 - duplicate_rate` |
| **Extraction Consistency**| `0.15` | Cohesion of extracted fields across multiple records (no boilerplate noise) |

### Status Categorization:
- **`0.85 – 1.00`**: `healthy` (Pipeline operating cleanly)
- **`0.65 – 0.849`**: `degraded` (Partial field coverage or minor anomalies)
- **`0.40 – 0.649`**: `unstable` (Severe drops in field completeness or count)
- **`0.00 – 0.399`**: `broken` (Empty output, total schema mismatch, or structural failure)

### Health Score vs Quality Score Distinction:
- **`health_score`**: Reflects the operational health of the scraping and extraction pipeline.
- **`quality_score`**: Reflects data completeness and intrinsic source data quality.

---

## 4. Failure Taxonomy for Future Phases

Structured failures reported in `failures: list[FailureItem]`:
- `EMPTY_RESULTS`: Zero records produced when content was expected.
- `SCRAPER_OUTPUT_MISSING`: Scraper returned empty content (transport/blocking failure).
- `EXTRACTION_DEGRADATION`: Content returned but extraction yield was near zero.
- `SCHEMA_MISMATCH`: Critical required fields missing entirely.
- `LOW_FIELD_COVERAGE`: Essential fields have coverage below critical threshold.
- `HIGH_DUPLICATE_RATE`: Duplicate rate exceeding 30%.
- `INVALID_URLS`: High rate of malformed URLs.
- `INVALID_FIELD_TYPES`: Unparseable field values.
- `LOW_RECORD_COUNT`: Severe drop in yield compared to expectation or baseline.

---

## 5. LangGraph Workflow & State Mutation

- **`validation_node`**: Invokes `ValidationAgent` passing `extracted_results`, `scraping_task`, `raw_results`.
- **State Updates**:
  - `state["validation_result"] = validation_result`
  - `state["failure"] = failure_info` (if degraded, unstable, or broken)
  - `state["final_output"] = ScrapingResult` with validation metadata and health score attached.
