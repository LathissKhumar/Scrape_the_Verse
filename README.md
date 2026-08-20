# SCRAPE-VERSE — Self-Healing Web Intelligence Platform

An enterprise-grade, self-healing web intelligence platform designed for discovering, researching, and converting business opportunities across the web.

## Project Structure

```
Scrape_The_Verse/
├── frontend/                     # Dedicated Next.js frontend application
│   ├── public/                   # Static assets & images
│   │   ├── images/               # Cold twilight tech workspace & background assets
│   │   └── ...
│   ├── src/
│   │   ├── app/                  # Next.js App Router (page, layout, globals.css)
│   │   ├── components/
│   │   │   ├── providers/        # Smooth scroll (Lenis + GSAP) providers & index
│   │   │   ├── sections/         # Landing page section modules & index
│   │   │   └── ui/               # Reusable UI primitives, cards, and cursor & index
│   │   ├── hooks/                # Custom animation & interactive state hooks & index
│   │   └── lib/                  # Data models, types, and utilities & index
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   └── tsconfig.json
├── package.json                  # Root workspace orchestrator
└── README.md
```

## Quick Start

You can run commands directly from the root repository directory (using npm workspaces) or from inside the `frontend/` folder.

### From Root:
```bash
# Start development server
npm run dev

# Build production bundle
npm run build

# Start production server
npm run start

# Lint codebase
npm run lint
```

### From `frontend/`:
```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to explore the platform.

---

## 🔍 SEO Agent & LibreCrawl Engine

LangGraph-powered AI SEO Audit Engine with headless Playwright JavaScript crawling, automated rule analyzers, multi-tab Excel export, structured JSON export, and domain-partitioned reporting.

### Run Full SEO Audit Command:

From workspace root:

```bash
python seo/seo_agent.py --url https://www.atlaskliniek.nl/en/dentist-amsterdam/ --depth 3 --max-pages 100 --javascript --pagespeed --export-all seo/report/atlas_audit
```

From `seo/` directory:

```bash
cd seo
python seo_agent.py --url https://www.atlaskliniek.nl/en/dentist-amsterdam/ --depth 3 --max-pages 100 --javascript --pagespeed --export-all report/atlas_audit
```

### Generated Report Outputs:

1. **📄 Executive Markdown Summary**: `seo/report/atlas_audit.md`
2. **🗂️ Detailed Master JSON**: `seo/report/atlas_audit.json`
3. **📊 Multi-Tab Styled Excel Workbook**: `seo/report/atlas_audit.xlsx`
4. **📂 Partitioned Domain Folder**: `seo/report/atlaskliniek.nl/` (17 normalized subfolders for LLM agents)
5. **📘 Directory Documentation**: `seo/report/REPORT.md`

### Run Test Suite:

```bash
pytest seo/tests LibreCrawl/tests/test_headless_engine.py
```

