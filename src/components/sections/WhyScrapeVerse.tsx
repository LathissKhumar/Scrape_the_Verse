'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Zap, ShieldCheck, BrainCircuit, Rocket } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const REASONS = [
  {
    icon: <Zap className="w-6 h-6 text-violet-accent" />,
    title: 'Parallel Ingestion Fleet',
    description: 'Executes multi-source collectors simultaneously for 10x faster market coverage.',
  },
  {
    icon: <ShieldCheck className="w-6 h-6 text-emerald-success" />,
    title: 'Autonomous Self-Healing',
    description: 'Eliminates scraper maintenance overhead with automated LLM DOM repair.',
  },
  {
    icon: <BrainCircuit className="w-6 h-6 text-blue-accent" />,
    title: 'Structured Intent Scoring',
    description: 'Normalizes unstructured web noise into actionable lead opportunity metrics.',
  },
  {
    icon: <Rocket className="w-6 h-6 text-violet-accent" />,
    title: 'End-to-End Sales Suite',
    description: 'Generates custom micro-sites, outreach copy, and voice scripts instantly.',
  },
]

export function WhyScrapeVerse() {
  const ref = useRef(null)

  return (
    <section id="why-scrape-verse" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden" aria-label="Why Scrape-Verse">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Value Proposition" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Why enterprise teams choose <GradientText>Scrape-Verse.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Combining self-healing web scraping with autonomous AI sales action into a unified platform.
          </p>
        </motion.div>

        {/* 2x2 Grid — Alternating Slide */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {REASONS.map((reason, i) => (
            <motion.div
              key={reason.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -60 : 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="glass-card p-8 space-y-4 h-full hover:border-violet-accent/40 shadow-xl">
                <div className="p-3 rounded-2xl bg-white/5 w-fit border border-white/10">{reason.icon}</div>
                <h3 className="text-xl font-bold font-display text-text-primary">{reason.title}</h3>
                <p className="text-sm font-body text-text-secondary leading-relaxed">{reason.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
