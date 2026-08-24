"use client";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";

const SCORES = [
  { label: "Business Fit", value: 80, color: "from-sky-400 to-cyan-300" },
  { label: "Digital Need", value: 75, color: "from-indigo-400 to-sky-400" },
  {
    label: "Opportunity Value",
    value: 90,
    color: "from-emerald-400 to-cyan-400",
  },
  {
    label: "Evidence Confidence",
    value: 85,
    color: "from-violet-400 to-indigo-400",
  },
  { label: "Serviceability", value: 90, color: "from-sky-400 to-blue-400" },
];

export function LeadScoring() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section
      id="lead-scoring"
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Lead Scoring — Prioritization"
    >
      <div className="max-w-4xl mx-auto px-6 lg:px-8 space-y-14">
        {/* Header */}
        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15%" }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="PRIORITIZATION" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Not All Leads Are Equal.{" "}
            <GradientText>We Score Every One.</GradientText>
          </h2>
          <p className="text-base text-text-secondary font-body max-w-2xl mx-auto leading-relaxed">
            Every lead is automatically scored across five dimensions so your
            team works the highest-value opportunities first.
          </p>
        </motion.div>

        {/* Score bars */}
        <div
          ref={ref}
          className="glass-level-2 p-8 md:p-10 rounded-3xl space-y-8"
        >
          {SCORES.map((score, i) => (
            <div key={score.label} className="space-y-2.5">
              <div className="flex items-center justify-between text-sm font-mono">
                <span className="text-slate-200 font-semibold">
                  {score.label}
                </span>
                <span className="text-sky-400 font-bold">{score.value}%</span>
              </div>
              <div className="h-2.5 rounded-full bg-white/8 overflow-hidden">
                <motion.div
                  className={`h-full rounded-full bg-gradient-to-r ${score.color} shadow-[0_0_10px_rgba(56,189,248,0.4)]`}
                  initial={{ width: "0%" }}
                  animate={
                    isInView ? { width: `${score.value}%` } : { width: "0%" }
                  }
                  transition={{
                    duration: 1.0,
                    delay: i * 0.15,
                    ease: [0.34, 1.56, 0.64, 1],
                  }}
                />
              </div>
            </div>
          ))}

          {/* Priority badge */}
          <div className="pt-4 border-t border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-emerald-500/15 border border-emerald-400/40">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-sm font-mono font-bold text-emerald-400 tracking-wider">
                PRIORITY: HIGH
              </span>
            </div>
            <p className="text-xs font-body text-slate-500 max-w-sm leading-relaxed">
              Scores are evidence-based — derived from what the agents actually
              found, not assumptions.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
