'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { GradientText } from '@/components/ui/GradientText'
import { Cpu, Gauge, Activity, Target, Sparkles } from 'lucide-react'

const PILLARS = [
  {
    num: '01',
    title: 'Autonomous Ingestion',
    tag: 'Web Discovery',
    icon: <Cpu className="w-5 h-5 text-sky-400" />,
    desc: 'Continuous real-time indexing across 500M+ web pages with intelligent rate-limiting and anti-fingerprinting proxies.',
    glow: 'radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.22) 0%, transparent 65%)',
  },
  {
    num: '02',
    title: 'Self-Healing Engine',
    tag: 'DOM Resilience',
    icon: <Gauge className="w-5 h-5 text-indigo-400" />,
    desc: 'AI vision models detect structural shifts and re-synthesize XPath selectors in 350ms without pipeline downtime.',
    glow: 'radial-gradient(ellipse at top right, rgba(96, 165, 250, 0.22) 0%, transparent 65%)',
  },
  {
    num: '03',
    title: 'Parallel Synthesis',
    tag: 'Data Enrichment',
    icon: <Activity className="w-5 h-6 text-cyan-300" />,
    desc: 'Cross-correlates business registries, reviews, and decision-maker contact paths into normalized streams in sub-seconds.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(129, 140, 248, 0.22) 0%, transparent 65%)',
  },
  {
    num: '04',
    title: 'Actionable Intelligence',
    tag: 'Sales Conversion',
    icon: <Target className="w-5 h-5 text-emerald-400" />,
    desc: 'Dispatches high-confidence purchase signals and customized outreach collateral directly to your CRM webhook queues.',
    glow: 'radial-gradient(ellipse at center, rgba(52, 211, 153, 0.18) 0%, transparent 65%)',
  },
]

// Duplicate for continuous seamless marquee loop
const MARQUEE_ITEMS = [...PILLARS, ...PILLARS, ...PILLARS]

export function PinnedHorizontalPillars() {
  const [isPaused, setIsPaused] = useState(false)

  return (
    <section
      id="pillars-marquee"
      className="py-14 md:py-18 relative border-b border-white/10 bg-transparent font-body overflow-hidden"
      aria-label="Continuously Moving Core Pillars"
    >
      {/* Header bar - Compact with no excessive free space */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 w-full mb-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
          <div>
            <SectionLabel label="Continuous Pipeline Stream" />
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold font-display tracking-tight text-text-primary mt-1.5">
              <GradientText>Four Core Pillars.</GradientText> Infinite Autonomous Flow.
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-slate-300">Live Continuous Stream</span>
            <span className="text-slate-500 hidden sm:inline">(Hover to pause)</span>
          </div>
        </div>
      </div>

      {/* Continuously Moving Horizontal Marquee Track */}
      <div
        className="relative w-full overflow-hidden"
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        {/* Subtle Edge Fade Gradients */}
        <div className="absolute left-0 top-0 bottom-0 w-16 md:w-20 bg-gradient-to-r from-black/25 to-transparent z-20 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-16 md:w-20 bg-gradient-to-l from-black/25 to-transparent z-20 pointer-events-none" />

        <motion.div
          className="flex items-center gap-6 w-max will-change-transform py-2"
          animate={{
            x: isPaused ? undefined : ['0%', '-33.333%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: 'loop',
              duration: 22,
              ease: 'linear',
            },
          }}
        >
          {MARQUEE_ITEMS.map((card, idx) => (
            <motion.div
              key={`${card.num}-${idx}`}
              whileHover={{ y: -4, scale: 1.02 }}
              data-cursor-hover
              className="w-[320px] sm:w-[360px] md:w-[390px] h-[270px] rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden shrink-0 glass-liquid border border-white/25 shadow-xl backdrop-blur-2xl transition-all duration-300 group"
              style={{
                boxShadow:
                  '0 15px 35px rgba(0, 0, 0, 0.35), inset 0 1px 1.5px rgba(255, 255, 255, 0.45)',
              }}
            >
              {/* Radial glow background */}
              <div
                className="absolute inset-0 pointer-events-none opacity-75 group-hover:opacity-100 transition-opacity duration-300"
                style={{ background: card.glow }}
              />

              {/* Top spec shine */}
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

              {/* Card Header — Compact */}
              <div className="relative z-10 flex items-center justify-between">
                <span className="text-4xl sm:text-5xl font-black font-mono tracking-tighter bg-gradient-to-br from-white via-sky-300 to-indigo-400 bg-clip-text text-transparent opacity-90">
                  {card.num}
                </span>
                <div className="flex items-center gap-2">
                  <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-300 bg-cyan-950/70 border border-cyan-500/30">
                    {card.tag}
                  </span>
                  <div className="p-2 rounded-xl bg-white/10 border border-white/20 backdrop-blur-md shadow-md group-hover:border-sky-400/60 transition-colors">
                    {card.icon}
                  </div>
                </div>
              </div>

              {/* Card Body — Compact & Readable */}
              <div className="relative z-10 space-y-1.5">
                <h3 className="text-lg sm:text-xl font-bold font-display text-white group-hover:text-sky-300 transition-colors">
                  {card.title}
                </h3>
                <p className="text-xs sm:text-sm font-body leading-relaxed text-slate-300/90 line-clamp-3">
                  {card.desc}
                </p>
              </div>

              {/* Card Footer Indicator */}
              <div className="relative z-10 pt-2.5 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  ACTIVE NODE
                </span>
                <span className="text-sky-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-1 font-semibold">
                  EXPLORE &rarr;
                </span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
