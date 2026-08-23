'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Bot, Search, BarChart3, Settings, Palette, Rocket } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const TECH_CATEGORIES = [
  {
    category: 'AI & Agents',
    icon: <Bot className="w-5 h-5 text-sky-400" />,
    items: ['Claude AI (Anthropic)', 'Multi-Agent Architecture', 'Prompt Engineering', 'Structured Output Parsing'],
    color: 'border-sky-400/25 from-sky-400/10',
  },
  {
    category: 'Lead Discovery',
    icon: <Search className="w-5 h-5 text-indigo-400" />,
    items: ['Web Scraping', 'IndiaMART Crawler', 'Yelp Data Extraction', 'Google Maps Scraping', 'Avvo Scraping'],
    color: 'border-indigo-400/25 from-indigo-400/10',
  },
  {
    category: 'SEO & Web Analysis',
    icon: <BarChart3 className="w-5 h-5 text-emerald-400" />,
    items: ['Custom Crawl Engine', 'On-Page SEO Analyzer', 'Technical SEO Audit', 'Local SEO Analysis', 'Content Gap Detection'],
    color: 'border-emerald-400/25 from-emerald-400/10',
  },
  {
    category: 'Backend & Pipeline',
    icon: <Settings className="w-5 h-5 text-violet-400" />,
    items: ['Python', 'FastAPI', 'Agent Orchestration', 'REST API', 'Async Pipeline'],
    color: 'border-violet-400/25 from-violet-400/10',
  },
  {
    category: 'Frontend',
    icon: <Palette className="w-5 h-5 text-cyan-400" />,
    items: ['React 19', 'Next.js 16', 'Tailwind CSS 4', 'TypeScript', 'Framer Motion', 'GSAP'],
    color: 'border-cyan-400/25 from-cyan-400/10',
  },
  {
    category: 'Output Compatible With',
    icon: <Rocket className="w-5 h-5 text-rose-400" />,
    items: ['Lovable', 'v0 by Vercel', 'Bolt', 'Firebase Studio', 'Claude Code', 'Cursor', 'OpenCode'],
    color: 'border-rose-400/25 from-rose-400/10',
  },
]

// Duplicate items for continuous seamless horizontal marquee loop
const MARQUEE_CATEGORIES = [...TECH_CATEGORIES, ...TECH_CATEGORIES]

export function TechStackSection() {
  const [isPaused, setIsPaused] = useState(false)

  return (
    <section
      id="tech-stack-section"
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Tech Stack — Under the Hood"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-10">
        {/* Header */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <SectionLabel label="UNDER THE HOOD" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            <GradientText>Built With</GradientText>
          </h2>
          <p className="text-base text-text-secondary font-body max-w-xl mx-auto leading-relaxed">
            The technologies powering every agent in the Scrape-Verse pipeline.
          </p>
        </div>
      </div>

      {/* Continuously Moving Horizontal Marquee Track (Right to Left) */}
      <div
        className="relative w-full overflow-hidden mt-8"
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        <motion.div
          className="flex items-stretch gap-6 w-max will-change-transform py-4 px-6"
          animate={{
            x: isPaused ? undefined : ['0%', '-50%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: 'loop',
              duration: 35,
              ease: 'linear',
            },
          }}
        >
          {MARQUEE_CATEGORIES.map((cat, i) => (
            <motion.div
              key={`${cat.category}-${i}`}
              whileHover={{ y: -4, scale: 1.02 }}
              data-cursor-hover
              className={`w-[320px] sm:w-[360px] glass-card p-6 rounded-3xl border ${cat.color} bg-gradient-to-br to-transparent flex flex-col justify-between shrink-0 shadow-2xl backdrop-blur-2xl transition-all duration-300 group cursor-default`}
            >
              <div className="space-y-4">
                {/* Category header with clean Lucide SVG icon */}
                <div className="flex items-center gap-3 border-b border-white/10 pb-3">
                  <div className="p-2 rounded-xl bg-white/10 border border-white/15 backdrop-blur-md shadow-md shrink-0 flex items-center justify-center">
                    {cat.icon}
                  </div>
                  <h3 className="font-bold font-display text-text-primary text-base sm:text-lg group-hover:text-sky-300 transition-colors">
                    {cat.category}
                  </h3>
                </div>

                {/* Tech chips */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {cat.items.map((item) => (
                    <span
                      key={item}
                      className="text-[11px] font-mono font-semibold px-2.5 py-1 rounded-full bg-white/8 border border-white/15 text-slate-200 group-hover:border-sky-400/40 transition-colors"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-white/10 flex items-center justify-between text-[10px] font-mono text-slate-400 mt-4">
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  INTEGRATED
                </span>
                <span className="text-sky-400 font-bold group-hover:translate-x-0.5 transition-transform">
                  SCRAPE-VERSE STACK &rarr;
                </span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}