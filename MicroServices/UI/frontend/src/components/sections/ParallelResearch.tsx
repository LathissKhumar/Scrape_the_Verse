"use client";
import { motion } from "framer-motion";
import { useRef } from "react";
import { Zap, CheckCircle2 } from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { NeonBadge } from "@/components/ui/NeonBadge";
import { RESEARCH_COLLECTORS } from "@/lib/mock-data";

export function ParallelResearch() {
  const ref = useRef(null);

  return (
    <section
      id="parallel-research"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Parallel Research"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header with Blur Text Reveal */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, y: 30, filter: "blur(10px)" }}
          whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="02" label="Parallel Web Research" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Every prospect <GradientText>tells a different story.</GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Four independent collectors evaluate website presence, customer
            reviews, competitor density, and social engagement concurrently.
          </p>
        </motion.div>

        {/* Fan-out Header Node */}
        <motion.div
          className="flex flex-col items-center gap-4 mb-14"
          initial={{ opacity: 0, scale: 0.85 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="glass-level-2 px-8 py-4 text-center border-sky-400/60 bg-white/10 backdrop-blur-md shadow-lg">
            <div className="font-bold font-mono text-base text-sky-400 flex items-center justify-center gap-2">
              <Zap className="w-4 h-4 text-sky-400" />
              <span>PROSPECT IDENTIFIED</span>
            </div>
            <div className="text-xs font-mono text-slate-200 font-semibold mt-1">
              Urban Brew Café · Chennai, India
            </div>
          </div>
          <div className="w-0.5 h-10 bg-gradient-to-b from-sky-400 via-indigo-400 to-transparent opacity-90" />
          <span className="text-xs font-mono tracking-widest text-slate-200 font-semibold uppercase">
            CONCURRENT COLLECTOR EXECUTION
          </span>
        </motion.div>

        {/* 4 Collector Cards — 3D Perspective Staggered Slide (Matching Scroll_UI.mp4) */}
        <div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8"
          style={{ perspective: "1200px" }}
        >
          {RESEARCH_COLLECTORS.map((collector, i) => (
            <motion.div
              key={collector.id}
              initial={{ opacity: 0, x: 80, rotateY: -15, scale: 0.9 }}
              whileInView={{ opacity: 1, x: 0, rotateY: 0, scale: 1 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                delay: i * 0.14,
                duration: 0.8,
                ease: [0.16, 1, 0.3, 1],
              }}
            >
              <motion.div
                whileHover={{ y: -6, scale: 1.02 }}
                className="glass-card p-6 h-full space-y-4 flex flex-col justify-between hover:border-sky-400/60 shadow-xl"
              >
                <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-3">
                  <span className="font-bold text-base font-display text-text-primary">
                    {collector.title}
                  </span>
                  <NeonBadge label="SCRAPING" variant="running" />
                </div>
                <div className="space-y-2.5 font-mono text-xs">
                  {collector.metrics.map((m) => (
                    <div
                      key={m.label}
                      className="flex items-center justify-between"
                    >
                      <span className="text-slate-200 font-semibold">
                        {m.label}
                      </span>
                      <span className="text-sky-400 font-bold">{m.value}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>

        {/* Converge Node */}
        <motion.div
          className="flex flex-col items-center gap-4 mt-14"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ delay: 0.6, duration: 0.7 }}
        >
          <div className="w-0.5 h-12 bg-gradient-to-b from-transparent via-indigo-400 to-sky-400 opacity-90" />
          <div className="glass-level-2 px-10 py-5 text-center border-sky-400/60 bg-white/10 backdrop-blur-md shadow-xl flex flex-col items-center gap-1.5">
            <div className="font-bold tracking-wider font-mono text-sky-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>UNIFIED BUSINESS INTELLIGENCE PROFILE</span>
            </div>
            <div className="text-xs font-mono text-slate-200 font-semibold">
              Lead Score: 92/100 · Opportunity: High Priority
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
