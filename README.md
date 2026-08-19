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

