'use client'
import { motion, useInView } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'
import { CLIENT_METRICS, MONITORING_PROSPECTS } from '@/lib/mock-data'

export function Monitoring() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const [alertVisible, setAlertVisible] = useState(false)

  useEffect(() => {
    if (!inView) return
    const t = setTimeout(() => setAlertVisible(true), 3500)
    return () => clearTimeout(t)
  }, [inView])

  const metrics = [
    { label: 'Prospects Found', value: CLIENT_METRICS.prospectsFound.toLocaleString(), color: '#00E5FF' },
    { label: 'Qualified Opportunities', value: CLIENT_METRICS.qualified.toLocaleString(), color: '#EC0AFF' },
    { label: 'Hot Leads', value: CLIENT_METRICS.hotOpportunities.toLocaleString(), color: '#FF1744' },
    { label: 'Outreach Sent', value: CLIENT_METRICS.contacted.toLocaleString(), color: '#6D28D9' },
    { label: 'Owner Responses', value: CLIENT_METRICS.responses.toLocaleString(), color: '#00E5FF' },
    { label: 'Pipeline Value', value: CLIENT_METRICS.pipelineValue, color: '#EC0AFF' },
  ]

  return (
    <section id="monitoring" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Monitoring Dashboard">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="Live Prospect Monitoring" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Your Sales Pipeline,{' '}
            <GradientText gradient="recovery">Always Aware.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Persistent monitoring checks prospects continuously. The moment a business launches a website or acquires reviews, follow-up agents trigger automatically.
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-14">
          {metrics.map((m, i) => (
            <motion.div
              key={m.label}
              className="glass-card p-6 text-center flex flex-col justify-between"
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.08 }}
            >
              <div
                className="text-3xl font-black font-display tabular-nums"
                style={{ color: m.color }}
              >
                {m.value}
              </div>
              <div className="text-xs font-mono text-muted mt-2">
                {m.label}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Watch List */}
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="text-xs font-mono tracking-widest text-muted uppercase">
            ACTIVE PROSPECT WATCH LIST
          </div>

          <div className="space-y-4">
            {MONITORING_PROSPECTS.map((p, i) => (
              <motion.div
                key={p.id}
                className="glass-panel p-6"
                initial={{ opacity: 0 }}
                animate={inView ? { opacity: 1 } : {}}
                transition={{ delay: 0.3 + i * 0.1 }}
              >
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <span className="font-bold font-display text-lg text-off-white">
                    {p.name}
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {p.monitoring && <NeonBadge label="Website Monitor" variant="running" />}
                    {p.socialMonitoring && <NeonBadge label="Social Signal" variant="running" />}
                    {p.competitorMonitoring && <NeonBadge label="Competitor Intel" variant="running" />}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Triggered Alert */}
          {alertVisible && (
            <motion.div
              className="glass-panel p-6 border-cyan/50 shadow-xl shadow-cyan/15 bg-cyan/5"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-4 flex-wrap">
                <span className="text-2xl animate-bounce">🚨</span>
                <div className="flex-1">
                  <div className="text-base font-mono font-bold text-cyan">
                    New Website Launch Detected — Urban Brew Café
                  </div>
                  <div className="text-xs font-mono text-muted mt-1">
                    Domain urbanbrewatx.com went live · Follow-Up Agent triggered automatically
                  </div>
                </div>
                <NeonBadge label="ALERT TRIGGERED" variant="healthy" />
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </section>
  )
}
