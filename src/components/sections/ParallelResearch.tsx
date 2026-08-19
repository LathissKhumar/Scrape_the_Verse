'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'
import { ComicPanel } from '@/components/ui/ComicPanel'
import { RESEARCH_COLLECTORS } from '@/lib/mock-data'

export function ParallelResearch() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="parallel-research" ref={ref} className="py-24 relative" aria-label="Parallel Web Research">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel stage="02" label="Parallel Web Research" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            One prospect.{' '}
            <GradientText>Four dimensions</GradientText> of intelligence.
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            After discovering a prospect, four independent collectors run simultaneously — no waiting, no sequential bottleneck.
          </p>
        </div>

        {/* Fan-out */}
        <div className="flex flex-col items-center gap-4 mb-10">
          <div
            className="comic-panel px-6 py-3 text-center"
            style={{ backgroundColor: 'rgba(36,0,68,0.4)' }}
          >
            <div className="font-bold font-mono" style={{ color: '#EC0AFF' }}>PROSPECT</div>
            <div className="text-xs font-mono mt-0.5" style={{ color: '#A1A1B5' }}>Urban Brew Café</div>
          </div>
          <div className="w-px h-8" style={{ background: 'linear-gradient(to bottom, #EC0AFF, transparent)' }} />
          <div className="text-xs font-mono tracking-widest" style={{ color: '#A1A1B5' }}>
            PARALLEL COLLECTORS ACTIVATED
          </div>
        </div>

        {/* 4 collector cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {RESEARCH_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={!prefersReduced ? { opacity: 0, y: 30, scale: 0.95 } : false}
              animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5, ease: 'easeOut' }}
            >
              <ComicPanel className="p-5 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-sm" style={{ fontFamily: 'var(--font-display)', color: '#F8FAFC' }}>
                    {collector.title}
                  </span>
                  <NeonBadge label="Scraping" variant="running" />
                </div>
                <div className="space-y-2">
                  {collector.metrics.map((m) => (
                    <div key={m.label} className="flex items-center justify-between text-xs font-mono">
                      <span style={{ color: '#A1A1B5' }}>{m.label}</span>
                      <span style={{ color: '#00E5FF' }}>{m.value}</span>
                    </div>
                  ))}
                </div>
              </ComicPanel>
            </motion.div>
          ))}
        </div>

        {/* Converge */}
        <motion.div
          className="flex flex-col items-center gap-3 mt-10"
          initial={!prefersReduced ? { opacity: 0 } : false}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.7 }}
        >
          <div className="w-px h-10" style={{ background: 'linear-gradient(to bottom, transparent, #00E5FF)' }} />
          <div
            className="comic-panel px-8 py-4 text-center"
            style={{ borderColor: 'rgba(0,229,255,0.4)', backgroundColor: 'rgba(0,229,255,0.06)' }}
          >
            <div className="font-bold tracking-wider font-mono" style={{ color: '#00E5FF' }}>
              UNIFIED BUSINESS INTELLIGENCE
            </div>
            <div className="text-xs font-mono mt-1" style={{ color: '#A1A1B5' }}>
              Lead Score: 92/100 · Opportunity: High
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
