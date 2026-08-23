'use client'
import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { GradientText } from '@/components/ui/GradientText'

export function ImageDistortionSection() {
  const sectionRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start 85%', 'end 30%'],
  })

  // Scroll driven transforms: scale 0.8 -> 1, rotate -5deg -> 0deg
  const scale = useTransform(scrollYProgress, [0, 0.4, 0.8, 1], [0.8, 0.9, 0.98, 1])
  const rotate = useTransform(scrollYProgress, [0, 0.4, 0.8, 1], [-5, -2, 0, 0])
  const textX = useTransform(scrollYProgress, [0, 0.5], [60, 0])
  const textOpacity = useTransform(scrollYProgress, [0, 0.4], [0, 1])

  // Force a true square glass panel with no star polygon.
  const clipPath = useTransform(scrollYProgress, () => 'inset(0% 0% 0% 0% round 0px)')

  return (
    <section
      ref={sectionRef}
      className="py-16 md:py-24 relative border-b border-white/10 bg-transparent font-body overflow-hidden"
      aria-label="Vision Meets Intelligence Distortion"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Morphing Clip-Path Showcase Image */}
          <div className="lg:col-span-6 flex justify-center">
            <motion.div
              style={{ scale, rotate }}
              className="relative w-full max-w-[540px] h-[380px] sm:h-[440px] will-change-transform"
            >
              {/* Animated morphing container — Crystal Glassmorphic */}
              <motion.div
                style={{ clipPath }}
                className="w-full h-full rounded-3xl bg-white/15 border border-white/40 p-8 flex flex-col items-center justify-center relative overflow-hidden shadow-2xl backdrop-blur-2xl"
              >
                {/* Visual glyph with cyan/indigo drop-shadow */}
                <div className="relative z-10 flex flex-col items-center gap-3 text-center">
                  <div className="text-6xl sm:text-7xl select-none filter drop-shadow-[0_0_35px_rgba(56,189,248,0.9)] text-white">
                    ✦
                  </div>
                  <span className="text-xs font-mono font-bold tracking-[0.3em] uppercase text-cyan-300 drop-shadow">
                    Neural DOM Synthesis
                  </span>
                  <p className="text-xs text-slate-100 font-body max-w-xs drop-shadow-md">
                    Continuous geometry morphing aligns raw HTML structures with semantic entities in real time.
                  </p>
                </div>

                {/* Ambient glow in image background */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(56,189,248,0.25)_0%,transparent_70%)] pointer-events-none" />
              </motion.div>
            </motion.div>
          </div>

          {/* Text sliding in from opposite side */}
          <motion.div
            style={{ x: textX, opacity: textOpacity }}
            className="lg:col-span-6 space-y-6 will-change-transform"
          >
            <SectionLabel stage="05" label="Adaptive Vision Engine" />
            <h2 className="text-4xl sm:text-5xl font-bold font-display tracking-tight text-text-primary leading-[1.1]">
              Where <GradientText>Vision</GradientText>
              <br />
              Meets Web Reality.
            </h2>
            <p className="text-base sm:text-lg text-text-secondary font-body leading-relaxed max-w-xl">
              We do not treat scraping as static queries. We craft autonomous intelligence agents that continuously inspect the evolving web — where layout morphs, anti-bot defenses, and DOM updates resolve themselves instantly.
            </p>

            <div className="flex flex-wrap gap-2.5 pt-2">
              {[
                'Multi-Modal LLM Vision',
                'Zero-Downtime Repair',
                'Real-time Morphing',
                'Autonomous Schema Sync',
              ].map((tag) => (
                <span
                  key={tag}
                  data-cursor-hover
                  className="px-4 py-1.5 rounded-full text-xs font-mono font-semibold text-sky-400 bg-sky-950/40 border border-sky-400/30 backdrop-blur-md shadow-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
