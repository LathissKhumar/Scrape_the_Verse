'use client'
import { motion } from 'framer-motion'
import { useRef } from 'react'
import { Database, ShieldCheck, BrainCircuit, Rocket, Cpu } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'

const ARCHITECTURE_LAYERS = [
  {
    layer: 'Layer 1',
    title: 'Bright Data Scraper Studio',
    subtitle: 'Data Ingestion & Discovery Fleet',
    icon: <Database className="w-5 h-5 text-sky-400" />,
    description: 'Manages proxy rotation, rate limits, and multi-source web collection across maps and business registries.',
    glow: 'radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)',
  },
  {
    layer: 'Layer 2',
    title: 'Self-Healing CI Engine',
    subtitle: 'Autonomous Rule Generation',
    icon: <ShieldCheck className="w-5 h-5 text-violet-400" />,
    description: 'Monitors payload variations, detects broken CSS/DOM paths, and generates replacement extraction rules.',
    glow: 'radial-gradient(ellipse at top right, rgba(139, 92, 246, 0.25) 0%, transparent 65%)',
  },
  {
    layer: 'Layer 3',
    title: 'Gemini AI Intelligence',
    subtitle: 'Structured Reasoning & Scoring',
    icon: <BrainCircuit className="w-5 h-5 text-emerald-400" />,
    description: 'Normalizes unstructured web payloads into typed JSON objects, scores lead intent, and identifies opportunities.',
    glow: 'radial-gradient(ellipse at bottom left, rgba(52, 211, 153, 0.25) 0%, transparent 65%)',
  },
  {
    layer: 'Layer 4',
    title: 'Autonomous Sales Suite',
    subtitle: 'Automated Outreach & Monitoring',
    icon: <Rocket className="w-5 h-5 text-cyan-400" />,
    description: 'Generates custom mobile micro-sites, personalized outreach emails, voice call briefs, and domain watch alerts.',
    glow: 'radial-gradient(ellipse at bottom right, rgba(34, 211, 238, 0.25) 0%, transparent 65%)',
  },
]

