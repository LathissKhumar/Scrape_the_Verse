'use client'
import { motion, useReducedMotion } from 'framer-motion'
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
  const prefersReduced = useReducedMotion()
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (prefersReduced) { setCount(TOTAL); return }
    let current = 0
    const step = Math.ceil(TOTAL / 60)
    const id = setInterval(() => {
      current = Math.min(current + step, TOTAL)
      setCount(current)
      if (current >= TOTAL) clearInterval(id)
    }, 20)
    return () => clearInterval(id)
  }, [prefersReduced])

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      aria-label="Hero — Scrape-Verse self-healing web intelligence"
    >
      {/* Canvas background */}
      <div className="absolute inset-0 opacity-35">
        <WebCanvas nodes={HERO_NODES} edges={HERO_EDGES} />
      </div>

      {/* Halftone */}
      <div className="absolute inset-0 halftone opacity-25 pointer-events-none" />

      {/* Vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 30%, #05050A 80%)',
        }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-16 grid lg:grid-cols-2 gap-16 items-center w-full">
        {/* Left */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <div
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-mono mb-6"
            style={{
              color: '#EC0AFF',
              borderColor: 'rgba(236,10,255,0.3)',
              backgroundColor: 'rgba(236,10,255,0.05)',
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: '#EC0AFF', animation: 'pulse 2s infinite' }}
            />
            SELF-HEALING WEB INTELLIGENCE
          </div>

          <h1
            className="text-5xl lg:text-7xl font-black leading-tight mb-6"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            The Web
            <br />
            Changes.{' '}
            <GradientText>
              Your
              <br />
              Scrapers
              <br />
              Adapt.
            </GradientText>
          </h1>

          <p className="text-lg leading-relaxed mb-8 max-w-lg" style={{ color: '#A1A1B5' }}>
            Self-healing web intelligence that discovers prospects, researches
            businesses, detects opportunities, and powers autonomous sales
            workflows.
          </p>

          <div className="flex flex-wrap gap-4">
            <Button id="hero-cta-primary" variant="primary">
              Explore the Scraping Engine
            </Button>
            <Button id="hero-cta-secondary" variant="secondary">
              See Self-Healing in Action
            </Button>
          </div>
        </motion.div>

        {/* Right — live collector card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
          className="comic-panel p-6 space-y-4"
          style={{ backgroundColor: 'rgba(8,8,16,0.85)', backdropFilter: 'blur(8px)' }}
        >
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs tracking-widest" style={{ color: '#A1A1B5' }}>
              SCRAPE-VERSE
            </span>
            <span className="flex items-center gap-1.5 text-xs font-mono" style={{ color: '#00E5FF' }}>
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: '#00E5FF', animation: 'pulse 2s infinite' }}
              />
              LIVE
            </span>
          </div>

          <div className="space-y-1">
            {[
              ['Target', 'Restaurants'],
              ['Location', 'Austin, TX'],
              ['Criteria', 'No Website'],
            ].map(([label, value]) => (
              <div key={label} className="text-sm font-mono" style={{ color: '#A1A1B5' }}>
                {label}:{' '}
                <span style={{ color: '#F8FAFC' }}>{value}</span>
              </div>
            ))}
          </div>

          <div
            className="space-y-3 border-t pt-4"
            style={{ borderColor: 'rgba(255,255,255,0.08)' }}
          >
            {DISCOVERY_SOURCES.map((source, i) => (
              <motion.div
                key={source.name}
                className="flex items-center justify-between"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + i * 0.2 }}
              >
                <span className="flex items-center gap-2 text-sm font-mono" style={{ color: '#A1A1B5' }}>
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: source.color, animation: 'pulse 2s infinite' }}
                  />
                  {source.name}
                </span>
                <span className="font-mono text-sm tabular-nums" style={{ color: source.color }}>
                  {source.records.toLocaleString()} records
                </span>
              </motion.div>
            ))}
          </div>

          <div
            className="border-t pt-4 flex items-center justify-between"
            style={{ borderColor: 'rgba(255,255,255,0.08)' }}
          >
            <span className="text-sm font-mono" style={{ color: '#A1A1B5' }}>
              TOTAL
            </span>
            <span
              className="text-3xl font-black tabular-nums"
              style={{
                fontFamily: 'var(--font-display)',
                background:
                  'linear-gradient(135deg, #EC0AFF, #00E5FF)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {count.toLocaleString()} LEADS
            </span>
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div
          className="w-5 h-8 rounded-full flex justify-center pt-1.5"
          style={{ border: '1px solid rgba(161,161,181,0.3)' }}
        >
          <div
            className="w-1 h-2 rounded-full"
            style={{ backgroundColor: '#EC0AFF' }}
          />
        </div>
      </motion.div>
    </section>
  )
}
