'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const LAYERS = [
  {
    title: 'Bright Data Scraping Layer',
    desc: 'Scraper Studio collectors, proxy rotation, CAPTCHA bypass, rate-limit management.',
    color: '#EC0AFF',
    items: ['Google Maps API', 'Yelp Scraper', 'Website Crawler', 'Social Media Monitor'],
  },
  {
    title: 'Self-Healing Intelligence Engine',
    desc: 'DOM change detection, LLM selector repair, schema verification, automated CI runner.',
    color: '#6D28D9',
    items: ['DOM Diff Engine', 'LLM Repair Agent', 'Schema Validator', 'CI Test Runner'],
  },
  {
    title: 'Gemini AI Intelligence Processing',
    desc: 'Raw payload normalization, lead scoring algorithm, business profile generation.',
    color: '#00E5FF',
    items: ['Lead Scorer', 'Proposal Generator', 'Outreach Writer', 'Voice Script Engine'],
  },
  {
    title: 'Autonomous Sales Agent Layer',
    desc: 'Multi-agent orchestration, CRM synchronization, prospect nurture sequencing.',
    color: '#FF1744',
    items: ['Proposal Agent', 'Outreach Agent', 'Voice Agent', 'Follow-Up Agent'],
  },
]

export function Architecture() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="architecture" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="System Architecture">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="System Architecture" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Four Layers.{' '}
            <GradientText>One Pipeline.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Decoupled stack combining Bright Data extraction, self-healing runtime, Gemini AI reasoning, and sales agents.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          {LAYERS.map((layer, i) => (
            <motion.div
              key={layer.title}
              className="glass-panel p-8 space-y-4"
              style={{ borderColor: `${layer.color}40` }}
              initial={{ opacity: 0, x: -30 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: i * 0.15, duration: 0.5 }}
            >
              <div className="flex items-start gap-5">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-mono font-bold shrink-0 mt-0.5 shadow-lg"
                  style={{ backgroundColor: `${layer.color}20`, color: layer.color, border: `1px solid ${layer.color}50` }}
                >
                  0{i + 1}
                </div>
                <div className="flex-1 space-y-3">
                  <h3 className="font-bold text-xl font-display" style={{ color: layer.color }}>
                    {layer.title}
                  </h3>
                  <p className="text-sm font-body text-muted leading-relaxed">
                    {layer.desc}
                  </p>
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {layer.items.map((item) => (
                      <span
                        key={item}
                        className="text-xs font-mono px-3 py-1 rounded-md border backdrop-blur-sm"
                        style={{
                          backgroundColor: `${layer.color}10`,
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
