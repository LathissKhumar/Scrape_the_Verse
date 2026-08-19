'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { BUSINESS_INTEL_EXAMPLE } from '@/lib/mock-data'

const RAW_SNIPPET = `{
  "name": "Urban Brew Café",
  "rating": "4.7 (280 reviews)",
  "location": "Chennai, India",
  "website": null,
  "competitors": 5
}`

const STRUCTURED_OUTPUT = `{
  "businessName": "Urban Brew Café",
  "website": null,
  "rating": 4.7,
  "reviews": 280,
  "digitalPresence": 38,
  "leadScore": 92,
  "opportunity": "HIGH",
  "recommendation": "Modern website + online ordering"
}`

export function StructuredData() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="structured-data" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Structured Data Intelligence">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="04" label="Structured Intelligence" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            From raw web data <GradientText gradient="blue">to business intelligence.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Raw payload payload normalizes directly into structured JSON and passes into Gemini AI models for scoring.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Raw Scrape Data */}
          <div className="lg:col-span-5 glass-level-2 overflow-hidden">
            <div className="px-6 py-3.5 border-b border-white/10 text-xs font-mono font-bold text-muted bg-white/5">
              RAW UNSTRUCTURED PAYLOAD
            </div>
            <pre className="p-6 text-xs font-mono text-muted leading-relaxed overflow-x-auto bg-[#07090D]/90">
              {RAW_SNIPPET}
            </pre>
          </div>

          {/* Center Arrow */}
          <div className="lg:col-span-2 flex flex-col items-center justify-center gap-3 py-4">
            <div className="w-px h-8 bg-gradient-to-b from-transparent to-blue-accent hidden lg:block" />
            <div className="glass-level-2 px-6 py-3 text-center border-blue-accent/40 shadow-lg shadow-blue-accent/10">
              <span className="font-mono text-xs font-bold text-blue-accent">GEMINI AI REASONING</span>
            </div>
            <div className="w-px h-8 bg-gradient-to-b from-blue-accent to-transparent hidden lg:block" />
          </div>

          {/* Structured Intelligence */}
          <div className="lg:col-span-5 glass-level-2 overflow-hidden border-blue-accent/30">
            <div className="px-6 py-3.5 border-b border-white/10 text-xs font-mono font-bold text-blue-accent bg-blue-accent/5">
              STRUCTURED INTELLIGENCE OUTPUT
            </div>
            <pre className="p-6 text-xs font-mono text-blue-accent leading-relaxed overflow-x-auto bg-[#07090D]/90">
              {STRUCTURED_OUTPUT}
            </pre>
          </div>
        </div>

        {/* Intelligence Score Card */}
        <motion.div
          className="mt-12 glass-level-3 p-8 max-w-xl mx-auto space-y-6 border-blue-accent/30 shadow-2xl"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <h3 className="font-bold font-display text-xl text-text-primary">
                {BUSINESS_INTEL_EXAMPLE.businessName}
              </h3>
              <p className="text-xs font-mono text-muted">{BUSINESS_INTEL_EXAMPLE.location}</p>
            </div>
            <span className="px-3.5 py-1 rounded-full text-xs font-mono font-bold bg-emerald-success/10 text-emerald-success border border-emerald-success/30">
              OPPORTUNITY: {BUSINESS_INTEL_EXAMPLE.opportunity}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            <div className="glass-card p-4">
              <div className="text-muted">Digital Presence</div>
              <div className="text-xl font-bold text-blue-accent mt-1">{BUSINESS_INTEL_EXAMPLE.digitalPresenceScore} / 100</div>
            </div>
            <div className="glass-card p-4">
              <div className="text-muted">Lead Score</div>
              <div className="text-xl font-bold text-violet-accent mt-1">{BUSINESS_INTEL_EXAMPLE.leadScore} / 100</div>
            </div>
          </div>

          <div className="space-y-1.5 bg-white/5 p-4 rounded-xl border border-white/5 text-xs font-mono">
            <span className="text-muted uppercase">Recommendation:</span>
            <p className="text-text-secondary font-body font-normal leading-relaxed">
              &quot;{BUSINESS_INTEL_EXAMPLE.recommendation}&quot;
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
