'use client'
import { motion, useInView } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CI_COLLECTORS } from '@/lib/mock-data'

type CiState = 'pending' | 'running' | 'failing' | 'healing' | 'passing'

export function SelfHealingCI() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
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
    pending: 'WAITING', running: 'RUNNING PIPELINE', failing: 'TEST FAILURE DETECTED', healing: 'SELF-HEALING AGENT ACTIVE', passing: 'ALL COLLECTORS PASSING',
  }[state]

  return (
    <section id="self-healing-ci" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Self-Healing CI">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="Self-Healing CI Pipeline" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            <GradientText gradient="healing">Continuous Scraping.</GradientText> Zero Downtime.
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Automated test runner catches website schema changes during CI runs, triggers LLM repair agents, and resumes pipeline operations automatically.
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <div className="glass-panel overflow-hidden border-white/10 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5 font-mono text-sm">
              <div className="flex items-center gap-3">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: ciStatusColor, boxShadow: `0 0 10px ${ciStatusColor}` }}
                />
                <span className="font-bold tracking-wider" style={{ color: ciStatusColor }}>
                  {ciStatusLabel}
                </span>
              </div>
              <span className="text-xs text-muted">pipeline #47 · branch: main</span>
            </div>

            {/* List */}
            <div className="p-6 space-y-3 font-mono text-sm bg-[#05050A]/90">
              {CI_COLLECTORS.map((c, i) => {
                const colState = getCollectorStatus(i, c.status)
                return (
                  <div
                    key={c.name}
                    className="flex items-center justify-between gap-4 py-3 px-4 rounded-lg border border-white/5 bg-white/[0.02]"
                  >
                    <span className="text-muted">{c.name}</span>
                    <span className="font-bold shrink-0" style={{ color: STATUS_COLORS[colState] }}>
                      {STATUS_LABELS[colState]}
                    </span>
                  </div>
                )
              })}
            </div>

            {/* Footer message */}
            <div className="px-6 py-4 border-t border-white/10 bg-white/5 font-mono text-xs">
              {state === 'healing' && (
                <p className="text-magenta font-semibold animate-pulse">
                  ⚙ Self-healing agent re-generating DOM extraction paths for Collector C…
                </p>
              )}
              {state === 'passing' && (
                <p className="text-cyan font-semibold">
                  ✓ All collector tests restored — pipeline auto-merged and resumed.
                </p>
              )}
              {(state === 'pending' || state === 'running' || state === 'failing') && (
                <p className="text-muted">
                  {state === 'failing' ? '✗ Schema failure caught in unit test stage' : 'Executing collector health checks…'}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
