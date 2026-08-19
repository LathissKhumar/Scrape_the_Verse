'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'

const STORY = [
  { text: '"The web is where your next opportunity is hiding."', color: '#F5F7FA', size: 'text-4xl md:text-6xl', weight: 'font-bold', delay: 0 },
  { text: "Unstructured signals published across maps, reviews, directories, and social platforms.", color: '#A7AFBD', size: 'text-xl md:text-2xl', weight: 'font-normal', delay: 0.3 },
]

const WEB_NODES = ['Business Listing', 'Website Status', 'Review Sentiment', 'Competitor Gap', 'Social Signals', 'Location Data', 'Product Offering', 'Pricing Signals']
const NODE_COLORS = ['#38BDF8', '#8B5CF6', '#34D399', '#38BDF8', '#8B5CF6', '#34D399', '#38BDF8', '#8B5CF6']

export function WebDatabase() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="web-database"
      ref={ref}
      className="relative py-32 md:py-40 overflow-hidden border-b border-white/5 bg-void"
      aria-label="Web Intelligence Graph"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center space-y-6">
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
          className="mt-20 space-y-12"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6, duration: 0.8 }}
        >
          <p className="text-center text-xs font-mono tracking-widest text-muted uppercase">
            INTELLIGENCE LAYER SYNTHESIZES UNSTRUCTURED WEB SIGNALS
          </p>

          <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
            {WEB_NODES.map((node, i) => (
              <motion.div
                key={node}
                className="px-4 py-2.5 rounded-xl text-xs font-mono font-medium border backdrop-blur-md glass-card"
                style={{
                  color: NODE_COLORS[i],
                  borderColor: `${NODE_COLORS[i]}30`,
                }}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={inView ? { scale: 1, opacity: 1 } : {}}
                transition={{ delay: 0.8 + i * 0.07, type: 'spring' }}
              >
                <span className="w-1.5 h-1.5 rounded-full inline-block mr-2" style={{ backgroundColor: NODE_COLORS[i] }} />
                {node}
              </motion.div>
            ))}
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="w-px h-12 bg-gradient-to-b from-transparent to-violet-accent" />
            <div className="glass-level-2 px-8 py-4 text-center border-violet-accent/30 shadow-lg">
              <span className="font-mono text-sm font-semibold text-violet-accent tracking-wider">
                ⚡ BRIGHT DATA SCRAPER STUDIO
              </span>
            </div>
            <div className="w-px h-12 bg-gradient-to-b from-violet-accent to-blue-accent" />
            <div className="glass-level-2 px-8 py-4 text-center border-blue-accent/30 shadow-lg">
              <span className="font-mono text-sm font-semibold text-blue-accent tracking-wider">
                🧠 GEMINI STRUCTURED INTELLIGENCE LAYER
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
