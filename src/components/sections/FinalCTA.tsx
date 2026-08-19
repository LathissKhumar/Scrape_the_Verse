'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { ArrowRight, Calendar, Sparkles } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

export function FinalCTA() {
  const ref = useRef(null)

  return (
    <section
      id="final-cta"
      ref={ref}
      className="py-36 md:py-48 relative overflow-hidden bg-void border-b border-white/5 font-body"
      aria-label="Final Call to Action"
    >
      {/* Ambient Radial Lighting */}
      <motion.div
        className="absolute inset-0 pointer-events-none opacity-25 blur-[150px]"
        style={{
          background: 'radial-gradient(circle at center, #6D28D9 0%, #8B5CF6 40%, #38BDF8 80%, transparent 100%)',
        }}
        animate={{
          scale: [1, 1.12, 1],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
      />

      <div className="relative max-w-4xl mx-auto px-6 text-center z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.88, y: 45 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-accent/30 bg-violet-accent/10 text-xs font-mono font-medium text-violet-accent backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-violet-accent" />
            <span>ENTERPRISE WEB INTELLIGENCE</span>
          </div>

          <h2 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-display leading-[1.1] tracking-tight text-text-primary">
            The web changes.
            <br />
            <GradientText>Your intelligence adapts.</GradientText>
          </h2>

          <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto font-body leading-relaxed">
            Scrape-Verse continuously discovers, researches and monitors businesses across the web — while self-healing when websites change.
          </p>

          <div className="flex flex-wrap justify-center gap-5 pt-4">
            <Button id="final-cta-primary" variant="primary" className="!text-base !px-9 !py-4 shadow-xl shadow-violet-accent/25 flex items-center gap-2.5">
              <span>Explore the Intelligence Engine</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button id="final-cta-secondary" variant="secondary" className="!text-base !px-9 !py-4 flex items-center gap-2.5">
              <Calendar className="w-4 h-4 text-blue-accent" />
              <span>Schedule Architecture Demo</span>
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
