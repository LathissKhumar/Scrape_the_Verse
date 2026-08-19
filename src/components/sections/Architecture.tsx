'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Layers, Database, ShieldCheck, BrainCircuit, Rocket } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const ARCHITECTURE_LAYERS = [
  {
    layer: 'Layer 1',
    title: 'Bright Data Scraper Studio',
    subtitle: 'Data Ingestion & Discovery Fleet',
    icon: <Database className="w-5 h-5 text-blue-accent" />,
    description: 'Manages proxy rotation, rate limits, and multi-source web collection across maps and business registries.',
    color: '#38BDF8',
  },
  {
    layer: 'Layer 2',
    title: 'Self-Healing CI & DOM Repair Engine',
    subtitle: 'Autonomous Rule Generation',
    icon: <ShieldCheck className="w-5 h-5 text-violet-accent" />,
    description: 'Monitors payload variations, detects broken CSS/DOM paths, and generates replacement extraction rules.',
    color: '#8B5CF6',
  },
  {
    layer: 'Layer 3',
    title: 'Gemini AI Intelligence Layer',
    subtitle: 'Structured Reasoning & Scoring',
    icon: <BrainCircuit className="w-5 h-5 text-emerald-success" />,
    description: 'Normalizes unstructured web payloads into typed JSON objects, scores lead intent, and identifies opportunities.',
    color: '#34D399',
  },
  {
    layer: 'Layer 4',
    title: 'Autonomous Sales Suite',
    subtitle: 'Automated Outreach & Monitoring',
    icon: <Rocket className="w-5 h-5 text-blue-accent" />,
    description: 'Generates custom mobile micro-sites, personalized outreach emails, voice call briefs, and domain watch alerts.',
    color: '#38BDF8',
  },
]

export function Architecture() {
  const ref = useRef(null)

  return (
    <section id="architecture" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden" aria-label="System Architecture">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-20 space-y-4"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Enterprise Infrastructure" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Modular. Resilient. <GradientText>Production-Ready.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Four decoupled layers ensure high throughput, zero downtime, and end-to-end data integrity.
          </p>
        </motion.div>

        {/* Stacked Architecture Layers — Alternating Slide */}
        <div className="max-w-4xl mx-auto space-y-6">
          {ARCHITECTURE_LAYERS.map((layer, i) => (
            <motion.div
              key={layer.layer}
              initial={{ opacity: 0, x: i % 2 === 0 ? -60 : 60, filter: 'blur(8px)' }}
              whileInView={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ delay: i * 0.12, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            >
              <div
                className="glass-level-2 p-8 border-l-4 space-y-3 hover:border-blue-accent/40 shadow-xl"
                style={{ borderLeftColor: layer.color }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold tracking-widest text-muted uppercase">
                    {layer.layer}
                  </span>
                  <div className="p-2.5 rounded-xl bg-white/5">{layer.icon}</div>
                </div>

                <div>
                  <h3 className="text-2xl font-bold font-display text-text-primary">
                    {layer.title}
                  </h3>
                  <div className="text-xs font-mono text-blue-accent font-medium mt-0.5">
                    {layer.subtitle}
                  </div>
                </div>

                <p className="text-sm font-body leading-relaxed text-text-secondary">
                  {layer.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
