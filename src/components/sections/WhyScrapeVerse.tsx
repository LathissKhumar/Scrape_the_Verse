'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const DIFFERENTIATORS = [
  {
    icon: '🔧',
    title: 'Self-Healing by Design',
    description:
      'Most scrapers break silently. Ours detect structural changes within seconds and rewrite extraction logic automatically — zero downtime, zero manual fixes.',
    highlight: 'The web changes. We adapt.',
    color: '#FF1744',
  },
  {
    icon: '⚡',
    title: 'Parallel Web Intelligence',
    description:
      'Four collectors work concurrently per prospect — website quality, reviews, competitors, social. Comprehensive business intel in under 15 seconds.',
    highlight: '4× faster than sequential scraping.',
    color: '#EC0AFF',
  },
  {
    icon: '🧠',
    title: 'Direct Gemini Integration',
    description:
      'Scraped data flows directly into Gemini models. Raw web signals are converted into structured lead scores and sales context in a single pass.',
    highlight: 'Web Scrape → AI → Action.',
    color: '#6D28D9',
  },
  {
    icon: '📡',
    title: 'Persistent Prospect Monitoring',
    description:
      'Target businesses are continuously monitored. The instant a business launches a website or gets new reviews, follow-up agents trigger automatically.',
    highlight: 'Never miss a conversion window.',
    color: '#00E5FF',
  },
]

export function WhyScrapeVerse() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="why-scrape-verse" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Why Scrape-Verse">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel label="Core Advantages" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Built Different.{' '}
            <GradientText gradient="brand">Designed to Survive.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Why traditional scrapers break and Scrape-Verse delivers persistent competitive advantage.
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
                className="glass-card p-8 h-full space-y-4 flex flex-col justify-between"
                style={{ borderColor: `${d.color}30` }}
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0 backdrop-blur-md shadow-md"
                      style={{ backgroundColor: `${d.color}15`, border: `1px solid ${d.color}40` }}
                    >
                      {d.icon}
                    </div>
                    <h3 className="font-bold text-xl font-display" style={{ color: d.color }}>
                      {d.title}
                    </h3>
                  </div>

                  <p className="text-sm font-body leading-relaxed text-muted">
                    {d.description}
                  </p>
                </div>

                <div className="text-xs font-mono font-bold pt-2" style={{ color: d.color }}>
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
