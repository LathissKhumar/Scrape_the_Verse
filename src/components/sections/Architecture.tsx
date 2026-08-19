'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
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
    title: 'Self-Healing Intelligence',
    desc: 'Structural change detection, AI-driven selector repair, schema validation, CI pipeline.',
    color: '#6D28D9',
    items: ['DOM Diff Engine', 'LLM Repair Agent', 'Schema Validator', 'CI Runner'],
  },
  {
    title: 'Gemini AI Processing',
    desc: 'Business intelligence extraction, lead scoring, natural language recommendation generation.',
    color: '#00E5FF',
    items: ['Lead Scorer', 'Proposal Generator', 'Outreach Writer', 'Voice Script Engine'],
  },
  {
    title: 'Sales Automation Layer',
    desc: 'Multi-agent orchestration, CRM sync, follow-up sequencing, opportunity pipeline.',
    color: '#FF1744',
    items: ['Proposal Agent', 'Outreach Agent', 'Voice Agent', 'Follow-Up Agent'],
  },
]

export function Architecture() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="architecture" ref={ref} className="py-24 relative" aria-label="System Architecture">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="System Architecture" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Four layers.{' '}
            <GradientText>One pipeline.</GradientText>
          </h2>
        </div>

        <div className="max-w-2xl mx-auto space-y-3">
          {LAYERS.map((layer, i) => (
            <motion.div
              key={layer.title}
              className="comic-panel p-5"
              style={{ borderColor: `${layer.color}50`, backgroundColor: `${layer.color}08` }}
              initial={!prefersReduced ? { opacity: 0, x: -30 } : false}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: i * 0.15, duration: 0.5 }}
            >
              <div className="flex items-start gap-4 flex-wrap">
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold flex-shrink-0 mt-0.5"
                  style={{ backgroundColor: layer.color, color: '#05050A' }}
                >
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold mb-1" style={{ color: layer.color, fontFamily: 'var(--font-display)' }}>
                    {layer.title}
                  </h3>
                  <p className="text-sm mb-3" style={{ color: '#A1A1B5' }}>{layer.desc}</p>
                  <div className="flex flex-wrap gap-2">
                    {layer.items.map((item) => (
                      <span
                        key={item}
                        className="text-xs font-mono px-2 py-0.5 rounded"
                        style={{ backgroundColor: `${layer.color}18`, color: layer.color, border: `1px solid ${layer.color}30` }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {i < LAYERS.length - 1 && (
                <div className="flex justify-center mt-3">
                  <div className="w-px h-6" style={{ background: `linear-gradient(to bottom, ${layer.color}, ${LAYERS[i+1].color})` }} />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
