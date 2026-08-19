'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Radio, Bell, ArrowRight } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { MONITORING_PROSPECTS } from '@/lib/mock-data'

export function Monitoring() {
  const ref = useRef(null)

  return (
    <section id="monitoring" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden" aria-label="Post-Outreach Monitoring">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="06" label="Continuous Prospect Monitoring" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Never miss when a <GradientText>prospect changes their status.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Automated monitoring monitors target domains 24/7. When a prospect launches a new website, updates social handles, or changes pricing, sales teams are instantly notified.
          </p>
        </motion.div>

        {/* Live Prospect Monitoring Cards */}
        <motion.div
          className="max-w-4xl mx-auto space-y-6"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="glass-level-3 p-8 space-y-6 border-white/20 shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <span className="font-mono text-xs text-muted uppercase flex items-center gap-2">
                <Radio className="w-4 h-4 text-violet-accent animate-pulse" />
                <span>MONITORED PROSPECT WATCHLIST</span>
              </span>
              <span className="text-xs font-mono text-emerald-success font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-success animate-ping" />
                <span>24 ACTIVE PROSPECT MONITORS</span>
              </span>
            </div>

            <div className="space-y-4">
              {MONITORING_PROSPECTS.map((prospect) => (
                <div key={prospect.id} className="p-5 rounded-2xl bg-white/5 border border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="font-bold font-display text-lg text-text-primary flex items-center gap-2">
                      <span>{prospect.name}</span>
                      <span className="text-xs font-mono text-muted">({prospect.location})</span>
                    </div>
                    <div className="text-xs font-mono text-rose-error flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-error" />
                      <span>Website Status: {prospect.website}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1.5 rounded-xl text-xs font-mono bg-violet-accent/15 text-violet-accent border border-violet-accent/30 font-semibold flex items-center gap-1.5">
                      <Bell className="w-3.5 h-3.5 text-violet-accent" />
                      <span>Domain Watch On</span>
                    </span>
                    <ArrowRight className="w-4 h-4 text-muted hidden sm:inline" />
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
