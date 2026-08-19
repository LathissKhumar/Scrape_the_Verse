'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CollectorCard } from '@/components/ui/CollectorCard'
import { ACTIVE_COLLECTORS, SELF_HEAL_EVENTS } from '@/lib/mock-data'

export function ScraperControlCenter() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section
      id="scraper-control"
      ref={ref}
      className="py-24 relative"
      aria-label="Scraper Control Center"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="Scraper Control Center" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Six collectors.{' '}
            <GradientText>Always running.</GradientText>
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Real-time view of every Bright Data collector — health, record throughput, and the moment a self-heal fires.
          </p>
        </div>

        {/* Collector grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
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

        {/* Event stream */}
        <motion.div
          className="max-w-3xl mx-auto"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          <div className="text-xs font-mono tracking-widest mb-3" style={{ color: '#A1A1B5' }}>
            LIVE EVENT STREAM
          </div>
          <div
            className="comic-panel overflow-hidden"
            style={{ backgroundColor: '#060609' }}
          >
            <div className="p-4 space-y-1.5 font-mono text-xs max-h-56 overflow-y-auto">
              {SELF_HEAL_EVENTS.map((evt, i) => (
                <motion.div
                  key={i}
                  className="flex items-start gap-3"
                  initial={{ opacity: 0, x: -8 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ delay: 0.6 + i * 0.08 }}
                >
                  <span style={{ color: '#A1A1B5', flexShrink: 0 }}>{evt.time}</span>
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
