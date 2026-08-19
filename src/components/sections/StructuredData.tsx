'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { BUSINESS_INTEL_EXAMPLE } from '@/lib/mock-data'

const RAW_SNIPPET = `// Google Maps scrape result (raw)
const data = {
  name: "Urban Brew Café",
  address: "2109 E 7th St, Austin TX",
  rating: "4.7 (280 reviews)",
  phone: "(512) 555-0142",
  categories: ["Coffee Shop", "Café"],
  website: "—",  // not found
  hours: { Mon: "7am-9pm", ... }
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
  "recommendation": "Build modern website with online ordering"
}`

export function StructuredData() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="structured-data" ref={ref} className="py-24 relative" aria-label="Structured Intelligence">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel stage="04" label="Structured Intelligence" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            Raw web data →{' '}
            <GradientText gradient="recovery">AI-ready intelligence.</GradientText>
          </h2>
          <p className="mt-4 max-w-xl mx-auto" style={{ color: '#A1A1B5' }}>
            Bright Data gives us the raw material. We normalize it into clean JSON, then pass it directly into Gemini.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 items-start">
          {/* Raw */}
          <motion.div
            className="comic-panel overflow-hidden"
            initial={{ opacity: 0, x: -30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="px-4 py-2 border-b text-xs font-mono" style={{ borderColor: 'rgba(255,255,255,0.08)', color: '#A1A1B5' }}>
              RAW WEB SCRAPE
            </div>
            <pre className="p-4 text-xs font-mono overflow-auto leading-5" style={{ color: '#A1A1B5' }}>
              {RAW_SNIPPET}
            </pre>
          </motion.div>

          {/* Arrow + Gemini */}
          <motion.div
            className="flex flex-col items-center justify-center gap-4 py-8"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <div className="text-4xl">→</div>
            <div
              className="comic-panel px-6 py-4 text-center"
              style={{ borderColor: 'rgba(0,229,255,0.4)', backgroundColor: 'rgba(0,229,255,0.06)' }}
            >
              <div className="font-bold font-mono text-sm" style={{ color: '#00E5FF' }}>GEMINI AI</div>
              <div className="text-xs font-mono mt-1" style={{ color: '#A1A1B5' }}>Normalise + Score + Recommend</div>
            </div>
            <div className="text-4xl">→</div>
          </motion.div>

          {/* Structured */}
          <motion.div
            className="comic-panel overflow-hidden"
            style={{ borderColor: 'rgba(0,229,255,0.4)' }}
            initial={{ opacity: 0, x: 30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <div className="px-4 py-2 border-b text-xs font-mono" style={{ borderColor: 'rgba(0,229,255,0.2)', color: '#00E5FF' }}>
              STRUCTURED INTELLIGENCE
            </div>
            <pre className="p-4 text-xs font-mono overflow-auto leading-5" style={{ color: '#00E5FF' }}>
              {STRUCTURED_OUTPUT}
            </pre>
          </motion.div>
        </div>

        {/* Score card */}
        <motion.div
          className="comic-panel max-w-md mx-auto mt-10 p-6 space-y-3"
          style={{ borderColor: 'rgba(0,229,255,0.4)', backgroundColor: 'rgba(0,229,255,0.04)' }}
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.8 }}
        >
          <div className="text-sm font-bold font-mono" style={{ color: '#00E5FF' }}>
            {BUSINESS_INTEL_EXAMPLE.businessName}
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            {[
              { label: 'Rating', value: `${BUSINESS_INTEL_EXAMPLE.rating} ★` },
              { label: 'Reviews', value: BUSINESS_INTEL_EXAMPLE.reviews },
              { label: 'Competitors', value: BUSINESS_INTEL_EXAMPLE.competitors },
              { label: 'Website Quality', value: `${BUSINESS_INTEL_EXAMPLE.websiteQuality}%` },
            ].map((item) => (
              <div key={item.label} className="flex justify-between border-b pb-1" style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
                <span style={{ color: '#A1A1B5' }}>{item.label}</span>
                <span style={{ color: '#F8FAFC' }}>{item.value}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between pt-2">
            <span className="font-mono text-sm font-bold" style={{ color: '#EC0AFF' }}>
              LEAD SCORE
            </span>
            <span
              className="text-2xl font-black"
              style={{
                fontFamily: 'var(--font-display)',
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
