'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CollectorCard } from '@/components/ui/CollectorCard'
import { ACTIVE_COLLECTORS, SELF_HEAL_EVENTS } from '@/lib/mock-data'

export function ScraperControlCenter() {
  const ref = useRef(null)

  const summaryMetrics = [
    { label: 'Active Collectors', value: '24', color: '#F5F7FA' },
    { label: 'Healthy Status', value: '21', color: '#34D399' },
    { label: 'Auto-Healing', value: '1', color: '#8B5CF6' },
    { label: 'Records Processed Today', value: '184,200', color: '#38BDF8' },
  ]

  return (
    <section
      id="scraper-control"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-void font-body overflow-hidden"
      aria-label="Scraper Control Center"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Slide from Bottom */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Platform Operations" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Scraper <GradientText>Control Center.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Real-time operations dashboard across all active Bright Data collectors — tracking records throughput, runtime health, and healing events.
          </p>
        </motion.div>

        {/* Top Summary Metrics - Scale up from Depth */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {summaryMetrics.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, scale: 0.94, y: 20 }}
              whileInView={{ opacity: 1, scale: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="glass-card p-6 text-center"
            >
              <div className="text-3xl font-bold font-display tabular-nums" style={{ color: m.color }}>
                {m.value}
              </div>
              <div className="text-xs font-mono text-muted mt-2 uppercase">{m.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Collector Cards Grid - Staggered Slide from Bottom */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {ACTIVE_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <CollectorCard collector={collector} />
            </motion.div>
          ))}
        </div>

        {/* Live System Event Stream - Slide from Bottom */}
        <motion.div
          className="max-w-4xl mx-auto space-y-4"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <div className="text-xs font-mono tracking-widest text-muted uppercase">
            LIVE SYSTEM EVENT LOG
          </div>
          <div className="glass-level-2 overflow-hidden">
            <div className="p-6 space-y-3 font-mono text-xs max-h-72 overflow-y-auto bg-[#07090D]/95">
              {SELF_HEAL_EVENTS.map((evt, i) => (
                <div
                  key={i}
                  className="flex items-start gap-4 py-1 border-b border-white/[0.03]"
                >
                  <span className="text-muted shrink-0">{evt.time}</span>
                  <span
                    style={{
                      color:
                        evt.type === 'error'
                          ? '#FB7185'
                          : evt.type === 'warning'
                          ? '#FBBF24'
                          : evt.type === 'healing'
                          ? '#8B5CF6'
                          : evt.type === 'success'
                          ? '#34D399'
                          : '#A7AFBD',
                      fontWeight: evt.type === 'healing' || evt.type === 'success' ? 600 : 400,
                    }}
                  >
                    {evt.message}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
