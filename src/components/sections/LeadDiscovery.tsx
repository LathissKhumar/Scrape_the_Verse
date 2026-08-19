'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
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
  const inView = useInView(ref, { once: true })
  const prefersReduced = useReducedMotion()
  const [phase, setPhase] = useState<Phase>('idle')
  const count = useCollectorCounter(TOTAL, 1500, phase === 'done' || phase === 'collecting')

  const handleDiscover = () => {
    if (phase !== 'idle') return
    setPhase('searching')
    setTimeout(() => setPhase('collecting'), 1200)
    setTimeout(() => setPhase('done'), 2400)
  }

  const steps = [
    { label: 'Searching the web…', active: phase === 'searching', done: phase === 'collecting' || phase === 'done' },
    { label: 'Collecting sources…', active: phase === 'collecting', done: phase === 'done' },
    { label: 'Normalizing results…', active: false, done: phase === 'done' },
  ]

  return (
    <section id="lead-discovery" ref={ref} className="py-24 relative" aria-label="Lead Discovery">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel stage="01" label="Lead Discovery" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Tell us <GradientText>who you&apos;re looking for.</GradientText>
          </h2>
        </div>

        <div className="max-w-xl mx-auto space-y-4">
          {/* Search form */}
          <div className="comic-panel p-6 space-y-4" style={{ backgroundColor: 'rgba(8,8,16,0.85)' }}>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Industry', value: 'Restaurants' },
                { label: 'Location', value: 'Austin, Texas' },
                { label: 'Requirement', value: 'No Website' },
                { label: 'Min Rating', value: '> 4.0' },
              ].map((field) => (
                <div key={field.label} className="space-y-1">
                  <label className="text-xs font-mono" style={{ color: '#A1A1B5' }}>
                    {field.label}
                  </label>
                  <div
                    className="px-3 py-2 rounded text-sm font-mono"
                    style={{
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.08)',
                      color: '#F8FAFC',
                    }}
                  >
                    {field.value}
                  </div>
                </div>
              ))}
            </div>

            <Button
              id="start-discovery-btn"
              variant="primary"
              onClick={handleDiscover}
              className="w-full justify-center"
            >
              {phase === 'idle'
                ? 'Start Discovery'
                : phase === 'done'
                ? '✓ Discovery Complete'
                : 'Discovering…'}
            </Button>
          </div>

          {/* Progress */}
          {phase !== 'idle' && (
            <motion.div
              className="comic-panel p-6 space-y-4"
              style={{ backgroundColor: 'rgba(8,8,16,0.85)' }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="space-y-2">
                {steps.map((step) => (
                  <div key={step.label} className="flex items-center gap-3 text-sm font-mono">
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
                  className="space-y-3 border-t pt-4"
                  style={{ borderColor: 'rgba(255,255,255,0.08)' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {DISCOVERY_SOURCES.map((source) => (
                    <div key={source.name} className="flex items-center justify-between text-sm font-mono">
                      <span className="flex items-center gap-2" style={{ color: '#A1A1B5' }}>
                        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: source.color }} />
                        {source.name}
                      </span>
                      <span style={{ color: source.color }}>{source.records.toLocaleString()} records</span>
                    </div>
                  ))}
                  <div
                    className="flex items-center justify-between border-t pt-3"
                    style={{ borderColor: 'rgba(255,255,255,0.08)' }}
                  >
                    <span className="text-sm font-mono" style={{ color: '#A1A1B5' }}>TOTAL</span>
                    <span
                      className="text-xl font-black"
                      style={{
                        fontFamily: 'var(--font-display)',
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
