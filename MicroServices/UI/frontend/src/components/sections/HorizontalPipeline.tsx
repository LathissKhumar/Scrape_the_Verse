'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const PIPELINE_CARDS = [
  {
    num: '01',
    title: 'Lead Discovery',
    desc: 'AI finds businesses from IndiaMART, Yelp, Google Maps, and Avvo automatically',
    badge: 'DISCOVERY',
  },
  {
    num: '02',
    title: 'Normalization',
    desc: 'Every source unified into one clean business profile with a single schema',
    badge: 'NORMALIZE',
  },
  {
    num: '03',
    title: 'Website Audit',
    desc: 'Full SEO and technical crawl with page-level findings and opportunity gaps',
    badge: 'SEO AUDIT',
  },
  {
    num: '04',
    title: 'Business Intelligence',
    desc: 'Market, customer, competitor and service context built by specialized agents',
    badge: 'INTELLIGENCE',
  },
  {
    num: '05',
    title: 'Opportunity Detection',
    desc: 'Evidence-backed gaps mapped to specific digital service opportunities',
    badge: 'OPPORTUNITY',
  },
  {
    num: '06',
    title: 'Prompt Generation',
    desc: 'Implementation-ready website spec generated automatically for any AI builder',
    badge: 'GENERATION',
  },
  {
    num: '07',
    title: 'Outreach & CRM',
    desc: 'Personalized pitch drafted and lead tracked through the full pipeline',
    badge: 'OUTREACH',
  },
]

// Duplicate items for continuous seamless horizontal marquee loop
const MARQUEE_CARDS = [...PIPELINE_CARDS, ...PIPELINE_CARDS]

export function HorizontalPipeline() {
  const [isPaused, setIsPaused] = useState(false)

  return (
    <section
      id="horizontal-pipeline"
      className="py-6 md:py-8 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="The Complete Pipeline — Horizontal Track"
    >
      {/* Section Header */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-2 text-center">
        <SectionLabel label="THE COMPLETE PIPELINE" />
        <h2 className="text-3xl md:text-4xl font-bold font-display tracking-tight text-text-primary">
          <GradientText>The Complete Pipeline</GradientText>
        </h2>
        <p className="text-xs sm:text-sm text-text-secondary font-body">
          Continuous autonomous execution across all 7 pipeline stages
        </p>
      </div>

      {/* Continuously Moving Horizontal Marquee Track */}
      <div className="relative w-full overflow-hidden mt-6">
        <motion.div
          className="flex items-stretch gap-6 w-max will-change-transform py-3 px-6"
          animate={{
            x: ['0%', '-50%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: 'loop',
              duration: 35,
              ease: 'linear',
            },
          }}
        >
          {MARQUEE_CARDS.map((card, i) => (
            <motion.div
              key={`${card.num}-${i}`}
              whileHover={{ y: -4, scale: 1.02 }}
              data-cursor-hover
              className="w-[300px] sm:w-[340px] md:w-[360px] glass-liquid p-6 rounded-2xl border border-white/25 shadow-xl shrink-0 flex flex-col justify-between group hover:border-sky-400/60 transition-all duration-300"
            >
              <PipelineCard card={card} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function PipelineCard({ card }: { card: typeof PIPELINE_CARDS[number] }) {
  return (
    <>
      {/* Top */}
      <div className="flex items-center justify-between">
        <span className="text-4xl sm:text-5xl font-black font-mono tracking-tighter text-sky-400">
          {card.num}
        </span>
        <span className="text-[10px] font-mono font-bold uppercase tracking-widest px-2.5 py-1 rounded-full border border-sky-400/30 bg-sky-500/10 text-sky-300">
          {card.badge}
        </span>
      </div>

      {/* Middle */}
      <div className="space-y-2 py-3">
        <h3 className="text-lg sm:text-xl font-bold font-display text-white group-hover:text-sky-300 transition-colors">
          {card.title}
        </h3>
        <p className="text-xs sm:text-sm font-body text-slate-300/80 leading-relaxed">{card.desc}</p>
      </div>

      {/* Footer */}
      <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <span className="flex items-center gap-1 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          ACTIVE NODE
        </span>
        <span className="text-sky-400 font-bold group-hover:translate-x-0.5 transition-transform">
          PIPELINE &rarr;
        </span>
      </div>
    </>
  )
}