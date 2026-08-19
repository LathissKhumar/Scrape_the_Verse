'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'
import { CLIENT_METRICS, MONITORING_PROSPECTS } from '@/lib/mock-data'

export function Monitoring() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()
  const [alertVisible, setAlertVisible] = useState(false)

  useEffect(() => {
    if (!inView) return
    const t = setTimeout(() => setAlertVisible(true), 4000)
    return () => clearTimeout(t)
  }, [inView])

  const metrics = [
    { label: 'Prospects Found', value: CLIENT_METRICS.prospectsFound.toLocaleString(), color: '#00E5FF' },
    { label: 'Qualified', value: CLIENT_METRICS.qualified.toLocaleString(), color: '#EC0AFF' },
    { label: 'Hot Opportunities', value: CLIENT_METRICS.hotOpportunities.toLocaleString(), color: '#FF1744' },
    { label: 'Contacted', value: CLIENT_METRICS.contacted.toLocaleString(), color: '#6D28D9' },
    { label: 'Responses', value: CLIENT_METRICS.responses.toLocaleString(), color: '#00E5FF' },
    { label: 'Pipeline Value', value: CLIENT_METRICS.pipelineValue, color: '#EC0AFF' },
  ]

  return (
    <section id="monitoring" ref={ref} className="py-24 relative" aria-label="Monitoring Dashboard">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="Live Monitoring" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Your pipeline,{' '}
            <GradientText gradient="recovery">always aware.</GradientText>
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Continuous monitoring tracks every prospect. When they launch a website or get new reviews, your agents re-engage automatically.
          </p>
        </div>

        {/* Metrics grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
          {metrics.map((m, i) => (
            <motion.div
              key={m.label}
              className="comic-panel p-4 text-center"
              style={{ backgroundColor: 'rgba(8,8,16,0.7)' }}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.08 }}
            >
              <div className="text-2xl font-black tabular-nums" style={{ fontFamily: 'var(--font-display)', color: m.color }}>
                {m.value}
              </div>
              <div className="text-xs font-mono mt-1" style={{ color: '#A1A1B5' }}>{m.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Prospect watch list */}
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="text-xs font-mono tracking-widest mb-2" style={{ color: '#A1A1B5' }}>
            PROSPECT WATCH LIST
          </div>

          {MONITORING_PROSPECTS.map((p, i) => (
            <motion.div
              key={p.id}
              className="comic-panel p-4"
              style={{ backgroundColor: 'rgba(8,8,16,0.8)' }}
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.3 + i * 0.1 }}
            >
              <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="font-mono text-sm" style={{ color: '#F8FAFC' }}>{p.name}</span>
                <div className="flex flex-wrap gap-2">
                  {p.monitoring && <NeonBadge label="Website Monitor" variant="running" />}
                  {p.socialMonitoring && <NeonBadge label="Social" variant="running" />}
                  {p.competitorMonitoring && <NeonBadge label="Competitors" variant="running" />}
                </div>
              </div>
            </motion.div>
          ))}

          {/* Alert pop-in */}
          {alertVisible && (
            <motion.div
              className="comic-panel p-4"
              style={{ borderColor: 'rgba(0,229,255,0.5)', backgroundColor: 'rgba(0,229,255,0.07)' }}
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-3 flex-wrap">
                <span className="text-lg">🚨</span>
                <div className="flex-1">
                  <div className="text-sm font-mono font-bold" style={{ color: '#00E5FF' }}>
                    Website Detected — Urban Brew Café
                  </div>
                  <div className="text-xs font-mono mt-0.5" style={{ color: '#A1A1B5' }}>
                    urbanbrewatx.com just went live — Follow-Up Agent triggered
                  </div>
                </div>
                <NeonBadge label="NEW" variant="healthy" />
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </section>
  )
}
