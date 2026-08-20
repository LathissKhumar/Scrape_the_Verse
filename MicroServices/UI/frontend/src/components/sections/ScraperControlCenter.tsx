'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Cpu, Activity } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CollectorCard } from '@/components/ui/CollectorCard'
import { ACTIVE_COLLECTORS, SELF_HEAL_EVENTS } from '@/lib/mock-data'

const EVENT_COLORS: Record<string, string> = {
  info: '#A7AFBD',
  warning: '#FBBF24',
  error: '#FB7185',
  healing: '#8B5CF6',
  success: '#34D399',
}

export function ScraperControlCenter() {
  const ref = useRef(null)

  return (
    <section
      id="scraper-control"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Scraper Control Center"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-16">
        {/* Section Header */}
        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Scraper Operations Studio" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Built on <GradientText>Bright Data Scraper Studio.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-2xl mx-auto font-body">
            Monitor active web collectors, inspect self-healing logs, and track real-time record extraction volume.
          </p>
        </motion.div>

        {/* Real-time Collector Grid */}
        <div className="space-y-6">
          <div className="flex items-center justify-between font-mono text-xs text-muted border-b border-white/10 pb-4">
            <span className="uppercase tracking-widest flex items-center gap-2">
              <Cpu className="w-4 h-4 text-violet-accent" />
              <span>ACTIVE COLLECTOR FLEET</span>
            </span>
            <span className="text-emerald-success font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-success animate-ping" />
              <span>24 COLLECTORS ONLINE</span>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
        </div>

        {/* Live Self-Healing Stream Log */}
        <motion.div
          className="glass-level-3 overflow-hidden border-white/20 shadow-2xl space-y-0"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ duration: 0.7, delay: 0.3 }}
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5 font-mono text-xs">
            <div className="flex items-center gap-3">
              <Activity className="w-4 h-4 text-violet-accent" />
              <span className="text-text-primary font-bold">REAL-TIME SELF-HEALING ENGINE STREAM</span>
            </div>
            <span className="text-muted">Target: competitor-intelligence</span>
          </div>

          <div className="p-6 space-y-3 font-mono text-xs max-h-72 overflow-y-auto bg-black/40">
            {SELF_HEAL_EVENTS.map((event, i) => (
              <div key={i} className="flex items-start gap-4 border-b border-white/5 pb-2.5 last:border-0 last:pb-0">
                <span className="text-muted shrink-0">{event.time}</span>
                <span
                  style={{
                    color: EVENT_COLORS[event.type] ?? '#F5F7FA',
                    fontWeight: event.type === 'healing' || event.type === 'success' ? 600 : 400,
                  }}
                >
                  {event.message}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
