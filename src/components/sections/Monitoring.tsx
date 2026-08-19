'use client'
import { motion, useInView } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { Bell, ArrowRight } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { NeonBadge } from '@/components/ui/NeonBadge'

export function Monitoring() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const [alertVisible, setAlertVisible] = useState(false)

  useEffect(() => {
    if (!inView) return
    const t = setTimeout(() => setAlertVisible(true), 2500)
    return () => clearTimeout(t)
  }, [inView])

  const flowNodes = ['WEB SIGNAL', 'MONITOR AGENT', 'EVENT TRIGGER', 'AI ANALYSIS', 'FOLLOW-UP ACTION']

  return (
    <section id="monitoring" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void font-body overflow-hidden" aria-label="Post-Outreach Monitoring">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Slide from Bottom */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Continuous Monitoring" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Don&apos;t stop watching <GradientText gradient="emerald">when the message is sent.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Persistent monitoring checks prospects continuously. The instant a business launches a website or acquires new reviews, agents re-engage automatically.
          </p>
        </motion.div>

        {/* Animated Event Travel Path */}
        <motion.div
          className="max-w-4xl mx-auto mb-14"
          initial={{ opacity: 0, scale: 0.96, y: 30 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="glass-level-2 p-6 overflow-x-auto">
            <div className="flex items-center justify-between min-w-[650px]">
              {flowNodes.map((node, i) => (
                <div key={node} className="flex items-center">
                  <div className="px-4 py-2 rounded-xl text-xs font-mono font-medium bg-white/5 border border-white/10 text-blue-accent">
                    {node}
                  </div>
                  {i < flowNodes.length - 1 && (
                    <div className="flex items-center px-2">
                      <div className="w-6 md:w-8 h-0.5 bg-gradient-to-r from-blue-accent to-emerald-success opacity-60" />
                      <ArrowRight className="w-3.5 h-3.5 text-emerald-success/60 -ml-1" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Prospect Watch List */}
        <motion.div
          className="max-w-3xl mx-auto space-y-6"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ duration: 0.7, delay: 0.25 }}
        >
          <div className="glass-level-2 p-8 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <h3 className="font-bold font-display text-lg text-text-primary">
                  Urban Brew Café
                </h3>
                <p className="text-xs font-mono text-muted">Chennai, India · Monitoring Active</p>
              </div>
              <NeonBadge label="ACTIVE MONITOR" variant="running" />
            </div>

            <div className="grid grid-cols-2 gap-4 font-mono text-xs text-muted">
              <div>Website Status: <span className="text-text-primary">Not detected</span></div>
              <div>Social Monitor: <span className="text-emerald-success">Active</span></div>
            </div>
          </div>

          {/* Triggered Alert Event */}
          {alertVisible && (
            <motion.div
              className="glass-level-3 p-6 border-emerald-success/40 shadow-xl bg-emerald-success/5"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-4 flex-wrap">
                <div className="w-10 h-10 rounded-xl bg-emerald-success/15 border border-emerald-success/30 flex items-center justify-center text-emerald-success shrink-0">
                  <Bell className="w-5 h-5 text-emerald-success" />
                </div>
                <div className="flex-1 font-mono text-xs">
                  <div className="font-bold text-emerald-success text-sm">
                    Website Launch Detected — urbanbrewchennai.com
                  </div>
                  <div className="text-muted mt-1">
                    Domain live event captured · Follow-Up Agent triggered automatically
                  </div>
                </div>
                <NeonBadge label="TRIGGERED" variant="healthy" />
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </section>
  )
}
