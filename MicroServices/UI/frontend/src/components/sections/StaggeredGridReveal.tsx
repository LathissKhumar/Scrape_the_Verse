'use client'
import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { GradientText } from '@/components/ui/GradientText'
import { ArrowUpRight } from 'lucide-react'

const GRID_CARDS = [
  {
    emoji: '🌐',
    title: 'Nebula Stream Engine',
    desc: 'Real-time WebSocket event ingestion pipeline streaming 50M+ structural changes per day with sub-16ms latency.',
    tech: 'Rust · WebSockets · Edge',
  },
  {
    emoji: '🧬',
    title: 'DOM Genome Mapper',
    desc: 'Deep hierarchical element fingerprinting that traces selector ancestry across responsive breakpoints.',
    tech: 'Vision AI · Tree Matching',
  },
  {
    emoji: '🤖',
    title: 'AgentFlow Orchestrator',
    desc: 'Autonomous multi-agent DAG builder that converts raw extraction feeds directly into enriched CRM opportunities.',
    tech: 'AI Agents · TypeScript · Queue',
  },
  {
    emoji: '🛰️',
    title: 'Orbit Proxy Constellation',
    desc: 'Dynamic rotating residential IP mesh operating across 195 countries with automatic captcha resolution.',
    tech: 'Bright Data · TLS Fingerprint',
  },
  {
    emoji: '💎',
    title: 'Prism Schema Engine',
    desc: 'Self-adapting JSON-LD and microdata normalizer with automated duplicate entity deduplication.',
    tech: 'Vector Search · Embeddings',
  },
  {
    emoji: '🔮',
    title: 'Spectra Vision Inspector',
    desc: 'Visual LLM inspection that evaluates screenshots to extract unindexed pricing cards and hidden canvas menus.',
    tech: 'Gemini Vision · OCR · D3',
  },
  {
    emoji: '🌊',
    title: 'FlowState Rate Balancer',
    desc: 'Adaptive machine-learning throttler that predicts server limits and scales request pools without triggering 429s.',
    tech: 'Dynamic EBPF · Go · Redis',
  },
  {
    emoji: '⚡',
    title: 'Volt Anomaly Radar',
    desc: 'Continuous real-time sentinel alerting teams instantly when target website structural shifts cross error thresholds.',
    tech: 'ClickHouse · Vector Logs',
  },
  {
    emoji: '🎨',
    title: 'Synthetic Landing Studio',
    desc: 'Instant generation of personalized enterprise pitch decks and dynamic micro-sites for hot discovered leads.',
    tech: 'Next.js 16 · Tailwind · Canvas',
  },
]

export function StaggeredGridReveal() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="grid-reveal"
      ref={ref}
      className="py-32 md:py-44 relative border-b border-white/10 bg-transparent font-body overflow-hidden"
      aria-label="3x3 Staggered Grid Intelligence Modules"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-20">
        {/* Header */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <SectionLabel stage="04" label="Modular Architecture" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Nine Modules. <GradientText>Infinite Coverage.</GradientText>
          </h2>
          <p className="text-base text-text-secondary font-body max-w-xl mx-auto">
            Discover the modular subsystems that power our self-healing extraction pipeline. Hover to inspect 3D perspective dynamics.
          </p>
        </div>

        {/* 3x3 3D Perspective Grid */}
        <div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto"
          style={{ perspective: '1200px' }}
        >
          {GRID_CARDS.map((card, i) => (
            <TiltProjectCard key={card.title} card={card} index={i} isInView={isInView} />
          ))}
        </div>
      </div>
    </section>
  )
}

function TiltProjectCard({
  card,
  index,
  isInView,
}: {
  card: typeof GRID_CARDS[number]
  index: number
  isInView: boolean
}) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5
    setRotateY(x * 16)
    setRotateX(-y * 16)
  }

  const handleMouseLeave = () => {
    setRotateX(0)
    setRotateY(0)
    setIsHovered(false)
  }

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, rotateY: 82, rotateX: -8, scale: 0.94 }}
      animate={
        isInView
          ? {
              opacity: 1,
              rotateY: [0, 15, 0, -15, 0],
              rotateX: [0, -7, 0, 7, 0],
              y: [0, -8, 0],
              scale: 1,
            }
          : { opacity: 0, rotateY: 82, rotateX: -8, scale: 0.94 }
      }
      transition={{
        opacity: { duration: 0.7, delay: (index % 3) * 0.2 + Math.floor(index / 3) * 0.2 },
        rotateY: {
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: (index % 3) * 0.25 + Math.floor(index / 3) * 0.18,
        },
        rotateX: {
          duration: 12,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: (index % 3) * 0.3 + Math.floor(index / 3) * 0.22,
        },
        y: {
          duration: 7,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: (index % 3) * 0.2,
        },
        scale: { duration: 0.8, delay: (index % 3) * 0.18 + Math.floor(index / 3) * 0.2 },
      }}
      whileHover={{
        scale: 1.02,
        y: -10,
        rotateY: 0,
        rotateX: 0,
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      data-cursor-hover
      className="relative rounded-3xl p-8 min-h-[280px] flex flex-col justify-between glass-level-3 border border-white/25 shadow-2xl backdrop-blur-xl cursor-none transition-shadow duration-300 will-change-transform group"
      style={{
        transformStyle: 'preserve-3d',
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) ${
          isHovered ? 'translateZ(20px)' : 'translateZ(0px)'
        }`,
        boxShadow: isHovered
          ? '0 25px 60px rgba(56, 189, 248, 0.25), inset 0 1.5px 2px rgba(255, 255, 255, 0.6)'
          : '0 15px 40px rgba(0, 0, 0, 0.3), inset 0 1px 1.5px rgba(255, 255, 255, 0.3)',
      }}
    >
      {/* Dynamic Hover Radial Glow */}
      <div
        className="absolute inset-0 rounded-3xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background: 'radial-gradient(circle at center, rgba(56, 189, 248, 0.2) 0%, transparent 70%)',
        }}
      />

      {/* Card Header & Content */}
      <div className="relative z-10 space-y-3">
        <span className="text-4xl select-none block leading-none">{card.emoji}</span>
        <h3 className="text-xl font-bold font-display text-text-primary group-hover:text-sky-300 transition-colors">
          {card.title}
        </h3>
        <p className="text-sm font-body text-slate-300/80 leading-relaxed">{card.desc}</p>
      </div>

      {/* Card Footer */}
      <div className="relative z-10 pt-4 border-t border-white/10 flex items-center justify-between">
        <span className="text-xs font-mono font-bold tracking-wider uppercase text-cyan-300">
          {card.tech}
        </span>
        <div className="p-2 rounded-full bg-white/10 border border-white/20 group-hover:border-sky-400 group-hover:bg-sky-500/20 transition-all">
          <ArrowUpRight className="w-4 h-4 text-sky-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
        </div>
      </div>
    </motion.div>
  )
}
