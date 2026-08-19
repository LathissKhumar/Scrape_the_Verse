'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const DIFFERENTIATORS = [
  {
    icon: '🔧',
    title: 'Self-Healing by Design',
    description:
      'Most scrapers break silently. Ours detect structural changes within seconds and repair the extraction logic automatically — no manual intervention, no data gaps.',
    highlight: 'The web changes. We adapt.',
    color: '#FF1744',
  },
  {
    icon: '⚡',
    title: 'Parallel Intelligence',
    description:
      'Four collectors work simultaneously per prospect — website quality, reviews, competitors, social. Full business profile in under 15 seconds.',
    highlight: '4× faster than sequential scraping.',
    color: '#EC0AFF',
  },
  {
    icon: '🧠',
    title: 'Direct AI Integration',
    description:
      'Scraped data flows into Gemini without transformation layers. Raw intelligence becomes structured sales context in a single pass.',
    highlight: 'Web → AI → Action.',
    color: '#6D28D9',
  },
  {
    icon: '📡',
    title: 'Persistent Monitoring',
    description:
      'Prospects are watched continuously. The moment a business without a website launches one, your pipeline is notified and agents re-engage.',
    highlight: 'Never miss an opportunity.',
    color: '#00E5FF',
  },
]

export function WhyScrapeVerse() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="why-scrape-verse" ref={ref} className="py-24 relative" aria-label="Why Scrape-Verse">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="Why Scrape-Verse" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Built different.{' '}
            <GradientText gradient="brand">Designed to survive.</GradientText>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {DIFFERENTIATORS.map((d, i) => (
            <motion.div
              key={d.title}
              className="comic-panel p-6 space-y-3"
              style={{ borderColor: `${d.color}40`, backgroundColor: 'rgba(8,8,16,0.7)' }}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5 }}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{d.icon}</span>
                <h3 className="font-bold" style={{ fontFamily: 'var(--font-display)', color: d.color }}>
                  {d.title}
                </h3>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: '#A1A1B5' }}>
                {d.description}
              </p>
              <p className="text-sm font-mono font-semibold" style={{ color: d.color }}>
                {d.highlight}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