export function Architecture() {
  const ref = useRef(null)

  return (
    <section
      id="architecture"
      ref={ref}
      className="py-20 md:py-32 relative border-b border-white/5 bg-transparent font-body"
      aria-label="System Architecture — Circular Orbit"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-8 sm:mb-12 space-y-4 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
          whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Enterprise Infrastructure" />
          <h2 className="text-3xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Modular. Resilient. <GradientText>Production-Ready.</GradientText>
          </h2>
          <p className="text-sm sm:text-base text-text-secondary max-w-xl mx-auto font-body">
            Four decoupled architecture layers rolling circularly in an autonomous orbital system around AgencyOS core.
          </p>
        </motion.div>

        {/* Circular Orbit Ring Viewport — Generous height & radius so cards and center NEVER overlap */}
        <div className="relative w-full min-h-[720px] sm:min-h-[840px] md:min-h-[920px] flex items-center justify-center my-4 py-8">
          {/* Static Central Engine Core — Simple & Clean Orb */}
          <div className="absolute z-30 flex flex-col items-center justify-center pointer-events-auto">
            <motion.div
              animate={{ scale: [1, 1.04, 1] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              className="relative w-32 h-32 sm:w-36 sm:h-36 md:w-40 md:h-40 rounded-full glass-level-3 border-2 border-sky-400/60 shadow-[0_0_50px_rgba(56,189,248,0.5)] backdrop-blur-3xl flex flex-col items-center justify-center text-center p-3 overflow-hidden group"
              style={{
                boxShadow:
                  '0 20px 50px rgba(0, 0, 0, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.5)',
              }}
            >
              {/* Glow Accent */}
              <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/20 via-indigo-500/10 to-transparent pointer-events-none" />

              {/* Status Pulse */}
              <div className="relative z-10 flex items-center gap-1 mb-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="text-[9px] font-mono font-bold text-emerald-400 uppercase tracking-wider">
                  ACTIVE
                </span>
              </div>

              {/* Brand Logo in Center */}
              <div className="relative z-10 py-0.5">
                <img
                  src="/images/Main_logo_vibrant.png"
                  alt="AgencyOS Logo"
                  className="h-6 sm:h-7 md:h-8 object-contain filter drop-shadow-[0_2px_10px_rgba(56,189,248,0.6)] saturate-[1.2]"
                />
              </div>

              {/* Simple Bottom Label */}
              <div className="relative z-10 text-[9px] sm:text-[10px] font-mono text-cyan-300 font-bold uppercase tracking-widest mt-1">
                CORE ENGINE
              </div>
            </motion.div>
          </div>

          {/* Continuously Rotating Orbital Container — Expanded radius so cards rotate far outside center core */}
          <motion.div
            className="relative w-[520px] h-[520px] sm:w-[660px] sm:h-[660px] md:w-[780px] md:h-[780px] flex items-center justify-center"
            animate={{ rotate: 360 }}
            transition={{
              repeat: Infinity,
              duration: 38,
              ease: 'linear',
            }}
          >
            {/* White Lined Orbit Ring Line — Reduced opacity */}
            <div className="absolute inset-4 sm:inset-6 md:inset-8 rounded-full border border-white/20 shadow-[0_0_15px_rgba(255,255,255,0.12)] pointer-events-none opacity-60" />
            <div className="absolute inset-0 rounded-full border border-dashed border-sky-400/15 pointer-events-none opacity-40" />
            <div className="absolute inset-10 sm:inset-14 rounded-full border border-white/08 pointer-events-none opacity-30" />

            {/* 4 Square Blocks Rolling along the White Lined Orbit */}
            {ARCHITECTURE_LAYERS.map((layer, i) => {
              // Angles: 0 deg (Top), 90 deg (Right), 180 deg (Bottom), 270 deg (Left)
              const angleDeg = i * 90 - 90
              const rad = (angleDeg * Math.PI) / 180
              const radiusPercent = 43 // 43% radius keeps cards orbiting far outside the center core

              const leftPos = 50 + radiusPercent * Math.cos(rad)
              const topPos = 50 + radiusPercent * Math.sin(rad)

              return (
                <div
                  key={layer.layer}
                  className="absolute -translate-x-1/2 -translate-y-1/2 z-10"
                  style={{
                    left: `${leftPos}%`,
                    top: `${topPos}%`,
                  }}
                >
                  {/* Counter-rotation keeps square blocks upright while rolling in orbit */}
                  <motion.div
                    animate={{ rotate: -360 }}
                    transition={{
                      repeat: Infinity,
                      duration: 38,
                      ease: 'linear',
                    }}
                    whileHover={{ scale: 1.06 }}
                    className="w-44 h-44 sm:w-56 sm:h-56 md:w-64 md:h-64 p-4 sm:p-5 rounded-2xl flex flex-col justify-between glass-liquid border border-white/30 shadow-2xl backdrop-blur-2xl transition-all duration-300 group hover:border-sky-400/80 cursor-pointer overflow-hidden relative"
                    style={{
                      boxShadow:
                        '0 20px 45px rgba(0, 0, 0, 0.45), inset 0 1px 2px rgba(255, 255, 255, 0.5)',
                    }}
                  >
                    {/* Radial Glow */}
                    <div
                      className="absolute inset-0 pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ background: layer.glow }}
                    />
                    <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

                    {/* Top Header */}
                    <div className="relative z-10 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border border-sky-300/35 bg-sky-500/10 text-sky-100 backdrop-blur-md">
                          {layer.layer}
                        </span>
                        <div className="p-1.5 sm:p-2 rounded-xl bg-white/10 border border-white/20 shadow-md group-hover:border-sky-400/60 transition-all shrink-0">
                          {layer.icon}
                        </div>
                      </div>

                      <h3 className="text-sm sm:text-base md:text-lg font-bold font-display text-white group-hover:text-sky-300 transition-colors leading-tight">
                        {layer.title}
                      </h3>
                      <div className="text-[10px] sm:text-xs font-mono text-cyan-300 font-semibold">
                        {layer.subtitle}
                      </div>
                    </div>

                    {/* Body */}
                    <p className="relative z-10 text-[11px] sm:text-xs font-body leading-relaxed text-slate-300/90 line-clamp-4">
                      {layer.description}
                    </p>
                  </motion.div>
                </div>
              )
            })}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
