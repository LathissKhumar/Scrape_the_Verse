'use client'
import { motion, useInView, useReducedMotion } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { PIPELINE_STAGES } from '@/lib/mock-data'

export function Pipeline() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const prefersReduced = useReducedMotion()

  return (
    <section id="pipeline" ref={ref} className="py-24 relative" aria-label="5-stage core pipeline">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <SectionLabel label="Core Pipeline" />
          <h2 className="text-4xl md:text-5xl font-black" style={{ fontFamily: 'var(--font-display)' }}>
            <GradientText>Five Stages.</GradientText> One Continuous Loop.
          </h2>
        </div>

        <div className="relative">
          {/* Vertical connector */}
          <div
            className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px opacity-30"
            style={{
              background: 'linear-gradient(to bottom, #240044, #EC0AFF, #00E5FF)',
            }}
          />

          <div className="space-y-10">
            {PIPELINE_STAGES.map((stage, i) => (
              <motion.div
                key={stage.stage}
                className={`flex items-center gap-8 ${i % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}
                initial={!prefersReduced ? { opacity: 0, x: i % 2 === 0 ? -40 : 40 } : false}
                animate={inView ? { opacity: 1, x: 0 } : {}}
                transition={{ delay: i * 0.12, duration: 0.6, ease: 'easeOut' }}
              >
                <div className={`flex-1 ${i % 2 === 0 ? 'lg:text-right' : 'lg:text-left'}`}>
                  <div className="comic-panel p-6 inline-block max-w-sm text-left" style={{ backgroundColor: 'rgba(8,8,16,0.7)' }}>
                    <div className="text-xs font-mono mb-2" style={{ color: '#EC0AFF' }}>
                      STAGE {stage.stage}
                    </div>
                    <h3 className="text-xl font-bold mb-2" style={{ fontFamily: 'var(--font-display)', color: '#F8FAFC' }}>
                      {stage.title}
                    </h3>
                    <p className="text-sm leading-relaxed" style={{ color: '#A1A1B5' }}>
                      {stage.description}
                    </p>
                  </div>
                </div>

                {/* Center node */}
                <div
                  className="hidden lg:flex w-12 h-12 rounded-full border-2 items-center justify-center text-xl flex-shrink-0 relative z-10"
                  style={{ borderColor: '#EC0AFF', backgroundColor: '#240044' }}
                >
                  {stage.icon}
                </div>

                <div className="flex-1 hidden lg:block" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
