'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { Button } from '@/components/ui/Button'
import { useSelfHealingSequence } from '@/hooks/useSelfHealingSequence'

const PHASE_COLORS = {
  idle: '#A1A1B5',
  running: '#00E5FF',
  failure: '#FF1744',
  healing: '#EC0AFF',
  recovered: '#00E5FF',
}

const PHASE_LABELS = {
  idle: 'READY',
  running: 'RUNNING',
  failure: 'FAILURE DETECTED',
  healing: 'SELF-HEALING IN PROGRESS…',
  recovered: 'RECOVERED ✓',
}

const EVENT_COLORS: Record<string, string> = {
  info: '#A1A1B5',
  warning: '#FF9800',
  error: '#FF1744',
  healing: '#EC0AFF',
  success: '#00E5FF',
}

export function SelfHealingDemo() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })
  const { phase, eventLog, start, reset } = useSelfHealingSequence()

  const phaseColor = PHASE_COLORS[phase]

  return (
    <section
      id="self-healing"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-void"
      aria-label="Self-Healing Demo"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="03" label="Self-Healing Scrapers" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            When the Web Breaks Rules,{' '}
            <GradientText gradient="failure">We Rewrite Ours.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Simulate a real target website layout break. Watch the pipeline detect HTML structure changes and auto-generate new extraction selectors dynamically.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          {/* Glass Console Container */}
          <div className="glass-panel overflow-hidden border-white/10 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5 font-mono text-sm">
              <div className="flex items-center gap-3">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{
                    backgroundColor: phaseColor,
                    boxShadow: `0 0 10px ${phaseColor}`,
                  }}
                />
                <span className="font-bold tracking-wider" style={{ color: phaseColor }}>
                  {PHASE_LABELS[phase]}
                </span>
              </div>
              <span className="text-xs text-muted">
                collector: restaurant-discovery
              </span>
            </div>

            {/* Log Stream */}
            <div className="h-80 overflow-y-auto p-6 space-y-2.5 font-mono text-xs bg-[#05050A]/90">
              {eventLog.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted">
                  Click &quot;▶ Run Self-Healing Demo&quot; to simulate a break…
                </div>
              ) : (
                eventLog.map((entry, i) => (
                  <motion.div
                    key={i}
                    className="flex items-start gap-4"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <span className="text-muted shrink-0">{entry.time}</span>
                    <span
                      style={{
                        color: EVENT_COLORS[entry.type] ?? '#F8FAFC',
                        fontWeight: entry.type === 'healing' || entry.type === 'success' ? 600 : 400,
                      }}
                    >
                      {entry.message}
                    </span>
                  </motion.div>
                ))
              )}
            </div>

            {/* Footer Control */}
            <div className="p-4 border-t border-white/10 bg-white/5 flex gap-4">
              <Button
                id="run-healing-demo-btn"
                variant={phase === 'recovered' ? 'ghost' : 'primary'}
                onClick={start}
                className="flex-1 justify-center !py-3 shadow-lg"
              >
                {phase === 'idle' ? '▶ Run Self-Healing Demo' : phase === 'recovered' ? '✓ Demo Complete' : 'Executing Recovery Sequence…'}
              </Button>
              {phase !== 'idle' && (
                <Button id="reset-healing-demo-btn" variant="ghost" onClick={reset} className="!px-6">
                  Reset
                </Button>
              )}
            </div>
          </div>

          {/* Key Insight Cards */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6"
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.5 }}
          >
            {[
              { stat: '< 15s', label: 'Mean Time To Heal', color: '#00E5FF' },
              { stat: '99.7%', label: 'Pipeline Uptime Guarantee', color: '#EC0AFF' },
              { stat: '0', label: 'Manual Selector Fixes', color: '#FF1744' },
            ].map((item) => (
              <div key={item.label} className="glass-card p-6 text-center">
                <div
                  className="text-4xl font-black font-display"
                  style={{ color: item.color }}
                >
                  {item.stat}
                </div>
                <div className="text-xs font-mono text-muted mt-2">
                  {item.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
