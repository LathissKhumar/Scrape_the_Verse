'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

export function FinalCTA() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section
      id="final-cta"
      ref={ref}
      className="py-32 relative overflow-hidden"
      aria-label="Final Call to Action"
    >
      {/* Background */}
      <div
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at center, #240044 0%, transparent 70%)',
        }}
      />
      <div className="absolute inset-0 halftone opacity-15 pointer-events-none" />

      <div className="relative max-w-4xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
        >
          <div
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-mono mb-8"
            style={{ color: '#EC0AFF', borderColor: 'rgba(236,10,255,0.3)', backgroundColor: 'rgba(236,10,255,0.05)' }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: '#EC0AFF', animation: 'pulse 2s infinite' }}
            />
            HACKATHON SUBMISSION 2026
          </div>

          <h2
            className="text-5xl md:text-7xl font-black leading-tight mb-6"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            The web is your{' '}
            <GradientText>database.</GradientText>
            <br />
            We make it{' '}
            <GradientText gradient="healing">unbreakable.</GradientText>
          </h2>

          <p className="text-xl mb-10 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Self-healing web intelligence that discovers, understands, and converts business opportunities — autonomously.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Button id="final-cta-primary" variant="primary" className="!text-base !px-8 !py-4">
              Explore Scrape-Verse
            </Button>
            <Button id="final-cta-secondary" variant="secondary" className="!text-base !px-8 !py-4">
              View on GitHub
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
