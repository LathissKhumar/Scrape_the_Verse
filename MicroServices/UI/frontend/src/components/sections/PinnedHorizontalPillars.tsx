'use client'
import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { GradientText } from '@/components/ui/GradientText'
import {
  Palette,
  Zap,
  GitBranch,
  Radio,
  Database,
  ShieldCheck,
  Search,
  Layers,
  BrainCircuit,
  Server,
  Cpu,
} from 'lucide-react'

interface TechStackItem {
  num: string
  title: string
  tag: string
  icon: React.ReactNode
  desc: string
  glow: string
  badgeColor: string
}

const TECH_STACK: TechStackItem[] = [
  {
    num: '01',
    title: 'React & Tailwind CSS',
    tag: 'Frontend Layer',
    icon: <Palette className="w-5 h-5 text-sky-400" />,
    desc: 'Dynamic liquid glassmorphic user interface, reactive real-time telemetry dashboards, and client-side controls styled with Tailwind CSS.',
    glow: 'radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-sky-300 bg-sky-950/70 border-sky-500/30',
  },
  {
    num: '02',
    title: 'FastAPI Backend',
    tag: 'Backend Services',
    icon: <Zap className="w-5 h-5 text-emerald-400" />,
    desc: 'High-throughput asynchronous Python REST backend orchestrating scraper pipelines, webhook queues, and streaming data endpoints.',
    glow: 'radial-gradient(ellipse at top right, rgba(52, 211, 153, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-emerald-300 bg-emerald-950/70 border-emerald-500/30',
  },
  {
    num: '03',
    title: 'LangGraph Orchestrator',
    tag: 'Orchestration',
    icon: <GitBranch className="w-5 h-5 text-indigo-400" />,
    desc: 'Stateful multi-agent DAG orchestration managing complex cyclic workflows, extraction checkpoints, and decision routing.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(129, 140, 248, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-indigo-300 bg-indigo-950/70 border-indigo-500/30',
  },
  {
    num: '04',
    title: 'A2A Communication',
    tag: 'Agent-to-Agent Protocol',
    icon: <Radio className="w-5 h-5 text-cyan-300" />,
    desc: 'Decoupled Agent-to-Agent message passing and structured event bus enabling autonomous inter-service collaboration.',
    glow: 'radial-gradient(ellipse at center, rgba(56, 189, 248, 0.22) 0%, transparent 65%)',
    badgeColor: 'text-cyan-300 bg-cyan-950/70 border-cyan-500/30',
  },
  {
    num: '05',
    title: 'Bright Data Scraper Studio',
    tag: 'Web Data Ingestion',
    icon: <Database className="w-5 h-5 text-blue-400" />,
    desc: 'Industrial-grade web collection across business registries and maps with rotating residential IP mesh and anti-bot resolution.',
    glow: 'radial-gradient(ellipse at top left, rgba(96, 165, 250, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-blue-300 bg-blue-950/70 border-blue-500/30',
  },
  {
    num: '06',
    title: 'Bright Data Auto-Healing',
    tag: 'Self-Healing Engine',
    icon: <ShieldCheck className="w-5 h-5 text-violet-400" />,
    desc: 'Automated collector resilience that detects DOM structural breaks, synthesizes new extraction paths, and prevents downtime.',
    glow: 'radial-gradient(ellipse at bottom right, rgba(168, 85, 247, 0.22) 0%, transparent 65%)',
    badgeColor: 'text-violet-300 bg-violet-950/70 border-violet-500/30',
  },
  {
    num: '07',
    title: 'Screaming Frog + Crawler',
    tag: 'Deep Website Audit',
    icon: <Search className="w-5 h-5 text-amber-400" />,
    desc: 'Comprehensive website technical audits with automated open-source crawler fallback to evaluate digital presence and SEO signals.',
    glow: 'radial-gradient(ellipse at center, rgba(245, 158, 11, 0.22) 0%, transparent 65%)',
    badgeColor: 'text-amber-300 bg-amber-950/70 border-amber-500/30',
  },
  {
    num: '08',
    title: 'Chroma Vector DB',
    tag: 'RAG / Evidence Store',
    icon: <Layers className="w-5 h-5 text-rose-400" />,
    desc: 'High-density embedding store for retrieval-augmented generation (RAG), verifying lead evidence, and entity deduplication.',
    glow: 'radial-gradient(ellipse at top right, rgba(251, 113, 133, 0.22) 0%, transparent 65%)',
    badgeColor: 'text-rose-300 bg-rose-950/70 border-rose-500/30',
  },
  {
    num: '09',
    title: 'Gemini API + Ollama',
    tag: 'LLM Reasoning & Fallback',
    icon: <BrainCircuit className="w-5 h-5 text-sky-400" />,
    desc: 'Primary cloud intelligence via Google Gemini API paired with offline Ollama local LLM fallback for uninterrupted inference.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-sky-300 bg-sky-950/70 border-sky-500/30',
  },
  {
    num: '10',
    title: 'SQLite & PostgreSQL',
    tag: 'Database Persistence',
    icon: <Server className="w-5 h-5 text-emerald-400" />,
    desc: 'Zero-config SQLite for swift local development with seamless migration path to PostgreSQL for production deployments.',
    glow: 'radial-gradient(ellipse at top right, rgba(52, 211, 153, 0.22) 0%, transparent 65%)',
    badgeColor: 'text-emerald-300 bg-emerald-950/70 border-emerald-500/30',
  },
  {
    num: '11',
    title: 'Local-First Deployment',
    tag: 'Free-Tier & Local-First',
    icon: <Cpu className="w-5 h-5 text-indigo-400" />,
    desc: 'Cost-effective deployment architecture prioritizing local-first execution with free-tier cloud deployment where strictly necessary.',
    glow: 'radial-gradient(ellipse at center, rgba(129, 140, 248, 0.25) 0%, transparent 65%)',
    badgeColor: 'text-indigo-300 bg-indigo-950/70 border-indigo-500/30',
  },
]

