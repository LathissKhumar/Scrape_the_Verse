'use client'
import { motion } from 'framer-motion'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { CheckCircle } from 'lucide-react'

const STEPS = [
  {
    num: '01',
    title: 'Lead Discovered',
    content: 'Atlas Kliniek found via directory scraping. Amsterdam, dental services, website URL extracted.',
  },
  {
    num: '02',
    title: 'Lead Normalized',
    content: 'Business profile created: B2C dental clinic, Amsterdam, specialized services, existing website.',
  },
  {
    num: '03',
    title: 'Website Audited',
    content: 'SEO score: 72/100. 39 pages missing meta descriptions. 24 titles too long. No dedicated service pages found. H1 missing on key pages.',
  },
  {
    num: '04',
    title: 'Business Analyzed',
    content: 'Core service: Dental Anxiety Treatment. Primary customer: anxiety patients. Customer needs: gentle techniques, extended consultations, sedation options.',
  },
  {
    num: '05',
    title: 'Opportunity Detected',
    content: 'No dedicated Dental Anxiety Treatment page exists — despite being the core service and primary customer search intent.',
  },
  {
    num: '06',
    title: 'Service Recommended',
    content: 'SEO optimization + dedicated service page development + content improvement for anxiety treatment.',
  },
  {
    num: '07',
    title: 'Prompt Generated',
    content: 'Implementation-ready spec delivered. Architecture, page content, SEO rules, UX guidelines, conversion flow — ready to paste into Lovable, v0, or Claude Code.',
  },
]

export function LiveExample() {
  return (
    <section
      id="live-example"
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Live Pipeline Example — Atlas Kliniek"
    >
      <div className="max-w-5xl mx-auto px-6 lg:px-8 space-y-16">
        {/* Header */}
        <motion.div
          className="text-center space-y-3"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-15%' }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="REAL EXAMPLE" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Watch the Pipeline Run on a{' '}
            <GradientText>Real Business</GradientText>
          </h2>
          <p className="text-base text-text-secondary font-body">
            Atlas Kliniek · Amsterdam · Dental Services
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-sky-400/60 via-indigo-400/40 to-transparent hidden md:block" />

          <div className="flex flex-col gap-6">
            {STEPS.map((step, i) => (
              <motion.div
                key={step.num}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: '-10%' }}
                transition={{
                  delay: i * 0.12,
                  duration: 0.55,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="relative md:ml-16 glass-card p-6 rounded-2xl border border-white/20 group hover:border-sky-400/40 transition-all duration-300"
              >
                {/* Node dot */}
                <div className="absolute -left-[3.15rem] top-1/2 -translate-y-1/2 hidden md:flex w-7 h-7 rounded-full border-2 border-sky-400 bg-[#07090D] items-center justify-center shadow-[0_0_12px_rgba(56,189,248,0.5)]">
                  <CheckCircle className="w-3.5 h-3.5 text-sky-400" />
                </div>

                <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                  <span className="text-2xl font-black font-mono text-sky-400 shrink-0">
                    {step.num}
                  </span>
                  <div className="space-y-1.5">
                    <h3 className="font-bold font-display text-text-primary group-hover:text-sky-300 transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-sm font-body text-slate-300/80 leading-relaxed">
                      {step.content}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}