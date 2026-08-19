'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Zap, Layers, CheckCircle2 } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'
import { RESEARCH_COLLECTORS } from '@/lib/mock-data'

export function ParallelResearch() {
  const ref = useRef(null)

  return (
    <section id="parallel-research" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void font-body overflow-hidden" aria-label="Parallel Research">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Slide in from Right */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, x: 60 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="02" label="Parallel Web Research" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Every prospect <GradientText>tells a different story.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Four independent collectors evaluate website presence, customer reviews, competitor density, and social engagement concurrently.
          </p>
        </motion.div>

        {/* Fan-out Header Node */}
        <motion.div
          className="flex flex-col items-center gap-4 mb-14"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="glass-level-2 px-8 py-4 text-center border-violet-accent/30 shadow-lg">
            <div className="font-bold font-mono text-base text-violet-accent flex items-center justify-center gap-2">
              <Zap className="w-4 h-4 text-violet-accent" />
              <span>PROSPECT IDENTIFIED</span>
            </div>
            <div className="text-xs font-mono text-muted mt-1">Urban Brew Café · Chennai, India</div>
          </div>
          <div className="w-px h-10 bg-gradient-to-b from-violet-accent to-transparent" />
          <span className="text-xs font-mono tracking-widest text-muted uppercase">
            CONCURRENT COLLECTOR EXECUTION
          </span>
        </motion.div>

        {/* 4 Collector Cards - Staggered Slide from Right */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {RESEARCH_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={{ opacity: 0, x: 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="glass-card p-6 h-full space-y-4 flex flex-col justify-between hover:border-blue-accent/40">
                <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-3">
                  <span className="font-bold text-base font-display text-text-primary">
                    {collector.title}
                  </span>
                  <NeonBadge label="SCRAPING" variant="running" />
                </div>
                <div className="space-y-2.5 font-mono text-xs">
                  {collector.metrics.map((m) => (
                    <div key={m.label} className="flex items-center justify-between">
                      <span className="text-muted">{m.label}</span>
                      <span className="text-blue-accent font-semibold">{m.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Converge Node */}
        <motion.div
          className="flex flex-col items-center gap-4 mt-14"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <div className="w-px h-12 bg-gradient-to-b from-transparent to-blue-accent" />
          <div className="glass-level-2 px-10 py-5 text-center border-blue-accent/40 shadow-xl flex flex-col items-center gap-1.5">
            <div className="font-bold tracking-wider font-mono text-blue-accent flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-success" />
              <span>UNIFIED BUSINESS INTELLIGENCE PROFILE</span>
            </div>
            <div className="text-xs font-mono text-muted">
              Lead Score: 92/100 · Opportunity: High Priority
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
