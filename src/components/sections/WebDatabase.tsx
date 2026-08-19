'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'

const STORY = [
  { text: '"The web is our database."', color: '#F8FAFC', size: '3xl md:text-5xl', weight: 'black', delay: 0 },
  { text: "But databases don't constantly change their structure.", color: '#A1A1B5', size: 'xl md:text-2xl', weight: 'normal', delay: 0.4 },
  { text: 'The web does.', color: '#FF1744', size: '2xl md:text-4xl', weight: 'bold', delay: 0.8 },
  { text: "That's why our scrapers heal themselves.", color: '#00E5FF', size: '2xl md:text-4xl', weight: 'bold', delay: 1.2 },
]

const WEB_NODES = ['Business', 'Website', 'Review', 'Competitor', 'Social', 'Location', 'Product', 'Pricing']
const NODE_COLORS = ['#00E5FF', '#EC0AFF', '#FF1744', '#6D28D9', '#00E5FF', '#EC0AFF', '#FF1744', '#6D28D9']

export function WebDatabase() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section
      id="web-database"
      ref={ref}
      className="relative py-32 overflow-hidden"
      aria-label="The web is our database"
    >
      <div className="absolute inset-0 halftone opacity-15 pointer-events-none" />
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          {STORY.map((line, i) => (
            <motion.p
              key={i}
              className={`text-${line.size} font-${line.weight} leading-tight`}
              style={{ color: line.color, fontFamily: i === 0 || i === 2 || i === 3 ? 'var(--font-display)' : 'var(--font-body)' }}
              initial={!prefersReduced ? { opacity: 0, y: 20 } : false}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: line.delay, duration: 0.6, ease: 'easeOut' }}
            >
              {line.text}
            </motion.p>
          ))}
        </div>

        <motion.div
          className="mt-20"
          initial={!prefersReduced ? { opacity: 0 } : false}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.6, duration: 0.8 }}
        >
          <p className="text-center text-xs font-mono tracking-widest mb-8" style={{ color: '#A1A1B5' }}>
            SCRAPING ENGINE CONNECTS EVERYTHING
          </p>

          <div className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
            {WEB_NODES.map((node, i) => (
              <motion.div
                key={node}
                className="px-3 py-1.5 rounded text-xs font-mono border"
                style={{
                  color: NODE_COLORS[i],
                  borderColor: `${NODE_COLORS[i]}40`,
                  backgroundColor: `${NODE_COLORS[i]}10`,
                }}
                initial={!prefersReduced ? { scale: 0, opacity: 0 } : false}
                animate={inView ? { scale: 1, opacity: 1 } : {}}
                transition={{ delay: 1.8 + i * 0.08, type: 'spring' }}
              >
                {node}
              </motion.div>
            ))}
          </div>

          <div className="flex flex-col items-center gap-3 mt-8">
            <div className="w-px h-10" style={{ background: 'linear-gradient(to bottom, rgba(161,161,181,0) , #EC0AFF)' }} />
            <div
              className="px-6 py-3 rounded border text-sm font-mono font-bold tracking-wider"
              style={{ color: '#EC0AFF', borderColor: 'rgba(236,10,255,0.4)', backgroundColor: 'rgba(236,10,255,0.08)' }}
            >
              ⚡ SCRAPING ENGINE
            </div>
            <div className="w-px h-10" style={{ background: 'linear-gradient(to bottom, #EC0AFF, #00E5FF)' }} />
            <div
              className="px-6 py-3 rounded border text-sm font-mono font-bold tracking-wider"
              style={{ color: '#00E5FF', borderColor: 'rgba(0,229,255,0.4)', backgroundColor: 'rgba(0,229,255,0.08)' }}
            >
              🧠 STRUCTURED INTELLIGENCE
            </div>
          </div>

          <p className="text-center text-sm mt-8 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Millions of businesses publish signals across websites, directories, reviews, maps and social platforms.
            Scrape-Verse turns those scattered signals into structured intelligence.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
