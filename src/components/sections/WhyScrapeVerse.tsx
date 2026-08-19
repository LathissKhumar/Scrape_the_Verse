'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const DIFFERENTIATORS = [
  {
    icon: '🛡️',
    title: 'Self-Healing Runtime',
    description:
      'Target website layout changes are detected within seconds. Extraction paths are auto-repaired via LLM reasoning — zero downtime, zero manual maintenance.',
    highlight: 'The web changes. We adapt.',
    color: '#FB7185',
  },
  {
    icon: '⚡',
    title: 'Parallel Intelligence Stream',
    description:
      'Four concurrent collectors execute per prospect — site quality, customer sentiment, competitor gaps, and social footprint in under 15 seconds.',
    highlight: '4× faster than sequential scraping.',
    color: '#8B5CF6',
  },
  {
    icon: '🧠',
    title: 'Native Gemini AI Reasoning',
    description:
      'Scraped payloads stream directly into Gemini models. Raw data converts into structured lead scores and opportunity recommendations in a single pass.',
    highlight: 'Raw Web Data → AI → Action.',
    color: '#38BDF8',
  },
  {
    icon: '📡',
    title: 'Persistent Prospect Monitoring',
    description:
      'Target businesses are continuously monitored. The instant a business launches a website or acquires reviews, follow-up agents trigger automatically.',
    highlight: 'Never miss a conversion window.',
    color: '#34D399',
  },
]

export function WhyScrapeVerse() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="why-scrape-verse" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Why Scrape-Verse">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="Platform Value" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Built for enterprise.{' '}
            <GradientText gradient="signature">Designed for reliability.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Why traditional web scrapers break and Scrape-Verse delivers persistent competitive advantage.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-10">
          {DIFFERENTIATORS.map((d, i) => (
            <motion.div
              key={d.title}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5 }}
            >
              <div
                className="glass-card p-8 h-full space-y-5 flex flex-col justify-between"
                style={{ borderColor: `${d.color}25` }}
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0 backdrop-blur-md"
                      style={{ backgroundColor: `${d.color}15`, border: `1px solid ${d.color}30` }}
                    >
                      {d.icon}
                    </div>
                    <h3 className="font-bold text-xl font-display text-text-primary" style={{ color: d.color }}>
                      {d.title}
                    </h3>
                  </div>

                  <p className="text-sm font-body leading-relaxed text-text-secondary">
                    {d.description}
                  </p>
                </div>

                <div className="text-xs font-mono font-semibold pt-2" style={{ color: d.color }}>
                  {d.highlight}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
