"use client";
import { motion } from "framer-motion";
import { useRef } from "react";
import { Play, RotateCcw, ShieldAlert, Cpu } from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { Button } from "@/components/ui/Button";
import { useSelfHealingSequence } from "@/hooks/useSelfHealingSequence";

const PHASE_COLORS = {
  idle: "#CBD5E1",
  running: "#60A5FA",
  failure: "#F43F5E",
  healing: "#38BDF8",
  recovered: "#34D399",
};

const PHASE_LABELS = {
  idle: "READY",
  running: "SCRAPING TARGET SITE",
  failure: "STRUCTURE CHANGED — COLLECTOR FAILED",
  healing: "SELF-HEALING AGENT ACTIVATED…",
  recovered: "COLLECTOR RECOVERED ✓",
};

const EVENT_COLORS: Record<string, string> = {
  info: "#E2E8F0",
  warning: "#F59E0B",
  error: "#F43F5E",
  healing: "#38BDF8",
  success: "#34D399",
};

export function SelfHealingDemo() {
  const ref = useRef(null);
  const { phase, eventLog, start, reset } = useSelfHealingSequence();

  const phaseColor = PHASE_COLORS[phase];

  return (
    <section
      id="self-healing"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Self-Healing Engine"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header - Scale from Depth */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, scale: 0.92, y: 30 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="03" label="Self-Healing Engine" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            The web changes.{" "}
            <GradientText gradient="signature">
              Your scraper shouldn&apos;t stop.
            </GradientText>
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            When target sites change their DOM layout or CSS selectors,
            Scrape-Verse detects structural failure and automatically generates
            new extraction rules.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center max-w-6xl mx-auto">
          {/* Left Explanation - Slide in from Left */}
          <motion.div
            className="lg:col-span-5 space-y-6"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-level-2 p-6 space-y-4">
              <h3 className="text-xl font-bold font-display text-text-primary flex items-center gap-2">
                <Cpu className="w-5 h-5 text-sky-400" />
                <span>Automated DOM Repair Workflow</span>
              </h3>
              <div className="space-y-3 font-mono text-xs">
                {[
                  {
                    step: "1. Change Detection",
                    desc: "Monitors DOM tree variations and selector matches.",
                  },
                  {
                    step: "2. Deconstruction",
                    desc: "Isolates broken extraction paths from raw payload.",
                  },
                  {
                    step: "3. LLM Re-Analysis",
                    desc: "Gemini re-evaluates page layout to locate fields.",
                  },
                  {
                    step: "4. Validation & Recovery",
                    desc: "Executes test extraction and updates rule schema.",
                  },
                ].map((item) => (
                  <div
                    key={item.step}
                    className="p-3 rounded-xl bg-white/10 border border-white/15 space-y-0.5"
                  >
                    <div className="font-bold text-sky-400">{item.step}</div>
                    <div className="text-slate-200">{item.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Right Interactive Glass Browser - Scale up from Depth */}
          <motion.div
            className="lg:col-span-7 space-y-6"
            initial={{ opacity: 0, scale: 0.94, y: 40 }}
            whileInView={{ opacity: 1, scale: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div
              className={`glass-level-3 overflow-hidden transition-all duration-500 ${
                phase === "failure"
                  ? "border-rose-error/40 shadow-rose-error/10"
                  : phase === "healing"
                    ? "border-sky-400/60 shadow-sky-500/15"
                    : "border-white/20"
              }`}
            >
              {/* Browser Window Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5 font-mono text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-error/60" />
                  <div className="w-3 h-3 rounded-full bg-amber-warning/60" />
                  <div className="w-3 h-3 rounded-full bg-emerald-success/60" />
                  <span className="text-slate-300 ml-3 hidden sm:inline">
                    https://target-site.com/listing/482
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: phaseColor }}
                  />
                  <span
                    className="font-bold tracking-wider"
                    style={{ color: phaseColor }}
                  >
                    {PHASE_LABELS[phase]}
                  </span>
                </div>
              </div>

              {/* Console Log Stream */}
              <div className="h-80 overflow-y-auto p-6 space-y-2.5 font-mono text-xs bg-white/10 backdrop-blur-md">
                {eventLog.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-slate-300 gap-2">
                    <ShieldAlert className="w-4 h-4 text-sky-400" />
                    <span>
                      Click &quot;Run Self-Healing Sequence&quot; to test layout
                      break…
                    </span>
                  </div>
                ) : (
                  eventLog.map((entry, i) => (
                    <motion.div
                      key={i}
                      className="flex items-start gap-4"
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <span className="text-muted shrink-0">{entry.time}</span>
                      <span
                        style={{
                          color: EVENT_COLORS[entry.type] ?? "#F5F7FA",
                          fontWeight:
                            entry.type === "healing" || entry.type === "success"
                              ? 600
                              : 400,
                        }}
                      >
                        {entry.message}
                      </span>
                    </motion.div>
                  ))
                )}
              </div>

              {/* Controls */}
              <div className="p-4 border-t border-white/10 bg-white/5 flex gap-4">
                <Button
                  id="run-healing-demo-btn"
                  variant={phase === "recovered" ? "ghost" : "primary"}
                  onClick={start}
                  className="flex-1 justify-center !py-3 shadow-lg flex items-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>
                    {phase === "idle"
                      ? "Run Self-Healing Sequence"
                      : phase === "recovered"
                        ? "Recovery Verified"
                        : "Executing Recovery Sequence…"}
                  </span>
                </Button>
                {phase !== "idle" && (
                  <Button
                    id="reset-healing-demo-btn"
                    variant="ghost"
                    onClick={reset}
                    className="!px-6 flex items-center gap-2"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset</span>
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
