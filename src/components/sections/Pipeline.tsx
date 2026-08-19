'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { PIPELINE_STAGES } from '@/lib/mock-data'

export function Pipeline() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="pipeline" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-void" aria-label="5-stage core pipeline">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-20 space-y-4">
          <SectionLabel label="Core Pipeline Architecture" />
          <h2 className="text-4xl md:text-5xl font-black font-display tracking-tight">
            <GradientText>Five Autonomous Stages.</GradientText> One Continuous Loop.
          </h2>
          <p className="text-base text-muted max-w-xl mx-auto font-body">
            Raw web discovery feeds parallel research collectors, guarded by self-healing CI logic and converted into sales actions by AI agents.
          </p>
        </div>

        <div className="relative">
          {/* Vertical center line */}
          <div
            className="hidden lg:block absolute left-1/2 top-4 bottom-4 w-0.5 -translate-x-1/2 opacity-30"
            style={{
              background: 'linear-gradient(to bottom, #240044, #EC0AFF, #00E5FF, #FF1744)',
            }}
          />

          <div className="space-y-12 md:space-y-16">
            {PIPELINE_STAGES.map((stage, i) => (
              <motion.div
                key={stage.stage}
                className={`flex flex-col lg:flex-row items-center gap-8 ${
                  i % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'
                }`}
                initial={{ opacity: 0, y: 30 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: i * 0.12, duration: 0.6, ease: 'easeOut' }}
              >
                <div className={`flex-1 w-full ${i % 2 === 0 ? 'lg:text-right' : 'lg:text-left'}`}>
                  <div className="glass-panel p-8 inline-block max-w-lg text-left space-y-3 border-white/10 hover:border-magenta/40 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold tracking-widest text-magenta">
                        STAGE {stage.stage}
                      </span>
                      <span className="text-xl lg:hidden">{stage.icon}</span>
                    </div>
                    <h3 className="text-2xl font-bold font-display text-off-white">
                      {stage.title}
                    </h3>
                    <p className="text-sm font-body leading-relaxed text-muted">
                      {stage.description}
                    </p>
                  </div>
                </div>

                {/* Center node */}
                <div
                  className="hidden lg:flex w-14 h-14 rounded-2xl border-2 items-center justify-center text-2xl shrink-0 z-10 shadow-xl shadow-magenta/10 backdrop-blur-md"
                  style={{ borderColor: '#EC0AFF', backgroundColor: 'rgba(36, 0, 68, 0.8)' }}
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
