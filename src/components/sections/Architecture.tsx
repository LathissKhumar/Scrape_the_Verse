'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const LAYERS = [
  {
    title: 'Bright Data Scraping Layer',
    desc: 'Scraper Studio collectors, proxy rotation, CAPTCHA bypass, rate-limit management.',
    color: '#8B5CF6',
    items: ['Google Maps API', 'Yelp Scraper', 'Website Crawler', 'Social Media Indexer'],
  },
  {
    title: 'Self-Healing Engine Layer',
    desc: 'DOM change detection, LLM selector repair, schema verification, automated CI runner.',
    color: '#38BDF8',
    items: ['DOM Diff Engine', 'LLM Repair Agent', 'Schema Validator', 'CI Test Runner'],
  },
  {
    title: 'Gemini AI Intelligence Layer',
    desc: 'Raw payload normalization, lead scoring algorithm, business profile generation.',
    color: '#34D399',
    items: ['Lead Scorer', 'Proposal Generator', 'Outreach Writer', 'Voice Script Engine'],
  },
  {
    title: 'Autonomous Sales Action Layer',
    desc: 'Multi-agent orchestration, CRM synchronization, prospect nurture sequencing.',
    color: '#8B5CF6',
    items: ['Proposal Agent', 'Outreach Agent', 'Voice Agent', 'Follow-Up Agent'],
  },
]

export function Architecture() {
  const ref = useRef(null)

  return (
    <section id="architecture" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void font-body overflow-hidden" aria-label="System Architecture">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Scale from Depth */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, scale: 0.92, y: 30 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="System Architecture" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Built for developers.{' '}
            <GradientText>Designed for business.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Decoupled infrastructure combining Bright Data extraction, self-healing runtime, Gemini AI reasoning, and sales agents.
          </p>
        </motion.div>

        {/* Business vs Developer Split - Slide from Left and Right */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 max-w-4xl mx-auto">
          <motion.div
            className="glass-level-2 p-8 space-y-3"
            initial={{ opacity: 0, x: -60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="font-mono text-xs font-bold text-blue-accent uppercase">BUSINESS VIEW</div>
            <h3 className="text-xl font-bold font-display text-text-primary">Discover & Convert Prospects</h3>
            <p className="text-xs font-body text-text-secondary leading-relaxed">
              Identify high-opportunity leads, generate customized proposals, and trigger outreach automatically without manual research.
            </p>
          </motion.div>

          <motion.div
            className="glass-level-2 p-8 space-y-3 border-violet-accent/30"
            initial={{ opacity: 0, x: 60 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="font-mono text-xs font-bold text-violet-accent uppercase">DEVELOPER VIEW</div>
            <h3 className="text-xl font-bold font-display text-text-primary">Resilient Scraping Infrastructure</h3>
            <p className="text-xs font-body text-text-secondary leading-relaxed">
              Deploy Studio collectors with built-in DOM diffing, LLM selector auto-healing, and event webhooks for continuous operations.
            </p>
          </motion.div>
        </div>

        {/* Architecture Stack - Alternating Left & Right Slide */}
        <div className="max-w-3xl mx-auto space-y-6">
          {LAYERS.map((layer, i) => (
            <motion.div
              key={layer.title}
              className="glass-level-2 p-8 space-y-4"
              style={{ borderColor: `${layer.color}40` }}
              initial={{ opacity: 0, x: i % 2 === 0 ? -60 : 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="flex items-start gap-5">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-mono font-bold shrink-0 mt-0.5"
                  style={{ backgroundColor: `${layer.color}15`, color: layer.color, border: `1px solid ${layer.color}40` }}
                >
                  0{i + 1}
                </div>
                <div className="flex-1 space-y-3">
                  <h3 className="font-bold text-xl font-display" style={{ color: layer.color }}>
                    {layer.title}
                  </h3>
                  <p className="text-sm font-body text-text-secondary leading-relaxed">
                    {layer.desc}
                  </p>
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {layer.items.map((item) => (
                      <span
                        key={item}
                        className="text-xs font-mono px-3 py-1 rounded-md border bg-white/5"
                        style={{
                          color: layer.color,
                          borderColor: `${layer.color}30`,
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
