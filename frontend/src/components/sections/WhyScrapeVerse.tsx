'use client'
import { motion, useScroll, useTransform, type MotionValue } from 'framer-motion'
import { useRef } from 'react'
import { Zap, ShieldCheck, BrainCircuit, Rocket, Sparkles } from 'lucide-react'

const MANIFESTO_WORDS =
  'We believe web intelligence should feel alive. Not just brittle extractors that break overnight — but resilient, self-healing, unforgettably fast autonomous pipelines. Every site Scrape-Verse monitors is parsed, understood, and transformed into continuous business growth.'.split(
    ' '
  )

const REASONS = [
  {
    icon: <Zap className="w-6 h-6 text-sky-400" />,
    title: 'Parallel Ingestion Fleet',
    description: 'Executes multi-source collectors simultaneously for 10x faster market coverage.',
  },
  {
    icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
    title: 'Autonomous Self-Healing',
    description: 'Eliminates scraper maintenance overhead with automated LLM DOM repair.',
  },
  {
    icon: <BrainCircuit className="w-6 h-6 text-indigo-400" />,
    title: 'Structured Intent Scoring',
    description: 'Normalizes unstructured web noise into actionable lead opportunity metrics.',
  },
  {
    icon: <Rocket className="w-6 h-6 text-cyan-300" />,
    title: 'End-to-End Sales Suite',
    description: 'Generates custom micro-sites, outreach copy, and voice scripts instantly.',
  },
]

export function WhyScrapeVerse() {
  const sectionRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start 80%', 'center 30%'],
  })

  return (
    <section
      id="why-scrape-verse"
      ref={sectionRef}
      className="py-32 md:py-44 relative border-b border-white/5 font-body overflow-hidden bg-transparent"
      aria-label="Why Scrape-Verse — Kinetic Typography Manifesto"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 space-y-24">
        {/* Kinetic Typography Manifesto */}
        <div className="max-w-5xl mx-auto space-y-8">
          <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-cyan-400 uppercase font-bold">
            <Sparkles className="w-4 h-4" />
            <span>— The Intelligence Manifesto</span>
          </div>

          <div className="flex flex-wrap gap-x-3 gap-y-2">
            {MANIFESTO_WORDS.map((word, i) => {
              const start = (i / MANIFESTO_WORDS.length) * 0.7
              const end = start + 0.2
              return (
                <KineticWord
                  key={i}
                  word={word}
                  index={i}
                  progress={scrollYProgress}
                  start={start}
                  end={end}
                />
              )
            })}
          </div>
        </div>

        {/* 2x2 Value Grid with Glassmorphic Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto pt-10">
          {REASONS.map((reason, i) => (
            <motion.div
              key={reason.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -40 : 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              whileHover={{ y: -4, scale: 1.01 }}
              data-cursor-hover
            >
              <div className="glass-card p-8 space-y-4 h-full hover:border-sky-400/50 shadow-2xl rounded-3xl">
                <div className="p-3.5 rounded-2xl bg-white/10 w-fit border border-white/15 backdrop-blur-md">
                  {reason.icon}
                </div>
                <h3 className="text-xl font-bold font-display text-text-primary">{reason.title}</h3>
                <p className="text-sm font-body text-text-secondary leading-relaxed">
                  {reason.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function KineticWord({
  word,
  index,
  progress,
  start,
  end,
}: {
  word: string
  index: number
  progress: MotionValue<number>
  start: number
  end: number
}) {
  const y = useTransform(progress, [start, end], [50, 0])
  const opacity = useTransform(progress, [start, end], [0.3, 1])
  const color = useTransform(progress, [start, end], ['#666677', '#ffffff'])

  return (
    <span className="inline-block overflow-hidden pb-1">
      <motion.span
        style={{ y, opacity, color }}
        className="inline-block text-2xl sm:text-4xl md:text-5xl font-black font-display tracking-tight leading-[1.2] will-change-transform"
      >
        {word}
      </motion.span>
    </span>
  )
}
