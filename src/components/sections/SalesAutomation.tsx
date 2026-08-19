'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const AGENTS = [
  {
    id: 'proposal',
    icon: '📄',
    name: 'Proposal Agent',
    description: 'Generates custom proposals based on target business rating gaps and competitor site benchmarks.',
    output: 'Custom PDF proposal + Tiered Pricing',
    color: '#EC0AFF',
  },
  {
    id: 'email',
    icon: '✉️',
    name: 'Outreach Agent',
    description: 'Drafts hyper-personalized emails highlighting specific opportunity signals (rating, review count).',
    output: 'Subject line + 3-paragraph outreach sequence',
    color: '#6D28D9',
  },
  {
    id: 'voice',
    icon: '🎙️',
    name: 'Voice Agent',
    description: 'Conducts discovery calls, reads business intelligence on-the-fly, and captures owner objections.',
    output: 'Call transcript + Qualification Score',
    color: '#FF1744',
  },
  {
    id: 'followup',
    icon: '🔄',
    name: 'Follow-Up Agent',
    description: 'Monitors prospect website & social updates, auto-triggering re-engagement when signals change.',
    output: 'Trigger events + Automated nurture sequence',
    color: '#00E5FF',
  },
]

export function SalesAutomation() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="sales-automation" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="AI Sales Automation">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="05" label="AI Sales Automation" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Intelligence Doesn&apos;t Wait.{' '}
            <GradientText>Agents Take Action.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Four specialized AI agents consume structured intelligence to execute outreach, calls, proposals, and follow-ups automatically.
          </p>
        </div>

        {/* 2x2 Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-10">
          {AGENTS.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5 }}
            >
              <div
                className="glass-card p-8 h-full space-y-5 flex flex-col justify-between"
                style={{ borderColor: `${agent.color}30` }}
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0 backdrop-blur-md shadow-md"
                      style={{ backgroundColor: `${agent.color}15`, border: `1px solid ${agent.color}40` }}
                    >
                      {agent.icon}
                    </div>
                    <div>
                      <h3 className="font-bold text-xl font-display" style={{ color: agent.color }}>
                        {agent.name}
                      </h3>
                      <span className="text-xs font-mono text-muted">Autonomous Agent</span>
                    </div>
                  </div>

                  <p className="text-sm font-body leading-relaxed text-muted">
                    {agent.description}
                  </p>
                </div>

                <div
                  className="text-xs font-mono px-4 py-3 rounded-lg border backdrop-blur-sm"
                  style={{
                    backgroundColor: `${agent.color}0A`,
                    color: agent.color,
                    borderColor: `${agent.color}25`,
                  }}
                >
                  <span className="font-bold">OUTPUT:</span> {agent.output}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Banner */}
        <motion.div
          className="mt-14 glass-panel p-8 max-w-3xl mx-auto text-center border-cyan/30 shadow-xl shadow-cyan/10"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
        >
          <p className="text-base font-mono text-muted">
            From raw Google Maps listing to a delivered proposal:{' '}
            <span className="text-cyan font-bold text-lg">Under 90 Seconds.</span>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
