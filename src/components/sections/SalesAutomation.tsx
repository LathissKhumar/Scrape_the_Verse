'use client'
import { motion, useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const AGENTS = [
  {
    id: 'proposal',
    icon: '📄',
    name: 'Proposal Agent',
    description: 'Generates tailored sales proposals from structured intelligence and competitor gap analysis.',
    output: 'Custom PDF proposal + Tiered Pricing Specs',
    color: '#8B5CF6',
  },
  {
    id: 'email',
    icon: '✉️',
    name: 'Outreach Agent',
    description: 'Drafts personalized outreach sequences referencing specific opportunity signals (rating, missing site).',
    output: 'Subject line + 3-stage email sequence',
    color: '#38BDF8',
  },
  {
    id: 'voice',
    icon: '🎙️',
    name: 'Voice Agent',
    description: 'Conducts discovery calls, reads business intelligence on-the-fly, and logs owner feedback.',
    output: 'Call transcript + Qualification score',
    color: '#34D399',
  },
  {
    id: 'followup',
    icon: '🔄',
    name: 'Follow-Up Agent',
    description: 'Monitors prospect website and review updates, auto-triggering re-engagement sequences.',
    output: 'Trigger events + Automated re-engagement',
    color: '#38BDF8',
  },
]

export function SalesAutomation() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const [activeId, setActiveId] = useState<string>('proposal')

  return (
    <section id="sales-automation" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="AI Sales Action">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="05" label="Autonomous Action" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Intelligence <GradientText>becomes action.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Four specialized AI agents convert structured intelligence into outreach, proposals, voice calls, and follow-ups.
          </p>
        </div>

        {/* Action Pipeline Steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {AGENTS.map((agent, i) => {
            const isActive = activeId === agent.id
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                onClick={() => setActiveId(agent.id)}
                className="cursor-pointer"
              >
                <div
                  className={`glass-card p-6 h-full space-y-4 flex flex-col justify-between transition-all duration-300 ${
                    isActive
                      ? 'glass-level-3 border-violet-accent/50 shadow-xl shadow-violet-accent/15 scale-[1.02]'
                      : 'opacity-70 hover:opacity-100'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 backdrop-blur-md"
                        style={{ backgroundColor: `${agent.color}15`, border: `1px solid ${agent.color}30` }}
                      >
                        {agent.icon}
                      </div>
                      <div>
                        <h3 className="font-bold text-lg font-display text-text-primary">
                          {agent.name}
                        </h3>
                      </div>
                    </div>

                    <p className="text-xs font-body text-text-secondary leading-relaxed">
                      {agent.description}
                    </p>
                  </div>

                  <div className="text-xs font-mono px-3.5 py-2.5 rounded-lg bg-white/5 border border-white/5 text-blue-accent">
                    <span className="text-muted font-bold">OUTPUT:</span> {agent.output}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Conversion Guarantee Banner */}
        <motion.div
          className="mt-14 glass-level-2 p-8 max-w-2xl mx-auto text-center border-blue-accent/30 shadow-xl"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          <p className="text-sm font-mono text-text-secondary">
            From raw web listing to a delivered proposal:{' '}
            <span className="text-blue-accent font-bold">Under 90 Seconds.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
