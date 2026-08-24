"use client";
import { motion } from "framer-motion";
import { useRef, useState } from "react";
import {
  Play,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Cpu,
} from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { Button } from "@/components/ui/Button";
import { CI_COLLECTORS } from "@/lib/mock-data";

export function SelfHealingCI() {
  const ref = useRef(null);
  const [ciState, setCiState] = useState<
    "idle" | "running" | "repairing" | "passed"
  >("idle");

  const handleRunCI = () => {
    setCiState("running");
    setTimeout(() => setCiState("repairing"), 1200);
    setTimeout(() => setCiState("passed"), 2600);
  };

  const handleResetCI = () => {
    setCiState("idle");
  };

  return (
    <section
      id="self-healing-ci"
      ref={ref}
      className="py-32 md:py-40 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Self-Healing CI"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-16 space-y-4"
          initial={{ opacity: 0, x: -60, filter: "blur(10px)" }}
          whileInView={{ opacity: 1, x: 0, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel stage="03b" label="Self-Healing CI Pipeline" />
          <h2 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            <GradientText>Continuous Scraping.</GradientText> Zero Downtime.
          </h2>
          <p className="text-base text-text-secondary max-w-xl mx-auto font-body">
            Automated test runner catches website schema changes during CI runs,
            triggers LLM repair agents, and resumes pipeline operations
            automatically.
          </p>
        </motion.div>

        {/* Console Container */}
        <motion.div
          className="max-w-3xl mx-auto space-y-6"
          initial={{ opacity: 0, x: -50, scale: 0.96 }}
          whileInView={{ opacity: 1, x: 0, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="glass-level-3 overflow-hidden border-white/20 shadow-2xl">
            {/* Header bar */}
            <div className="px-6 py-4 border-b border-white/10 bg-white/5 font-mono text-xs flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-4 h-4 text-violet-accent" />
                <span className="text-text-primary font-bold">
                  scrape-verse-ci-runner.yml
                </span>
              </div>
              <span className="text-muted">Branch: main</span>
            </div>

            {/* Test Run Log Stream */}
            <div className="p-6 space-y-3 font-mono text-xs bg-black/40">
              {CI_COLLECTORS.map((collector) => {
                const isFailing =
                  collector.status === "fail" && ciState !== "passed";
                const isRepaired =
                  collector.status === "fail" && ciState === "passed";

                return (
                  <div
                    key={collector.name}
                    className="flex items-center justify-between p-3.5 rounded-xl bg-white/5 border border-white/5"
                  >
                    <div className="flex items-center gap-3">
                      {isFailing ? (
                        <AlertTriangle className="w-4 h-4 text-rose-error animate-bounce" />
                      ) : isRepaired ? (
                        <Cpu className="w-4 h-4 text-violet-accent" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 text-emerald-success" />
                      )}
                      <span className="text-text-primary font-medium">
                        {collector.name}
                      </span>
                    </div>

                    <span
                      className={`px-3 py-1 rounded-full text-[11px] font-bold ${
                        isFailing
                          ? "bg-rose-error/20 text-rose-error border border-rose-error/30"
                          : isRepaired
                            ? "bg-violet-accent/20 text-violet-accent border border-violet-accent/30"
                            : "bg-emerald-success/20 text-emerald-success border border-emerald-success/30"
                      }`}
                    >
                      {isFailing
                        ? "DOM CHANGED"
                        : isRepaired
                          ? "AUTO-HEALED"
                          : "PASSED"}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Action footer */}
            <div className="p-4 border-t border-white/10 bg-white/5 flex gap-4">
              <Button
                id="run-ci-pipeline-btn"
                variant={ciState === "passed" ? "ghost" : "primary"}
                onClick={handleRunCI}
                className="flex-1 justify-center !py-3 shadow-lg flex items-center gap-2"
              >
                <Play className="w-3.5 h-3.5" />
                <span>
                  {ciState === "idle"
                    ? "Simulate CI Pipeline Run"
                    : ciState === "passed"
                      ? "CI Test Passed ✓"
                      : "Running CI Self-Healing…"}
                </span>
              </Button>

              {ciState !== "idle" && (
                <Button
                  id="reset-ci-pipeline-btn"
                  variant="ghost"
                  onClick={handleResetCI}
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
    </section>
  );
}
