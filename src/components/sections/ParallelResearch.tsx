'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'
import { RESEARCH_COLLECTORS } from '@/lib/mock-data'

export function ParallelResearch() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="parallel-research" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Parallel Web Research">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="02" label="Parallel Web Research" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            One Prospect.{' '}
            <GradientText>Four Dimensions</GradientText> of Intelligence.
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            After discovering a target lead, four specialized collectors execute concurrently to gather multi-dimensional intelligence in under 15 seconds.
          </p>
        </div>

        {/* Fan-out header node */}
        <div className="flex flex-col items-center gap-4 mb-14">
          <div className="glass-panel px-8 py-4 text-center border-magenta/40 shadow-lg shadow-magenta/10">
            <div className="font-bold font-mono text-base text-magenta">TARGET PROSPECT</div>
            <div className="text-xs font-mono text-muted mt-1">Urban Brew Café · Austin, TX</div>
          </div>
          <div className="w-px h-10 bg-gradient-to-b from-magenta to-transparent" />
          <span className="text-xs font-mono tracking-widest text-muted uppercase">
            CONCURRENT SCRAPER EXECUTION
          </span>
        </div>

        {/* 4 Collector cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {RESEARCH_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5, ease: 'easeOut' }}
            >
              <div className="glass-card p-6 h-full space-y-4 flex flex-col justify-between">
                <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-3">
                  <span className="font-bold text-base font-display text-off-white">
                    {collector.title}
                  </span>
                  <NeonBadge label="SCRAPING" variant="running" />
                </div>
                <div className="space-y-2.5 font-mono text-xs">
                  {collector.metrics.map((m) => (
                    <div key={m.label} className="flex items-center justify-between">
                      <span className="text-muted">{m.label}</span>
                      <span className="text-cyan font-semibold">{m.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Converge node */}
        <motion.div
          className="flex flex-col items-center gap-4 mt-14"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.7 }}
        >
          <div className="w-px h-12 bg-gradient-to-b from-transparent to-cyan" />
          <div className="glass-panel px-10 py-5 text-center border-cyan/40 shadow-xl shadow-cyan/10">
            <div className="font-bold tracking-wider font-mono text-cyan">
              UNIFIED BUSINESS INTELLIGENCE
            </div>
            <div className="text-xs font-mono text-muted mt-1.5">
              Lead Score: 92/100 · Opportunity: High Priority
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
