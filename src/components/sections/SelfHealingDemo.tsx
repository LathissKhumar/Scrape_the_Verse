'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
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
  healing: 'SELF-HEALING…',
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
  const prefersReduced = useReducedMotion()
  const { phase, eventLog, start, reset } = useSelfHealingSequence()

  const phaseColor = PHASE_COLORS[phase]

  return (
    <section
      id="self-healing"
      ref={ref}
      className="py-24 relative"
      aria-label="Self-Healing Demo"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel stage="03" label="Self-Healing Scrapers" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            When the web breaks the rules,{' '}
            <GradientText gradient="failure">we rewrite ours.</GradientText>
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Watch a real self-healing event. A website changes its structure.
            The pipeline detects failure and repairs itself — no human intervention needed.
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          {/* Status bar */}
          <div
            className="flex items-center justify-between px-4 py-3 rounded-t font-mono text-sm"
            style={{
              backgroundColor: 'rgba(8,8,16,0.9)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderBottom: 'none',
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: phaseColor,
                  boxShadow: `0 0 8px ${phaseColor}`,
                  animation: phase === 'healing' ? 'pulse 0.8s infinite' : 'none',
                }}
              />
              <span style={{ color: phaseColor, fontWeight: 600 }}>
                {PHASE_LABELS[phase]}
              </span>
            </div>
            <span className="text-xs" style={{ color: '#A1A1B5' }}>
              collector: restaurant-discovery
            </span>
          </div>

          {/* Event log */}
          <div
            className="h-72 overflow-y-auto p-4 space-y-1.5 font-mono text-xs"
            style={{
              backgroundColor: '#060609',
              border: '1px solid rgba(255,255,255,0.08)',
              borderBottom: 'none',
            }}
          >
            {eventLog.length === 0 ? (
              <p style={{ color: '#A1A1B5' }}>
                Press &quot;Run Demo&quot; to trigger a self-healing event…
              </p>
            ) : (
              eventLog.map((entry, i) => (
                <motion.div
                  key={i}
                  className="flex items-start gap-3"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <span style={{ color: '#A1A1B5' }}>{entry.time}</span>
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

          {/* Control bar */}
          <div
            className="flex gap-3 p-4"
            style={{
              backgroundColor: 'rgba(8,8,16,0.9)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '0 0 4px 4px',
            }}
          >
            <Button
              id="run-healing-demo-btn"
              variant={phase === 'recovered' ? 'ghost' : 'primary'}
              onClick={start}
              className="flex-1 justify-center"
            >
              {phase === 'idle' ? '▶ Run Demo' : phase === 'recovered' ? '✓ Done' : 'Running…'}
            </Button>
            {phase !== 'idle' && (
              <Button id="reset-healing-demo-btn" variant="ghost" onClick={reset}>
                Reset
              </Button>
            )}
          </div>
        </div>

        {/* Key insight */}
        <motion.div
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          {[
            { stat: '< 15s', label: 'Mean Time To Heal', color: '#00E5FF' },
            { stat: '99.7%', label: 'Pipeline Uptime', color: '#EC0AFF' },
            { stat: '0', label: 'Human Interventions', color: '#FF1744' },
          ].map((item) => (
            <div
              key={item.label}
              className="comic-panel p-6 text-center"
              style={{ backgroundColor: 'rgba(8,8,16,0.6)' }}
            >
              <div
                className="text-4xl font-black"
                style={{ fontFamily: 'var(--font-display)', color: item.color }}
              >
                {item.stat}
              </div>
              <div className="text-xs font-mono mt-2" style={{ color: '#A1A1B5' }}>
                {item.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
