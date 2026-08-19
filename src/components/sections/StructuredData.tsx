'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Code, ArrowRight, BrainCircuit } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const RAW_HTML_SNIPPET = `<div class="biz-card-984">
  <h2 class="title_v2">Urban Brew Café</h2>
  <span class="loc-pin">Chennai, Tamil Nadu</span>
  <div class="rev-box">4.7 stars (280 reviews)</div>
  <p class="status-no-web">No official site found</p>
</div>`

const STRUCTURED_JSON_SNIPPET = `{
  "businessName": "Urban Brew Café",
  "location": "Chennai, India",
  "rating": 4.7,
  "reviews": 280,
  "hasWebsite": false,
  "digitalPresenceScore": 38,
  "leadScore": 92,
  "opportunity": "HIGH"
}`

export function StructuredData() {
  const ref = useRef(null)

  return (
    <section id="structured-data" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden" aria-label="Structured Data Intelligence">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, x: 60, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="04" label="Structured Data Intelligence" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            From raw web noise to <GradientText>structured JSON payload.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Scrape-Verse parses unpredictable HTML payloads into validated, type-safe JSON objects ready for Gemini AI analysis.
          </p>
        </motion.div>

        {/* Code Comparison Split Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center max-w-5xl mx-auto">
          {/* Raw HTML */}
          <motion.div
            className="lg:col-span-5"
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-level-2 overflow-hidden border-white/15 shadow-xl">
              <div className="px-5 py-3.5 border-b border-white/10 bg-white/5 font-mono text-xs flex items-center justify-between">
                <span className="text-muted flex items-center gap-2">
                  <Code className="w-3.5 h-3.5 text-rose-error" />
                  <span>RAW UNSTRUCTURED HTML</span>
                </span>
                <span className="text-rose-error text-[11px]">UNPREDICTABLE</span>
              </div>
              <pre className="p-6 text-xs font-mono text-muted leading-relaxed overflow-x-auto bg-black/40">
                <code>{RAW_HTML_SNIPPET}</code>
              </pre>
            </div>
          </motion.div>

          {/* Arrow */}
          <motion.div
            className="lg:col-span-2 flex flex-col items-center justify-center py-4"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="p-4 rounded-full bg-violet-accent/15 border border-violet-accent/30 text-violet-accent shadow-xl">
              <ArrowRight className="w-6 h-6 rotate-90 lg:rotate-0" />
            </div>
            <span className="text-[11px] font-mono text-violet-accent mt-2 font-bold flex items-center gap-1">
              <BrainCircuit className="w-3.5 h-3.5" />
              <span>GEMINI AI PARSER</span>
            </span>
          </motion.div>

          {/* Structured JSON */}
          <motion.div
            className="lg:col-span-5"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-level-3 overflow-hidden border-blue-accent/30 shadow-2xl">
              <div className="px-5 py-3.5 border-b border-white/10 bg-white/5 font-mono text-xs flex items-center justify-between">
                <span className="text-blue-accent font-bold flex items-center gap-2">
                  <Code className="w-3.5 h-3.5 text-blue-accent" />
                  <span>STRUCTURED JSON OBJECT</span>
                </span>
                <span className="text-emerald-success text-[11px] font-bold">TYPE-SAFE</span>
              </div>
              <pre className="p-6 text-xs font-mono text-blue-accent leading-relaxed overflow-x-auto bg-black/40">
                <code>{STRUCTURED_JSON_SNIPPET}</code>
              </pre>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
