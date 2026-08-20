'use client'
import { motion } from 'framer-motion'
import { useRef, useState } from 'react'
import { FileText, Mail, Mic, ArrowRight, Sparkles } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { Button } from '@/components/ui/Button'
import { AI_AGENTS } from '@/lib/mock-data'

const AGENT_ICONS: Record<string, React.ReactNode> = {
  'file-text': <FileText className="w-5 h-5 text-violet-accent" />,
  mail: <Mail className="w-5 h-5 text-blue-accent" />,
  mic: <Mic className="w-5 h-5 text-emerald-success" />,
}

export function SalesAutomation() {
  const ref = useRef(null)
  const [activeAgentId, setActiveAgentId] = useState<string>('landing-page')
  const activeAgent = AI_AGENTS.find((a) => a.id === activeAgentId) ?? AI_AGENTS[0]

  return (
    <section id="sales-automation" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden" aria-label="Autonomous AI Sales Suite">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Blur Text Reveal */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="05" label="Sales Automation Agents" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            From intelligence to <GradientText>automated sales action.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Scrape-Verse doesn&apos;t just collect data. Dedicated AI agents generate tailored landing pages, personalized emails, and voice scripts.
          </p>
        </motion.div>

        {/* 3D Bento Mosaic Grid Zoom (Matching Scroll_UI.mp4 Frame 00:13 - 00:16) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start" style={{ perspective: '1200px' }}>
          {/* Left Agent Selector - 3D Perspective Tile */}
          <motion.div
            className="lg:col-span-5 space-y-4"
            initial={{ opacity: 0, x: -60, rotateY: 12, scale: 0.92 }}
            whileInView={{ opacity: 1, x: 0, rotateY: 0, scale: 1 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="text-xs font-mono text-muted uppercase tracking-wider mb-2">
              SELECT AI SALES AGENT
            </div>
            {AI_AGENTS.map((agent) => {
              const isActive = agent.id === activeAgentId
              return (
                <motion.div
                  key={agent.id}
                  onClick={() => setActiveAgentId(agent.id)}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-5 rounded-2xl cursor-pointer transition-all duration-300 border flex items-center justify-between ${
                    isActive
                      ? 'bg-gradient-to-r from-violet-accent/25 to-blue-accent/15 border-violet-accent/50 shadow-xl shadow-violet-accent/10'
                      : 'glass-card hover:border-white/20'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${isActive ? 'bg-violet-accent/20' : 'bg-white/5'}`}>
                      {AGENT_ICONS[agent.icon]}
                    </div>
                    <div>
                      <div className="font-bold font-display text-base text-text-primary">
                        {agent.name}
                      </div>
                      <div className="text-xs font-mono text-muted mt-0.5">
                        {agent.agentRole}
                      </div>
                    </div>
                  </div>
                  <ArrowRight className={`w-4 h-4 transition-transform ${isActive ? 'text-violet-accent translate-x-1' : 'text-muted'}`} />
                </motion.div>
              )
            })}
          </motion.div>

          {/* Right Live Generation Preview - 3D Perspective Card */}
          <motion.div
            className="lg:col-span-7"
            initial={{ opacity: 0, x: 60, rotateY: -12, scale: 0.92 }}
            whileInView={{ opacity: 1, x: 0, rotateY: 0, scale: 1 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-level-3 p-8 space-y-6 border-white/20 shadow-2xl relative overflow-hidden">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <Sparkles className="w-4 h-4 text-violet-accent animate-pulse" />
                  <span className="font-mono text-xs text-muted uppercase">
                    GENERATED ARTIFACT PREVIEW
                  </span>
                </div>
                <span className="text-xs font-mono text-emerald-success font-semibold px-3 py-1 rounded-full bg-emerald-success/10 border border-emerald-success/20">
                  READY FOR OUTREACH
                </span>
              </div>

              <div className="space-y-4">
                <h3 className="text-2xl font-bold font-display text-text-primary">
                  {activeAgent.outputTitle}
                </h3>
                <div className="p-5 rounded-2xl bg-black/40 border border-white/10 font-mono text-xs text-text-secondary leading-relaxed space-y-2">
                  <div className="text-violet-accent font-semibold">// Target: Urban Brew Café</div>
                  <div className="whitespace-pre-line">{activeAgent.outputSnippet}</div>
                </div>
              </div>

              <div className="flex items-center justify-between border-t border-white/10 pt-4 font-mono text-xs text-muted">
                <span>Agent Status: <strong className="text-emerald-success">Active</strong></span>
                <Button id="deploy-agent-btn" variant="primary" className="!text-xs !px-5 !py-2 flex items-center gap-1.5 shadow-lg shadow-violet-accent/20">
                  <span>Execute Outreach</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
