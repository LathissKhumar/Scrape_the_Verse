'use client'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'
import { WebCanvas } from '@/components/ui/WebCanvas'
import { DISCOVERY_SOURCES } from '@/lib/mock-data'

const HERO_NODES = [
  { x: 0.5, y: 0.5, color: '#EC0AFF', radius: 10 },
  { x: 0.15, y: 0.2, label: 'Google Maps', color: '#00E5FF', radius: 6 },
  { x: 0.8, y: 0.15, label: 'Yelp', color: '#EC0AFF', radius: 5 },
  { x: 0.1, y: 0.7, label: 'Directories', color: '#6D28D9', radius: 5 },
  { x: 0.85, y: 0.75, label: 'Social', color: '#FF1744', radius: 5 },
  { x: 0.6, y: 0.08, label: 'Reviews', color: '#00E5FF', radius: 4 },
  { x: 0.25, y: 0.88, label: 'Competitors', color: '#EC0AFF', radius: 4 },
  { x: 0.92, y: 0.42, label: 'Websites', color: '#6D28D9', radius: 4 },
]

const HERO_EDGES = [
  { from: 0, to: 1, color: '#00E5FF', animated: true },
  { from: 0, to: 2, color: '#EC0AFF', animated: true },
  { from: 0, to: 3, color: '#6D28D9', animated: true },
  { from: 0, to: 4, color: '#FF1744', animated: true },
  { from: 0, to: 5, color: '#00E5FF', animated: true },
  { from: 0, to: 6, color: '#EC0AFF', animated: true },
  { from: 0, to: 7, color: '#6D28D9', animated: true },
  { from: 1, to: 5, color: 'rgba(109,40,217,0.2)', animated: false },
  { from: 2, to: 4, color: 'rgba(109,40,217,0.2)', animated: false },
]

const TOTAL = DISCOVERY_SOURCES.reduce((s, d) => s + d.records, 0)

export function Hero() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let current = 0
    const step = Math.ceil(TOTAL / 60)
    const id = setInterval(() => {
      current = Math.min(current + step, TOTAL)
      setCount(current)
      if (current >= TOTAL) clearInterval(id)
    }, 20)
    return () => clearInterval(id)
  }, [])

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center pt-28 pb-20 overflow-hidden border-b border-white/5"
      aria-label="Hero — Scrape-Verse self-healing web intelligence"
    >
      {/* Canvas background */}
      <div className="absolute inset-0 opacity-40">
        <WebCanvas nodes={HERO_NODES} edges={HERO_EDGES} />
      </div>

      {/* Halftone */}
      <div className="absolute inset-0 halftone opacity-30 pointer-events-none" />

      {/* Radial Glow */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none opacity-20 blur-[120px]"
        style={{
          background: 'radial-gradient(circle, #EC0AFF 0%, #6D28D9 50%, transparent 80%)',
        }}
      />

      {/* Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 grid lg:grid-cols-12 gap-12 lg:gap-16 items-center w-full">
        {/* Left column */}
        <motion.div
          className="lg:col-span-7 space-y-8"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <div
            className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border text-xs font-mono tracking-wider backdrop-blur-md"
            style={{
              color: '#EC0AFF',
              borderColor: 'rgba(236,10,255,0.35)',
              backgroundColor: 'rgba(236,10,255,0.08)',
            }}
          >
            <span
              className="w-2 h-2 rounded-full animate-ping"
              style={{ backgroundColor: '#EC0AFF' }}
            />
            SELF-HEALING WEB INTELLIGENCE
          </div>

          <h1
            className="text-5xl sm:text-6xl lg:text-7xl font-black font-display leading-[1.08] tracking-tight"
          >
            The Web Changes.
            <br />
            <GradientText className="py-1">
              Your Scrapers Adapt.
            </GradientText>
          </h1>

          <p className="text-lg sm:text-xl font-body leading-relaxed text-muted max-w-xl">
            Autonomous web intelligence platform that discovers leads, self-heals when target sites change structure, and delivers AI-driven sales automation.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <Button id="hero-cta-primary" variant="primary" className="!text-sm !px-7 !py-3.5 shadow-xl shadow-magenta/25">
              Explore Scraping Engine
            </Button>
            <Button id="hero-cta-secondary" variant="secondary" className="!text-sm !px-7 !py-3.5 backdrop-blur-md">
              See Self-Healing in Action
            </Button>
          </div>
        </motion.div>

        {/* Right column — Live Glass Card */}
        <motion.div
          className="lg:col-span-5"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
        >
          <div className="glass-panel p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <span className="font-mono text-xs tracking-widest text-muted">
                SCRAPE-VERSE MONITOR
              </span>
              <span className="flex items-center gap-2 text-xs font-mono text-cyan">
                <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
                LIVE STREAM
              </span>
            </div>

            <div className="space-y-2 font-mono text-xs">
              {[
                ['Target Industry', 'Restaurants & Dining'],
                ['Location Filter', 'Austin, Texas'],
                ['Discovery Criteria', 'High Rating / Missing Website'],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between items-center py-1">
                  <span className="text-muted">{label}:</span>
                  <span className="text-off-white font-medium">{value}</span>
                </div>
              ))}
            </div>

            <div className="space-y-3 border-t border-white/10 pt-5">
              {DISCOVERY_SOURCES.map((source, i) => (
                <motion.div
                  key={source.name}
                  className="flex items-center justify-between font-mono text-sm"
                  initial={{ opacity: 0, x: 15 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.15 }}
                >
                  <span className="flex items-center gap-2 text-muted">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: source.color }}
                    />
                    {source.name}
                  </span>
                  <span className="font-semibold tabular-nums" style={{ color: source.color }}>
                    {source.records.toLocaleString()} leads
                  </span>
                </motion.div>
              ))}
            </div>

            <div className="border-t border-white/10 pt-5 flex items-center justify-between">
              <span className="text-xs font-mono tracking-wider text-muted">TOTAL OPPORTUNITIES</span>
              <span
                className="text-3xl font-black font-display tabular-nums"
                style={{
                  background: 'linear-gradient(135deg, #EC0AFF, #00E5FF)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                {count.toLocaleString()}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-6 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 rounded-full border border-white/20 flex justify-center pt-2 backdrop-blur-sm">
          <div className="w-1.5 h-2.5 rounded-full bg-magenta" />
        </div>
      </motion.div>
    </section>
  )
}
