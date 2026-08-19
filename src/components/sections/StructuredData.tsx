'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { BUSINESS_INTEL_EXAMPLE } from '@/lib/mock-data'

const RAW_SNIPPET = `// Google Maps Scrape (Raw)
{
  "name": "Urban Brew Café",
  "rating": "4.7 (280 reviews)",
  "phone": "(512) 555-0142",
  "categories": ["Coffee", "Café"],
  "website": null,
  "hours": { "Mon": "7am-9pm" }
}`

const STRUCTURED_OUTPUT = `{
  "businessName": "Urban Brew Café",
  "website": null,
  "rating": 4.7,
  "reviews": 280,
  "competitors": 12,
  "websiteQuality": 0,
  "leadScore": 92,
  "opportunity": "High",
  "recommendation": "Build modern website"
}`

export function StructuredData() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="structured-data" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="Structured Intelligence">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-16 space-y-4">
          <SectionLabel stage="04" label="Structured Intelligence" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            Raw Web Scrape →{' '}
            <GradientText gradient="recovery">AI-Ready Intelligence.</GradientText>
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Bright Data extracts raw HTML/JSON; Gemini normalizes and scores the output into action-oriented business profiles.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Raw Scrape */}
          <div className="lg:col-span-5 glass-panel overflow-hidden">
            <div className="px-5 py-3 border-b border-white/10 text-xs font-mono font-bold text-muted bg-white/5">
              RAW UNSTRUCTURED DATA
            </div>
            <pre className="p-6 text-xs font-mono text-muted leading-relaxed overflow-x-auto bg-[#05050A]/90">
              {RAW_SNIPPET}
            </pre>
          </div>

          {/* Arrow Center */}
          <div className="lg:col-span-2 flex flex-col items-center justify-center gap-3 py-4">
            <div className="w-px h-8 bg-gradient-to-b from-transparent to-cyan hidden lg:block" />
            <div className="glass-panel px-6 py-3 text-center border-cyan/40 shadow-lg shadow-cyan/10">
              <span className="font-mono text-xs font-bold text-cyan">GEMINI AI</span>
            </div>
            <div className="w-px h-8 bg-gradient-to-b from-cyan to-transparent hidden lg:block" />
          </div>

          {/* Structured Output */}
          <div className="lg:col-span-5 glass-panel overflow-hidden border-cyan/30">
            <div className="px-5 py-3 border-b border-white/10 text-xs font-mono font-bold text-cyan bg-cyan/5">
              STRUCTURED BUSINESS PROFILE
            </div>
            <pre className="p-6 text-xs font-mono text-cyan leading-relaxed overflow-x-auto bg-[#05050A]/90">
              {STRUCTURED_OUTPUT}
            </pre>
          </div>
        </div>

        {/* Lead Score Card */}
        <motion.div
          className="mt-12 glass-panel p-8 max-w-lg mx-auto space-y-4 border-cyan/40 shadow-xl shadow-cyan/10"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <span className="font-bold font-display text-lg text-cyan">
              {BUSINESS_INTEL_EXAMPLE.businessName}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan/10 text-cyan border border-cyan/30">
              OPPORTUNITY: {BUSINESS_INTEL_EXAMPLE.opportunity}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            {[
              { label: 'Rating', value: `${BUSINESS_INTEL_EXAMPLE.rating} ★` },
              { label: 'Reviews', value: BUSINESS_INTEL_EXAMPLE.reviews },
              { label: 'Competitors', value: BUSINESS_INTEL_EXAMPLE.competitors },
              { label: 'Website Score', value: `${BUSINESS_INTEL_EXAMPLE.websiteQuality}%` },
            ].map((item) => (
              <div key={item.label} className="flex justify-between py-1 border-b border-white/5">
                <span className="text-muted">{item.label}:</span>
                <span className="text-off-white font-medium">{item.value}</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="font-mono text-sm font-bold text-magenta">AI LEAD SCORE</span>
            <span
              className="text-3xl font-black font-display"
              style={{
                background: 'linear-gradient(135deg, #EC0AFF, #00E5FF)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {BUSINESS_INTEL_EXAMPLE.leadScore} / 100
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
