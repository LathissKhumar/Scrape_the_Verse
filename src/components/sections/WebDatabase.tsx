'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'

const STORY = [
  { text: '"The web is our database."', color: '#F8FAFC', size: 'text-4xl md:text-6xl', weight: 'font-black', delay: 0 },
  { text: "But databases don't constantly change their structure.", color: '#A1A1B5', size: 'text-xl md:text-3xl', weight: 'font-normal', delay: 0.3 },
  { text: 'The web does.', color: '#FF1744', size: 'text-3xl md:text-5xl', weight: 'font-bold', delay: 0.6 },
  { text: "That's why our scrapers heal themselves.", color: '#00E5FF', size: 'text-3xl md:text-5xl', weight: 'font-bold', delay: 0.9 },
]

const WEB_NODES = ['Business', 'Website', 'Review', 'Competitor', 'Social', 'Location', 'Product', 'Pricing']
const NODE_COLORS = ['#00E5FF', '#EC0AFF', '#FF1744', '#6D28D9', '#00E5FF', '#EC0AFF', '#FF1744', '#6D28D9']

export function WebDatabase() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="web-database"
      ref={ref}
      className="relative py-32 md:py-40 overflow-hidden border-b border-white/5 bg-void"
      aria-label="The web is our database"
    >
      <div className="absolute inset-0 halftone opacity-20 pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {STORY.map((line, i) => (
            <motion.p
              key={i}
              className={`${line.size} ${line.weight} leading-tight font-display tracking-tight`}
              style={{ color: line.color }}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: line.delay, duration: 0.6, ease: 'easeOut' }}
            >
              {line.text}
            </motion.p>
          ))}
        </div>

        <motion.div
          className="mt-24 space-y-12"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.2, duration: 0.8 }}
        >
          <p className="text-center text-xs font-mono tracking-widest text-muted uppercase">
            SCRAPING ENGINE CONNECTS UNSTRUCTURED SIGNALS
          </p>

          <div className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
            {WEB_NODES.map((node, i) => (
              <motion.div
                key={node}
                className="px-4 py-2 rounded-full text-xs font-mono font-semibold border backdrop-blur-md glass-card"
                style={{
                  color: NODE_COLORS[i],
                  borderColor: `${NODE_COLORS[i]}40`,
                }}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={inView ? { scale: 1, opacity: 1 } : {}}
                transition={{ delay: 1.4 + i * 0.08, type: 'spring' }}
              >
                {node}
              </motion.div>
            ))}
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="w-px h-12 bg-gradient-to-b from-transparent to-magenta" />
            <div className="glass-panel px-8 py-4 text-center border-magenta/40">
              <span className="font-mono text-sm font-bold text-magenta tracking-wider">
                ⚡ BRIGHT DATA SCRAPER STUDIO
              </span>
            </div>
            <div className="w-px h-12 bg-gradient-to-b from-magenta to-cyan" />
            <div className="glass-panel px-8 py-4 text-center border-cyan/40">
              <span className="font-mono text-sm font-bold text-cyan tracking-wider">
                🧠 GEMINI STRUCTURED INTELLIGENCE
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
