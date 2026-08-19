'use client'
import { motion } from 'framer-motion'
import { useRef, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { Button } from '@/components/ui/Button'
import { useCollectorCounter } from '@/hooks/useCollectorCounter'
import { CLIENT_METRICS } from '@/lib/mock-data'

type Phase = 'idle' | 'searching' | 'collecting' | 'done'

export function LeadDiscovery() {
  const ref = useRef(null)
  const [phase, setPhase] = useState<Phase>('idle')
  const countFound = useCollectorCounter(CLIENT_METRICS.prospectsFound, 1400, phase === 'done' || phase === 'collecting')
  const countMatched = useCollectorCounter(CLIENT_METRICS.matchedCriteria, 1400, phase === 'done' || phase === 'collecting')
  const countHigh = useCollectorCounter(CLIENT_METRICS.highOpportunities, 1400, phase === 'done' || phase === 'collecting')

  const handleDiscover = () => {
    if (phase !== 'idle') return
    setPhase('searching')
    setTimeout(() => setPhase('collecting'), 1200)
    setTimeout(() => setPhase('done'), 2400)
  }

  const steps = [
    { label: 'Connecting to Google Maps & Business Registries…', active: phase === 'searching', done: phase === 'collecting' || phase === 'done' },
    { label: 'Filtering missing website & high rating signals…', active: phase === 'collecting', done: phase === 'done' },
    { label: 'Synthesizing structured business profiles…', active: false, done: phase === 'done' },
  ]

  return (
    <section id="lead-discovery" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Lead Discovery">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="01" label="Lead Discovery" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Tell us <GradientText>who you&apos;re looking for.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Target high-intent prospects across maps and business registries with custom filters.
          </p>
        </div>

        <div className="max-w-2xl mx-auto space-y-8">
          {/* Glass Search Console */}
          <div className="glass-level-2 p-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
              {[
                { label: 'Industry', value: 'Restaurants' },
                { label: 'Location', value: 'Chennai' },
                { label: 'Criteria', value: 'No website' },
                { label: 'Min Rating', value: '4+ ★' },
                { label: 'Min Reviews', value: '100+' },
                { label: 'Discovery Engine', value: 'Bright Data Studio' },
              ].map((field) => (
                <div key={field.label} className="space-y-1.5">
                  <label className="text-muted">{field.label}</label>
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-text-primary font-medium">
                    {field.value}
                  </div>
                </div>
              ))}
            </div>

            <Button
              id="start-discovery-btn"
              variant="primary"
              onClick={handleDiscover}
              className="w-full justify-center !py-3.5 shadow-xl shadow-violet-accent/20"
            >
              {phase === 'idle'
                ? 'Discover Leads'
                : phase === 'done'
                ? '✓ Discovery Complete'
                : 'Executing Lead Sweep…'}
            </Button>
          </div>

          {/* Progress Stream & Counter */}
          {phase !== 'idle' && (
            <motion.div
              className="glass-level-2 p-8 space-y-6"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="space-y-3 font-mono text-xs">
                {steps.map((step) => (
                  <div key={step.label} className="flex items-center gap-3">
                    <span
                      style={{
                        color: step.done ? '#34D399' : step.active ? '#38BDF8' : '#6F7887',
                      }}
                    >
                      {step.done ? '✓' : step.active ? '●' : '○'}
                    </span>
                    <span
                      style={{
                        color: step.done ? '#34D399' : step.active ? '#F5F7FA' : '#6F7887',
                      }}
                    >
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>

              {phase === 'done' && (
                <motion.div
                  className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-white/10 pt-6 text-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="glass-card p-4">
                    <div className="text-2xl font-bold font-display text-text-primary tabular-nums">
                      {countFound.toLocaleString()}
                    </div>
                    <div className="text-xs font-mono text-muted mt-1">businesses discovered</div>
                  </div>

                  <div className="glass-card p-4">
                    <div className="text-2xl font-bold font-display text-blue-accent tabular-nums">
                      {countMatched.toLocaleString()}
                    </div>
                    <div className="text-xs font-mono text-muted mt-1">matching criteria</div>
                  </div>

                  <div className="glass-card p-4">
                    <div className="text-2xl font-bold font-display text-emerald-success tabular-nums">
                      {countHigh.toLocaleString()}
                    </div>
                    <div className="text-xs font-mono text-muted mt-1">high-opportunity</div>
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