// Duplicate for continuous seamless marquee loop
const MARQUEE_ITEMS = [...TECH_STACK, ...TECH_STACK]

export function PinnedHorizontalPillars() {
  const [isPaused, setIsPaused] = useState(false)

  return (
    <section
      id="tech-stack-marquee"
      className="py-14 md:py-18 relative border-b border-white/10 bg-transparent font-body overflow-hidden"
      aria-label="Technology Stack and Architecture"
    >
      {/* Header bar */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 w-full mb-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
          <div>
            <SectionLabel label="Integrated Technology Stack" />
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold font-display tracking-tight text-text-primary mt-1.5">
              Enterprise Tech Stack. <GradientText>Complete System Blueprint.</GradientText>
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-slate-300">11 Integrated Technologies</span>
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
        <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
          {[...Array(28)].map((_, i) => (
            <span
              key={i}
              className="absolute block rounded-full bg-sky-200/80 shadow-[0_0_12px_rgba(125,211,252,0.8)]"
              style={{
                width: `${(i % 4) + 2}px`,
                height: `${(i % 4) + 2}px`,
                left: `${(i * 11.7) % 100}%`,
                top: `${(i * 17.3) % 100}%`,
                opacity: 0.2 + (i % 5) * 0.12,
                animation: `glitterFloat ${4 + (i % 6)}s ease-in-out infinite`,
                animationDelay: `${(i % 7) * 0.6}s`,
              }}
            />
          ))}
        </div>

        {/* Subtle Edge Fade Gradients */}
        <div className="absolute left-0 top-0 bottom-0 w-16 md:w-20 bg-gradient-to-r from-black/25 to-transparent z-20 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-16 md:w-20 bg-gradient-to-l from-black/25 to-transparent z-20 pointer-events-none" />

        <motion.div
          className="flex items-center gap-6 w-max will-change-transform py-2"
          animate={{
            x: isPaused ? undefined : ['0%', '-50%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: 'loop',
              duration: 70,
              ease: 'linear',
            },
          }}
        >
          {MARQUEE_ITEMS.map((card, idx) => (
            <motion.div
              key={`${card.num}-${idx}`}
              whileHover={{ y: -4, scale: 1.02 }}
              data-cursor-hover
              className="w-[320px] sm:w-[360px] md:w-[390px] h-[280px] rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden shrink-0 glass-liquid border border-white/25 shadow-xl backdrop-blur-2xl transition-all duration-300 group"
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

              {/* Card Header */}
              <div className="relative z-10 flex items-center justify-between">
                <span className="text-4xl sm:text-5xl font-black font-mono tracking-tighter bg-gradient-to-br from-white via-sky-300 to-indigo-400 bg-clip-text text-transparent opacity-90">
                  {card.num}
                </span>
                <span className="inline-block px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border border-sky-300/35 bg-sky-500/10 text-sky-100 backdrop-blur-md shadow-sm shadow-sky-500/10">
                  {card.tag}
                </span>
              </div>

              {/* Card Body with Techstack Logo alongside its Name */}
              <div className="relative z-10 space-y-2.5">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-white/10 border border-white/20 backdrop-blur-md shadow-md group-hover:border-sky-400/60 group-hover:bg-white/15 transition-all shrink-0 flex items-center justify-center">
                    {card.icon}
                  </div>
                  <h3 className="text-lg sm:text-xl font-bold font-display text-white group-hover:text-sky-300 transition-colors leading-tight">
                    {card.title}
                  </h3>
                </div>
                <TypewriterDescription text={card.desc} />
              </div>

              {/* Card Footer Indicator */}
              <div className="relative z-10 pt-2.5 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  ACTIVE STACK
                </span>
                <span className="text-sky-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-1 font-semibold">
                  INTEGRATED &rarr;
                </span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function TypewriterDescription({ text }: { text: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [displayedText, setDisplayedText] = useState('')
  const [isDone, setIsDone] = useState(false)
  const hasStartedRef = useRef(false)

  useEffect(() => {
    let animFrame: number
    let typeInterval: NodeJS.Timeout | null = null

    const checkPosition = () => {
      const el = containerRef.current
      if (!el) {
        animFrame = requestAnimationFrame(checkPosition)
        return
      }

      const rect = el.getBoundingClientRect()
      // Triggers typing as soon as the card enters within the website frame / viewport
      const isInFrame = rect.right > 0 && rect.left < window.innerWidth

      if (isInFrame && !hasStartedRef.current) {
        hasStartedRef.current = true
        let charIndex = 0
        setDisplayedText('')
        setIsDone(false)

        typeInterval = setInterval(() => {
          if (charIndex < text.length) {
            setDisplayedText(text.slice(0, charIndex + 1))
            charIndex++
          } else {
            setIsDone(true)
            if (typeInterval) clearInterval(typeInterval)
          }
        }, 75)
      } else if (!hasStartedRef.current) {
        // Keep checking on next frame until the card reaches the frame
        animFrame = requestAnimationFrame(checkPosition)
      }
    }

    animFrame = requestAnimationFrame(checkPosition)

    return () => {
      cancelAnimationFrame(animFrame)
      if (typeInterval) clearInterval(typeInterval)
    }
  }, [text])

  return (
    <div ref={containerRef} className="min-h-[60px] sm:min-h-[66px] flex items-start">
      <p className="text-xs sm:text-sm font-body leading-relaxed text-slate-300/95 line-clamp-3">
        <span>{displayedText}</span>
        <motion.span
          className="inline-block w-[2px] h-3.5 ml-1 align-middle bg-cyan-400 shadow-[0_0_8px_#38bdf8]"
          animate={{ opacity: isDone ? [1, 0, 1] : 1 }}
          transition={{ duration: 0.7, repeat: Infinity, ease: 'easeInOut' }}
        />
      </p>
    </div>
  )
}
