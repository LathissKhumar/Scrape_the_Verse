'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CollectorCard } from '@/components/ui/CollectorCard'
import { ACTIVE_COLLECTORS, SELF_HEAL_EVENTS } from '@/lib/mock-data'

export function ScraperControlCenter() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="scraper-control"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-void"
      aria-label="Scraper Control Center"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="Scraper Control Center" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Six Collectors.{' '}
            <GradientText>Always Active.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Real-time status monitor across all Bright Data Studio collectors — tracking extraction rate, status, and self-healing triggers.
          </p>
        </div>

        {/* Collector Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {ACTIVE_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.1, duration: 0.4 }}
            >
              <CollectorCard collector={collector} />
            </motion.div>
          ))}
        </div>

        {/* Live Stream Console */}
        <motion.div
          className="max-w-4xl mx-auto space-y-4"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.4 }}
        >
          <div className="text-xs font-mono tracking-widest text-muted uppercase">
            LIVE SYSTEM EVENT STREAM
          </div>
          <div className="glass-panel overflow-hidden border-white/10 shadow-2xl">
            <div className="p-6 space-y-3 font-mono text-xs max-h-72 overflow-y-auto bg-[#05050A]/90">
              {SELF_HEAL_EVENTS.map((evt, i) => (
                <motion.div
                  key={i}
                  className="flex items-start gap-4 py-1 border-b border-white/[0.03]"
                  initial={{ opacity: 0, x: -8 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ delay: 0.5 + i * 0.08 }}
                >
                  <span className="text-muted shrink-0 font-medium">{evt.time}</span>
                  <span
                    style={{
                      color:
                        evt.type === 'error'
                          ? '#FF1744'
                          : evt.type === 'warning'
                          ? '#FF9800'
                          : evt.type === 'healing'
                          ? '#EC0AFF'
                          : evt.type === 'success'
                          ? '#00E5FF'
                          : '#A1A1B5',
                      fontWeight: evt.type === 'healing' || evt.type === 'success' ? 600 : 400,
                    }}
                  >
                    {evt.message}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
