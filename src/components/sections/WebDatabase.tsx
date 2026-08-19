'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

const STORY = [
  { text: '"The web is where your next opportunity is hiding."', color: '#F5F7FA', size: 'text-4xl md:text-6xl', weight: 'font-bold', delay: 0 },
  { text: "Unstructured signals published across maps, reviews, directories, and social platforms.", color: '#A7AFBD', size: 'text-xl md:text-2xl', weight: 'font-normal', delay: 0.25 },
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
      className="relative py-32 md:py-40 overflow-hidden border-b border-white/5 bg-transparent font-body"
      aria-label="Web Intelligence Graph"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Animated Text Blur Reveal (Matching Scroll_UI.mp4 Frame 00:05) */}
        <div className="max-w-4xl mx-auto text-center space-y-6">
          {STORY.map((line, i) => (
            <motion.p
              key={i}
              className={`${line.size} ${line.weight} leading-tight font-display tracking-tight`}
              style={{ color: line.color }}
              initial={{ opacity: 0, y: 30, filter: 'blur(12px)' }}
              animate={inView ? { opacity: 1, y: 0, filter: 'blur(0px)' } : {}}
              transition={{ delay: line.delay, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              {line.text}
            </motion.p>
          ))}
        </div>

        {/* 3D Tilt Perspective Container (Matching Scroll_UI.mp4 3D Scroll) */}
        <motion.div
          className="mt-20 space-y-12"
          style={{ perspective: '1200px' }}
          initial={{ opacity: 0, rotateX: 15, y: 40 }}
          animate={inView ? { opacity: 1, rotateX: 0, y: 0 } : {}}
          transition={{ delay: 0.5, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="text-center text-xs font-mono tracking-widest text-muted uppercase">
            INTELLIGENCE LAYER SYNTHESIZES UNSTRUCTURED WEB SIGNALS
          </p>

          <div className="flex flex-wrap justify-center gap-3.5 max-w-4xl mx-auto">
            {WEB_NODES.map((node, i) => (
              <motion.div
                key={node}
                className="px-4 py-2.5 rounded-xl text-xs font-mono font-medium border backdrop-blur-md glass-card"
                style={{
                  color: NODE_COLORS[i],
                  borderColor: `${NODE_COLORS[i]}35`,
                }}
                initial={{ scale: 0.85, opacity: 0, y: 20 }}
                animate={inView ? { scale: 1, opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.6 + i * 0.08, type: 'spring', stiffness: 120, damping: 15 }}
                whileHover={{ scale: 1.05, y: -4 }}
              >
                <span className="w-1.5 h-1.5 rounded-full inline-block mr-2" style={{ backgroundColor: NODE_COLORS[i] }} />
                {node}
              </motion.div>
            ))}
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="w-px h-12 bg-gradient-to-b from-transparent to-violet-accent" />
            <motion.div
              whileHover={{ scale: 1.03 }}
              className="glass-level-2 px-8 py-4 text-center border-violet-accent/30 shadow-lg"
            >
              <span className="font-mono text-sm font-semibold text-violet-accent tracking-wider">
                ⚡ BRIGHT DATA SCRAPER STUDIO
              </span>
            </motion.div>
            <div className="w-px h-12 bg-gradient-to-b from-violet-accent to-blue-accent" />
            <motion.div
              whileHover={{ scale: 1.03 }}
              className="glass-level-2 px-8 py-4 text-center border-blue-accent/30 shadow-lg"
            >
              <span className="font-mono text-sm font-semibold text-blue-accent tracking-wider">
                🧠 GEMINI STRUCTURED INTELLIGENCE LAYER
              </span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
