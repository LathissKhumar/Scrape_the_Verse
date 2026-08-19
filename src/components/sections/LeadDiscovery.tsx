'use client'
import { motion } from 'framer-motion'
import { useRef, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { Button } from '@/components/ui/Button'
import { useCollectorCounter } from '@/hooks/useCollectorCounter'
import { DISCOVERY_SOURCES } from '@/lib/mock-data'

type Phase = 'idle' | 'searching' | 'collecting' | 'done'
const TOTAL = DISCOVERY_SOURCES.reduce((s, d) => s + d.records, 0)

export function LeadDiscovery() {
  const ref = useRef(null)
  const [phase, setPhase] = useState<Phase>('idle')
  const count = useCollectorCounter(TOTAL, 1500, phase === 'done' || phase === 'collecting')

  const handleDiscover = () => {
    if (phase !== 'idle') return
    setPhase('searching')
    setTimeout(() => setPhase('collecting'), 1200)
    setTimeout(() => setPhase('done'), 2400)
  }

  const steps = [
    { label: 'Searching Google Maps & Business Directories…', active: phase === 'searching', done: phase === 'collecting' || phase === 'done' },
    { label: 'Filtering missing website & high rating signals…', active: phase === 'collecting', done: phase === 'done' },
    { label: 'Normalizing multi-source discovery results…', active: false, done: phase === 'done' },
  ]

  return (
    <section id="lead-discovery" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Lead Discovery">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="01" label="Lead Discovery Engine" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Tell Us <GradientText>Who You&apos;re Looking For.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Bright Data Scraper Studio sweeps directories, maps, and review platforms to aggregate high-intent opportunities in real time.
          </p>
        </div>

        <div className="max-w-2xl mx-auto space-y-8">
          {/* Glass Form */}
          <div className="glass-panel p-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { label: 'Target Industry', value: 'Restaurants & Dining' },
                { label: 'Location', value: 'Austin, Texas' },
                { label: 'Opportunity Signal', value: 'No Website / Rating > 4.0' },
                { label: 'Source Studio', value: 'Bright Data Studio' },
              ].map((field) => (
                <div key={field.label} className="space-y-1.5">
                  <label className="text-xs font-mono text-muted">
                    {field.label}
                  </label>
                  <div className="px-4 py-3 rounded-lg text-sm font-mono bg-white/5 border border-white/10 text-off-white">
                    {field.value}
                  </div>
                </div>
              ))}
            </div>

            <Button
              id="start-discovery-btn"
              variant="primary"
              onClick={handleDiscover}
              className="w-full justify-center !py-4 shadow-xl shadow-magenta/20"
            >
              {phase === 'idle'
                ? '▶ Trigger Discovery Agent'
                : phase === 'done'
                ? '✓ Discovery Sequence Complete'
                : 'Scraping Target Sources…'}
            </Button>
          </div>

          {/* Progress Glass Card */}
          {phase !== 'idle' && (
            <motion.div
              className="glass-panel p-8 space-y-6"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="space-y-3 font-mono text-sm">
                {steps.map((step) => (
                  <div key={step.label} className="flex items-center gap-3">
                    <span
                      style={{
                        color: step.done ? '#00E5FF' : step.active ? '#EC0AFF' : 'rgba(161,161,181,0.3)',
                      }}
                    >
                      {step.done ? '✓' : step.active ? '●' : '○'}
                    </span>
                    <span
                      style={{
                        color: step.done ? '#00E5FF' : step.active ? '#F8FAFC' : 'rgba(161,161,181,0.3)',
                      }}
                    >
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>

              {phase === 'done' && (
                <motion.div
                  className="space-y-4 border-t border-white/10 pt-5"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {DISCOVERY_SOURCES.map((source) => (
                    <div key={source.name} className="flex items-center justify-between font-mono text-sm">
                      <span className="flex items-center gap-2 text-muted">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: source.color }} />
                        {source.name}
                      </span>
                      <span style={{ color: source.color }} className="font-semibold tabular-nums">
                        {source.records.toLocaleString()} records
                      </span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between border-t border-white/10 pt-4">
                    <span className="text-xs font-mono tracking-widest text-muted">TOTAL LEADS DISCOVERED</span>
                    <span
                      className="text-2xl font-black font-display"
                      style={{
                        background: 'linear-gradient(135deg, #EC0AFF, #00E5FF)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                      }}
                    >
                      {count.toLocaleString()} LEADS
                    </span>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </section>
  )
}
