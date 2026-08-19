'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

export function FinalCTA() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="final-cta"
      ref={ref}
      className="py-36 md:py-48 relative overflow-hidden bg-void border-b border-white/5"
      aria-label="Final Call to Action"
    >
      {/* Radial Glow */}
      <div
        className="absolute inset-0 pointer-events-none opacity-30 blur-[140px]"
        style={{
          background: 'radial-gradient(circle at center, #240044 0%, #EC0AFF 40%, transparent 75%)',
        }}
      />
      <div className="absolute inset-0 halftone opacity-20 pointer-events-none" />

      <div className="relative max-w-4xl mx-auto px-6 text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="space-y-8"
        >
          <div
            className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border text-xs font-mono tracking-wider backdrop-blur-md"
            style={{ color: '#EC0AFF', borderColor: 'rgba(236,10,255,0.3)', backgroundColor: 'rgba(236,10,255,0.08)' }}
          >
            <span
              className="w-2 h-2 rounded-full animate-ping"
              style={{ backgroundColor: '#EC0AFF' }}
            />
            HACKATHON SUBMISSION 2026
          </div>

          <h2
            className="text-5xl sm:text-6xl lg:text-7xl font-black font-display leading-[1.1] tracking-tight"
          >
            The Web Is Your <GradientText>Database.</GradientText>
            <br />
            We Make It <GradientText gradient="healing">Unbreakable.</GradientText>
          </h2>

          <p className="text-lg sm:text-xl text-muted max-w-2xl mx-auto font-body leading-relaxed">
            Self-healing web intelligence that discovers, understands, and converts business opportunities — completely autonomously.
          </p>

          <div className="flex flex-wrap justify-center gap-5 pt-4">
            <Button id="final-cta-primary" variant="primary" className="!text-base !px-9 !py-4 shadow-xl shadow-magenta/25">
              Explore Scrape-Verse
            </Button>
            <Button id="final-cta-secondary" variant="secondary" className="!text-base !px-9 !py-4 backdrop-blur-md">
              View Architecture Specs
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
