# 🌐 Scrape-Verse — Frontend

> The landing page and UI layer for **Scrape-Verse**, an AI-powered business development platform built for web and SEO agencies.

---

## 🧰 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 16.3.1 | React framework (App Router) |
| **React** | 19.2.8 | UI library |
| **TypeScript** | ^5 | Type safety |
| **Tailwind CSS** | ^4 | Utility-first styling |
| **Framer Motion** | ^13 | Scroll & UI animations |
| **GSAP** | ^3.15 | Timeline & ScrollTrigger animations |
| **Lenis** | ^1.3 | Smooth scrolling provider |
| **Lucide React** | ^1.32 | Icon library |

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have the following installed:

- **Node.js** ≥ 18.x → [nodejs.org](https://nodejs.org)
- **npm** ≥ 9.x (comes with Node.js)

### 2. Navigate to the Frontend Directory

```bash
cd MicroServices/UI/frontend
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Run Development Server

```bash
npm run dev
```

The app will be available at:

```
http://localhost:3000
```

> The dev server uses **Webpack** (`next dev --webpack`) for compatibility with GSAP and Lenis.

---

## 📦 Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server at `localhost:3000` |
| `npm run build` | Build optimised production bundle |
| `npm run start` | Start production server (after build) |
| `npm run lint` | Run ESLint across the codebase |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css          # Global CSS, design tokens, keyframes
│   │   ├── layout.tsx           # Root layout with fonts & providers
│   │   └── page.tsx             # Main landing page composition
│   ├── components/
│   │   ├── sections/            # Landing page sections
│   │   │   ├── Hero.tsx
│   │   │   ├── ProblemSection.tsx
│   │   │   ├── HorizontalPipeline.tsx
│   │   │   ├── Pipeline.tsx
│   │   │   ├── LiveExample.tsx
│   │   │   ├── LeadScoring.tsx
│   │   │   ├── TechStackSection.tsx
│   │   │   ├── PinnedHorizontalPillars.tsx
│   │   │   ├── WhyScrapeVerse.tsx
│   │   │   ├── FinalCTA.tsx
│   │   │   └── Footer.tsx
│   │   ├── ui/                  # Reusable UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── GradientText.tsx
│   │   │   └── SectionLabel.tsx
│   │   └── providers/
│   │       └── SmoothScrollProvider.tsx   # Lenis smooth scroll
│   └── lib/
│       ├── mock-data.ts         # Pipeline & agent data
│       └── types.ts             # Shared TypeScript types
├── public/                      # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
└── README.md
```

---

## 🎨 Design System

- **Color Palette**: Cold glassmorphic dark theme (`#07090D` base, sky/cyan/indigo accents)
- **Typography**: `Inter` (body) + `Outfit` (display) via Google Fonts
- **Glass Effects**: `.glass-card`, `.glass-liquid`, `.glass-level-2/3` utility classes defined in `globals.css`
- **Animations**:
  - Scroll-triggered reveals via **GSAP ScrollTrigger**
  - Micro-animations via **Framer Motion**
  - Smooth page scroll via **Lenis**

---

## ⚡ Performance Notes

- Uses `--webpack` flag explicitly for compatibility with GSAP and Lenis (avoids Turbopack conflicts)
- `will-change: transform` applied on animated marquee tracks for GPU compositing
- `ScrollTrigger.refresh()` called with a 300ms delay after mount to sync trigger positions

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| Port 3000 already in use | Run `npm run dev -- -p 3001` to use a different port |
| Module not found errors | Delete `node_modules` and run `npm install` again |
| TypeScript errors | Run `npx tsc --noEmit --skipLibCheck` to inspect |
| GSAP animations not firing | Ensure `ScrollTrigger` is registered via `gsap.registerPlugin(ScrollTrigger)` |
| Smooth scroll not working | Check `SmoothScrollProvider` is wrapping the layout in `layout.tsx` |

---

## 📄 License

This project was built for **Hackathon 2026**. All rights reserved.
