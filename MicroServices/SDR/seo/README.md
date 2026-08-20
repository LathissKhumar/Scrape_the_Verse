# 🔍 SEO Agent & LibreCrawl Engine

LangGraph-powered AI SEO Audit Engine with headless Playwright JavaScript crawling, automated rule analyzers, multi-tab Excel export, structured JSON export, and domain-partitioned reporting.

---

## ⚡ Quick Start

### 1. Run Complete Audit with All Reports

From inside the `seo/` directory:

```bash
python seo_agent.py --url https://www.atlaskliniek.nl/en/dentist-amsterdam/ --depth 3 --max-pages 100 --javascript --pagespeed --export-all report/atlas_audit
```

From root workspace (`Scrape_the_Verse/`):

```bash
python seo/seo_agent.py --url https://www.atlaskliniek.nl/en/dentist-amsterdam/ --depth 3 --max-pages 100 --javascript --pagespeed --export-all seo/report/atlas_audit
```

---

## 📊 Command Options

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--url` | `-u` | Website URL to audit (required) | *None* |
| `--depth` | `-d` | Maximum crawl depth | `3` |
| `--max-pages` | `-m` | Maximum pages to crawl | `100` |
| `--javascript` | `--js` | Enable Playwright JavaScript rendering | `false` |
| `--pagespeed` | `--ps` | Enable Google PageSpeed Insights CWV analysis | `false` |
| `--pagespeed-key` | `-k` | Google PageSpeed API Key (prevents rate limits) | *Env / None* |
| `--export-all` | | Export Markdown report, full JSON, and Excel workbook | *None* |
| `--excel` | `-x` | Export detailed multi-tab Excel workbook (`.xlsx`) | *None* |
| `--json-output` | `-j` | Export raw & normalized audit JSON (`.json`) | *None* |
| `--output` | `-o` | Save Markdown report or export file | *None* |
| `--data-dir` | | Base directory for domain-partitioned data | `report` |

---

## 📁 Generated Reports & Directory Structure

Running `--export-all report/atlas_audit` creates all 4 report formats:

```
seo/report/
├── REPORT.md                         ← Complete human-readable directory documentation
├── atlas_audit.md                    ← Executive Markdown audit summary
├── atlas_audit.json                  ← Un-truncated master crawl & audit JSON
├── atlas_audit.xlsx                  ← Styled multi-tab Excel workbook (6 sheets)
│
└── atlaskliniek.nl/                  ← Domain folder (17 normalized subfolders)
    ├── index.json                    ← Master root index for LLM agents & APIs
    ├── analytics/                    ← GA4, GTM, Facebook Pixel tracking detection
    ├── content/                      ← Word count metrics, thin pages, duplicate titles
    ├── extra/                        ← Custom unclassified crawler fields
    ├── images/                       ← Image registry & missing alt text
    ├── issues/                       ← Issues database (critical → low)
    ├── links/                        ← Internal, external, broken links & architecture
    ├── local/                        ← LocalBusiness schema & NAP signals
    ├── onpage/                       ← Titles, meta descriptions, H1-H3 headings
    ├── pages/                        ← Per-page modular JSON records + index
    ├── performance/                  ← Response times, slow pages, PageSpeed CWV
    ├── raw/                          ← Original unmodified crawl JSON (source of truth)
    ├── recommendations/              ← Prioritized action items & quick wins
    ├── schema/                       ← JSON-LD structured data detected & missing
    ├── summary/                      ← Executive overview, category scores & validation
    └── technical/                    ← Canonicals, robots, sitemaps, redirects, errors
```

---

## 🧪 Run Automated Tests

To run the complete test suite (31 tests):

```bash
# From workspace root:
pytest seo/tests LibreCrawl/tests/test_headless_engine.py

# From seo/ directory (inside venv):
pytest tests/
```
