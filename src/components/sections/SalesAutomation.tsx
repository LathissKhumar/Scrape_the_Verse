'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { ComicPanel } from '@/components/ui/ComicPanel'

const AGENTS = [
  {
    id: 'proposal',
    icon: '📄',
    name: 'Proposal Agent',
    description: 'Generates tailored proposals from structured business intelligence and competitor gaps.',
    output: 'PDF proposal with pricing tier recommendations',
    color: '#EC0AFF',
  },
  {
    id: 'email',
    icon: '✉️',
    name: 'Outreach Agent',
    description: 'Writes personalised outreach emails referencing specific intel (rating, competitor advantage).',
    output: 'Subject line + 3-paragraph personalised email',
    color: '#6D28D9',
  },
  {
    id: 'voice',
    icon: '🎙️',
    name: 'Voice Agent',
    description: 'Makes discovery calls, reads business intelligence, captures objections for follow-up.',
    output: 'Call transcript + qualification score',
    color: '#FF1744',
  },
  {
    id: 'followup',
    icon: '🔄',
    name: 'Follow-Up Agent',
    description: 'Monitors prospect website and review changes, auto-triggers re-engagement on signals.',
    output: 'Trigger events + personalised follow-up sequence',
    color: '#00E5FF',
  },
]

export function SalesAutomation() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="sales-automation" ref={ref} className="py-24 relative" aria-label="AI Sales Automation">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel stage="05" label="AI Sales Automation" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Intelligence doesn&apos;t wait.
            <br />
            <GradientText>Agents take action.</GradientText>
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Once a prospect is scored, four specialised AI agents immediately turn intelligence into sales outcomes.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {AGENTS.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5 }}
            >
              <ComicPanel className="p-6 h-full space-y-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded flex items-center justify-center text-xl flex-shrink-0"
                    style={{ backgroundColor: `${agent.color}18`, border: `1px solid ${agent.color}40` }}
                  >
                    {agent.icon}
                  </div>
                  <h3 className="font-bold" style={{ fontFamily: 'var(--font-display)', color: agent.color }}>
                    {agent.name}
                  </h3>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: '#A1A1B5' }}>
                  {agent.description}
                </p>
                <div
                  className="text-xs font-mono px-3 py-2 rounded"
                  style={{ backgroundColor: `${agent.color}0D`, color: agent.color, border: `1px solid ${agent.color}20` }}
                >
                  OUTPUT: {agent.output}
                </div>
              </ComicPanel>
            </motion.div>
          ))}
        </div>

        {/* Outcome */}
        <motion.div
          className="mt-12 comic-panel p-6 max-w-2xl mx-auto text-center"
          style={{ borderColor: 'rgba(0,229,255,0.3)', backgroundColor: 'rgba(0,229,255,0.04)' }}
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
        >
          <p className="text-sm font-mono" style={{ color: '#A1A1B5' }}>
            From scraping a Google Maps listing to a sent proposal:{' '}
            <span style={{ color: '#00E5FF', fontWeight: 600 }}>under 90 seconds.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
