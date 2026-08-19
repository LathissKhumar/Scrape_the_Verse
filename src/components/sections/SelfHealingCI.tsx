'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CI_COLLECTORS } from '@/lib/mock-data'

type CiState = 'pending' | 'running' | 'failing' | 'healing' | 'passing'

export function SelfHealingCI() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()
  const [state, setState] = useState<CiState>('pending')

  useEffect(() => {
    if (!inView) return
    const t1 = setTimeout(() => setState('running'), 800)
    const t2 = setTimeout(() => setState('failing'), 2200)
    const t3 = setTimeout(() => setState('healing'), 3200)
    const t4 = setTimeout(() => setState('passing'), 5000)
    return () => { [t1, t2, t3, t4].forEach(clearTimeout) }
  }, [inView])

  const getCollectorStatus = (index: number, original: 'pass' | 'fail') => {
    if (state === 'pending') return 'pending'
    if (state === 'running') return index < 2 ? 'pass' : index === 2 ? 'running' : 'pending'
    if (state === 'failing') return original === 'pass' ? 'pass' : 'fail'
    if (state === 'healing') return original === 'pass' ? 'pass' : 'healing'
    return 'pass'
  }

  const STATUS_COLORS: Record<string, string> = {
    pass: '#00E5FF', fail: '#FF1744', running: '#60A5FA', healing: '#EC0AFF', pending: '#A1A1B5',
  }
  const STATUS_LABELS: Record<string, string> = {
    pass: '✓ PASS', fail: '✗ FAIL', running: '◌ RUNNING', healing: '⚙ HEALING', pending: '— PENDING',
  }

  const ciStatusColor = {
    pending: '#A1A1B5', running: '#60A5FA', failing: '#FF1744', healing: '#EC0AFF', passing: '#00E5FF',
  }[state]

  const ciStatusLabel = {
    pending: 'WAITING', running: 'RUNNING', failing: 'FAILURE', healing: 'SELF-HEALING', passing: 'ALL PASSING',
  }[state]

  return (
    <section id="self-healing-ci" ref={ref} className="py-24 relative" aria-label="Self-Healing CI">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="Self-Healing CI Pipeline" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            <GradientText gradient="healing">Continuous scraping.</GradientText> Zero downtime.
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            When a collector fails CI checks, the healing agent rewrites the extraction logic and re-runs automatically.
          </p>
        </div>

        <div className="max-w-xl mx-auto">
          {/* CI status bar */}
          <div
            className="flex items-center justify-between px-4 py-3 rounded-t font-mono text-sm"
            style={{ backgroundColor: 'rgba(8,8,16,0.9)', border: '1px solid rgba(255,255,255,0.08)', borderBottom: 'none' }}
          >
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: ciStatusColor, boxShadow: `0 0 6px ${ciStatusColor}` }}
              />
              <span style={{ color: ciStatusColor, fontWeight: 600 }}>CI: {ciStatusLabel}</span>
            </div>
            <span style={{ color: '#A1A1B5', fontSize: '11px' }}>pipeline #47 · branch: main</span>
          </div>

          {/* Collector list */}
          <div
            className="p-4 space-y-2 font-mono text-sm"
            style={{ backgroundColor: '#060609', border: '1px solid rgba(255,255,255,0.08)', borderBottom: 'none' }}
          >
            {CI_COLLECTORS.map((c, i) => {
              const colState = getCollectorStatus(i, c.status)
              return (
                <motion.div
                  key={c.name}
                  className="flex items-center justify-between gap-3 py-2 border-b"
                  style={{ borderColor: 'rgba(255,255,255,0.05)' }}
                  initial={!prefersReduced ? { opacity: 0 } : false}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.08 }}
                >
                  <span style={{ color: '#A1A1B5' }}>{c.name}</span>
                  <span style={{ color: STATUS_COLORS[colState], fontWeight: 600, minWidth: '80px', textAlign: 'right' }}>
                    {STATUS_LABELS[colState]}
                  </span>
                </motion.div>
              )
            })}
          </div>

          {/* Healing message */}
          <div
            className="px-4 py-3"
            style={{ backgroundColor: 'rgba(8,8,16,0.9)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0 0 4px 4px' }}
          >
            {state === 'healing' && (
              <motion.p
                className="text-xs font-mono"
                style={{ color: '#EC0AFF' }}
                initial={!prefersReduced ? { opacity: 0 } : false}
                animate={{ opacity: 1 }}
              >
                ⚙ Self-healing agent rewriting selector for Collector C…
              </motion.p>
            )}
            {state === 'passing' && (
              <motion.p
                className="text-xs font-mono"
                style={{ color: '#00E5FF' }}
                initial={!prefersReduced ? { opacity: 0 } : false}
                animate={{ opacity: 1 }}
              >
                ✓ All collectors passing · Pipeline resumed automatically
              </motion.p>
            )}
            {(state === 'pending' || state === 'running' || state === 'failing') && (
              <p className="text-xs font-mono" style={{ color: '#A1A1B5' }}>
                {state === 'failing' ? '✗ Collector C failure detected' : 'Pipeline running…'}
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
