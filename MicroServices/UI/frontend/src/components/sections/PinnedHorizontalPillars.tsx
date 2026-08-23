'use client'
import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { GradientText } from '@/components/ui/GradientText'
import {
  Globe,
  Dna,
  Bot,
  Satellite,
  Gem,
  Sparkles,
  Waves,
  Zap,
  Paintbrush,
} from 'lucide-react'

interface ModuleItem {
  num: string
  title: string
  tag: string
  icon: React.ReactNode
  desc: string
  glow: string
}

const NINE_MODULES: ModuleItem[] = [
  {
    num: '01',
    title: 'Nebula Stream Engine',
    tag: 'Rust · WebSockets · Edge',
    icon: <Globe className="w-5 h-5 text-sky-400" />,
    desc: 'Real-time WebSocket event ingestion pipeline streaming 50M+ structural changes per day with sub-16ms latency.',
    glow: 'radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)',
  },
  {
    num: '02',
    title: 'DOM Genome Mapper',
    tag: 'Vision AI · Tree Matching',
    icon: <Dna className="w-5 h-5 text-emerald-400" />,
    desc: 'Deep hierarchical element fingerprinting that traces selector ancestry across responsive breakpoints.',
    glow: 'radial-gradient(ellipse at top right, rgba(52, 211, 153, 0.25) 0%, transparent 65%)',
  },
  {
    num: '03',
    title: 'AgentFlow Orchestrator',
    tag: 'AI Agents · TypeScript · Queue',
    icon: <Bot className="w-5 h-5 text-indigo-400" />,
    desc: 'Autonomous multi-agent DAG builder that converts raw extraction feeds directly into enriched CRM opportunities.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(129, 140, 248, 0.25) 0%, transparent 65%)',
  },
  {
    num: '04',
    title: 'Orbit Proxy Constellation',
    tag: 'Bright Data · TLS Fingerprint',
    icon: <Satellite className="w-5 h-5 text-violet-400" />,
    desc: 'Dynamic rotating residential IP mesh operating across 195 countries with automatic captcha resolution.',
    glow: 'radial-gradient(ellipse at center, rgba(168, 85, 247, 0.25) 0%, transparent 65%)',
  },
  {
    num: '05',
    title: 'Prism Schema Engine',
    tag: 'Vector Search · Embeddings',
    icon: <Gem className="w-5 h-5 text-cyan-400" />,
    desc: 'Self-adapting JSON-LD and microdata normalizer with automated duplicate entity deduplication.',
    glow: 'radial-gradient(ellipse at top left, rgba(34, 211, 238, 0.25) 0%, transparent 65%)',
  },
  {
    num: '06',
    title: 'Spectra Vision Inspector',
    tag: 'Gemini Vision · OCR · D3',
    icon: <Sparkles className="w-5 h-5 text-fuchsia-400" />,
    desc: 'Visual LLM inspection that evaluates screenshots to extract unindexed pricing cards and hidden canvas menus.',
    glow: 'radial-gradient(ellipse at bottom right, rgba(232, 121, 249, 0.25) 0%, transparent 65%)',
  },
  {
    num: '07',
    title: 'FlowState Rate Balancer',
    tag: 'Dynamic EBPF · Go · Redis',
    icon: <Waves className="w-5 h-5 text-teal-400" />,
    desc: 'Adaptive machine-learning throttler that predicts server limits and scales request pools without triggering 429s.',
    glow: 'radial-gradient(ellipse at center, rgba(45, 212, 191, 0.25) 0%, transparent 65%)',
  },
  {
    num: '08',
    title: 'Volt Anomaly Radar',
    tag: 'ClickHouse · Vector Logs',
    icon: <Zap className="w-5 h-5 text-amber-400" />,
    desc: 'Continuous real-time sentinel alerting teams instantly when target website structural shifts cross error thresholds.',
    glow: 'radial-gradient(ellipse at top right, rgba(251, 191, 36, 0.25) 0%, transparent 65%)',
  },
  {
    num: '09',
    title: 'Synthetic Landing Studio',
    tag: 'Next.js 16 · Tailwind · Canvas',
    icon: <Paintbrush className="w-5 h-5 text-rose-400" />,
    desc: 'Instant generation of personalized enterprise pitch decks and dynamic micro-sites for hot discovered leads.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(251, 113, 133, 0.25) 0%, transparent 65%)',
  },
]

// Duplicate for continuous seamless marquee loop
const MARQUEE_ITEMS = [...NINE_MODULES, ...NINE_MODULES]

export function PinnedHorizontalPillars() {
  return (
    <section
      id="tech-stack-marquee"
      className="py-8 md:py-12 relative border-b border-white/10 bg-transparent font-body overflow-hidden"
      aria-label="Modular Architecture Subsystems"
    >
      {/* Header bar */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 w-full mb-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
          <div>
            <SectionLabel stage="04" label="Modular Architecture" />
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold font-display tracking-tight text-text-primary mt-1.5">
              Nine Modules. <GradientText>Infinite Coverage.</GradientText>
            </h2>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-slate-300">9 Core Subsystems</span>
          </div>
        </div>
      </div>

      {/* Continuously Moving Horizontal Marquee Track */}
      <div className="relative w-full overflow-hidden">
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

        <motion.div
          className="flex items-center gap-6 w-max will-change-transform py-2"
          animate={{
            x: ['-50%', '0%'],
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
              key={`${card.title}-${idx}`}
              whileHover={{ y: -4, scale: 1.02 }}
              data-cursor-hover
              className="w-[300px] sm:w-[340px] md:w-[360px] h-[200px] sm:h-[210px] rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden shrink-0 glass-liquid border border-white/25 shadow-xl backdrop-blur-2xl transition-all duration-300 group"
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

              {/* Card Header & Title with Techstack Icon */}
              <div className="relative z-10 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="p-1.5 rounded-xl bg-white/10 border border-white/20 backdrop-blur-md shadow-md group-hover:border-sky-400/60 group-hover:bg-white/15 transition-all shrink-0 flex items-center justify-center">
                    {card.icon}
                  </div>
                  <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border border-sky-300/35 bg-sky-500/10 text-sky-100 backdrop-blur-md shadow-sm">
                    {card.tag}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold font-display text-white group-hover:text-sky-300 transition-colors leading-tight">
                  {card.title}
                </h3>
              </div>

              {/* Card Body with Typewriter text */}
              <div className="relative z-10">
                <TypewriterDescription text={card.desc} />
              </div>

              {/* Card Footer Indicator */}
              <div className="relative z-10 pt-2 border-t border-white/10 flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400 font-semibold">
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
    <div ref={containerRef} className="min-h-[44px] flex items-start">
      <p className="text-xs font-body leading-relaxed text-slate-300/95 line-clamp-2">
        <span>{displayedText}</span>
        <motion.span
          className="inline-block w-[2px] h-3 ml-0.5 align-middle bg-cyan-400 shadow-[0_0_8px_#38bdf8]"
          animate={{ opacity: isDone ? [1, 0, 1] : 1 }}
          transition={{ duration: 0.7, repeat: Infinity, ease: 'easeInOut' }}
        />
      </p>
    </div>
  )
}
