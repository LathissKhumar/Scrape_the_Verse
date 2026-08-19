'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Search, Zap, ShieldCheck, BrainCircuit, Rocket } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { SectionLabel } from '@/components/ui/SectionLabel'
import { PIPELINE_STAGES } from '@/lib/mock-data'

const STAGE_ICONS: Record<string, React.ReactNode> = {
  search: <Search className="w-5 h-5 text-violet-accent" />,
  zap: <Zap className="w-5 h-5 text-blue-accent" />,
  'shield-check': <ShieldCheck className="w-5 h-5 text-emerald-success" />,
  'brain-circuit': <BrainCircuit className="w-5 h-5 text-violet-accent" />,
  rocket: <Rocket className="w-5 h-5 text-blue-accent" />,
}

export function Pipeline() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="pipeline" ref={ref} className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body" aria-label="5-stage core pipeline">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center mb-20 space-y-4">
          <SectionLabel label="Pipeline Architecture" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            <GradientText>Five Autonomous Stages.</GradientText> One Continuous Loop.
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Raw web discovery feeds parallel research collectors, guarded by self-healing CI logic and converted into sales actions by AI agents.
          </p>
        </div>

        <div className="relative">
          {/* Vertical center line */}
          <div
            className="hidden lg:block absolute left-1/2 top-4 bottom-4 w-0.5 -translate-x-1/2 opacity-30"
            style={{
              background: 'linear-gradient(to bottom, #6D28D9, #8B5CF6, #38BDF8, #34D399)',
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
                transition={{ delay: i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              >
                <div className={`flex-1 w-full ${i % 2 === 0 ? 'lg:text-right' : 'lg:text-left'}`}>
                  <motion.div
                    whileHover={{ scale: 1.015, y: -2 }}
                    className="glass-level-2 p-8 inline-block max-w-lg text-left space-y-3 border-white/10 hover:border-violet-accent/40 transition-all duration-300"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold tracking-widest text-violet-accent">
                        STAGE {stage.stage}
                      </span>
                      <span className="lg:hidden">{STAGE_ICONS[stage.icon]}</span>
                    </div>
                    <h3 className="text-2xl font-bold font-display text-text-primary">
                      {stage.title}
                    </h3>
                    <p className="text-sm font-body leading-relaxed text-text-secondary">
                      {stage.description}
                    </p>
                  </motion.div>
                </div>

                {/* Center node */}
                <motion.div
                  whileHover={{ scale: 1.15 }}
                  className="hidden lg:flex w-14 h-14 rounded-2xl border-2 items-center justify-center text-2xl shrink-0 z-10 shadow-xl shadow-violet-accent/15 backdrop-blur-md cursor-pointer"
                  style={{ borderColor: '#8B5CF6', backgroundColor: 'rgba(13, 17, 23, 0.9)' }}
                >
                  {STAGE_ICONS[stage.icon]}
                </motion.div>

                <div className="flex-1 hidden lg:block" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
