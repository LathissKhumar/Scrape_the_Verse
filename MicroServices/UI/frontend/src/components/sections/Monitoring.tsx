'use client'
import { motion, useInView } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'
import { Radio, Bell, ArrowRight } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { MONITORING_PROSPECTS } from '@/lib/mock-data'

const STATS = [
  {
    target: 98,
    suffix: '%',
    label: 'Self-Healing Accuracy',
    sub: 'XPath structural recovery rate without human intervention',
    ratio: 0.98,
    gradient: 'from-sky-400 to-cyan-300',
    color: '#38BDF8',
  },
  {
    target: 500,
    suffix: 'M+',
    label: 'Records Indexed Daily',
    sub: 'Parallel streaming crawlers with Bright Data proxy mesh',
    ratio: 0.85,
    gradient: 'from-indigo-400 to-sky-400',
    color: '#818CF8',
  },
  {
    target: 12,
    suffix: 'ms',
    label: 'Global Edge Latency',
    sub: 'Ultra-low latency extraction cache distributed across 42 regions',
    ratio: 0.72,
    gradient: 'from-emerald-400 to-cyan-400',
    color: '#34D399',
  },
]

export function Monitoring() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <section
      id="monitoring"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Post-Outreach Monitoring"
    >
      {/* SVG Definitions for SVG Rings */}
      <svg width="0" height="0" className="absolute pointer-events-none">
        <defs>
          <linearGradient id="stat-grad-1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="100%" stopColor="#00d4ff" />
          </linearGradient>
          <linearGradient id="stat-grad-2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#818CF8" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
          <linearGradient id="stat-grad-3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
        </defs>
      </svg>

      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-24">
        {/* Header */}
        <motion.div
          className="text-center space-y-4 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="06" label="Real-time Platform Metrics" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Proven Performance <GradientText>By The Numbers.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            High-throughput web scraping backed by self-repairing machine vision models and global proxy networks.
          </p>
        </motion.div>

        {/* 3 Morphing Number Counters with SVG Animated Progress Rings */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {STATS.map((stat, i) => (
            <StatProgressCard key={stat.label} stat={stat} index={i} isInView={isInView} />
          ))}
        </div>

        {/* Live Prospect Monitoring Cards */}
        <motion.div
          className="max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="glass-level-3 p-8 space-y-6 border-white/20 shadow-2xl rounded-3xl backdrop-blur-2xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <span className="font-mono text-xs text-muted uppercase flex items-center gap-2">
                <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
                <span className="text-slate-200">MONITORED PROSPECT WATCHLIST</span>
              </span>
              <span className="text-xs font-mono text-emerald-400 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>24 ACTIVE MONITORS</span>
              </span>
            </div>

            <div className="space-y-4">
              {MONITORING_PROSPECTS.map((prospect) => (
                <div
                  key={prospect.id}
                  data-cursor-hover
                  className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:border-sky-400/40 transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="font-bold font-display text-lg text-text-primary flex items-center gap-2">
                      <span>{prospect.name}</span>
                      <span className="text-xs font-mono text-muted">({prospect.location})</span>
                    </div>
                    <div className="text-xs font-mono text-rose-400 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                      <span>Target: {prospect.website}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1.5 rounded-xl text-xs font-mono bg-sky-500/15 text-sky-400 border border-sky-400/30 font-semibold flex items-center gap-1.5">
                      <Bell className="w-3.5 h-3.5 text-sky-400" />
                      <span>Live Watch Active</span>
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-400 hidden sm:inline" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function StatProgressCard({
  stat,
  index,
  isInView,
}: {
  stat: typeof STATS[number]
  index: number
  isInView: boolean
}) {
  const [count, setCount] = useState(0)
  const radius = 54
  const circumference = 2 * Math.PI * radius

  useEffect(() => {
    if (!isInView) return
    let start = 0
    const duration = 2000
    const startTime = performance.now()

    const updateCounter = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(easeProgress * stat.target))

      if (progress < 1) {
        requestAnimationFrame(updateCounter)
      } else {
        setCount(stat.target)
      }
    }

    const frameId = requestAnimationFrame(updateCounter)
    return () => cancelAnimationFrame(frameId)
  }, [isInView, stat.target])

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.15, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -6, scale: 1.02 }}
      data-cursor-hover
      className="glass-level-2 p-8 rounded-3xl border border-white/20 shadow-2xl flex flex-col items-center text-center space-y-6 relative overflow-hidden group"
    >
      {/* Radial glow */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20 group-hover:opacity-40 transition-opacity duration-500"
        style={{
          background: `radial-gradient(circle at center, ${stat.color} 0%, transparent 70%)`,
        }}
      />

      {/* SVG Progress Ring */}
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
          {/* Background circle */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="6"
          />
          {/* Progress circle */}
          <motion.circle
            cx="64"
            cy="64"
            r={radius}
            fill="none"
            stroke={`url(#stat-grad-${index + 1})`}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={isInView ? { strokeDashoffset: circumference * (1 - stat.ratio) } : {}}
            transition={{ duration: 2.2, delay: 0.2 + index * 0.15, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>

        {/* Center counter */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-3xl sm:text-4xl font-black text-white tabular-nums leading-none whitespace-nowrap">
            {count}
            <span className="text-sky-400 text-2xl sm:text-3xl align-middle">{stat.suffix}</span>
          </span>
        </div>
      </div>

      <div className="space-y-2 relative z-10">
        <h3 className="text-xl font-bold font-display text-text-primary">{stat.label}</h3>
        <p className="text-xs text-text-secondary leading-relaxed max-w-xs">{stat.sub}</p>
      </div>
    </motion.div>
  )
}
