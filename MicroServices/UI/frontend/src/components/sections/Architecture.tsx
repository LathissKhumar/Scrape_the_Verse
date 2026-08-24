"use client";

import { motion } from "framer-motion";
import { useRef } from "react";
import Link from "next/link";
import {
  Database,
  ShieldCheck,
  BrainCircuit,
  Rocket,
  ArrowUpRight,
} from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";

const ARCHITECTURE_LAYERS = [
  {
    layer: "Layer 3",
    title: "Gemini AI Intelligence",
    subtitle: "Structured Reasoning & Scoring",
    startAngle: 270, // Top (12 o'clock)
    route: "#pipeline",
    actionLabel: "Inspect Pipeline →",
    icon: <BrainCircuit className="w-5 h-5 text-emerald-400" />,
    description:
      "Normalizes unstructured web payloads into typed JSON objects, scores lead intent, and identifies high-margin redesign opportunities.",
    glow: "radial-gradient(ellipse at bottom left, rgba(52, 211, 153, 0.25) 0%, transparent 65%)",
  },
  {
    layer: "Layer 4",
    title: "Autonomous Sales Suite",
    subtitle: "Automated Outreach & Monitoring",
    startAngle: 0, // Right (3 o'clock)
    route: "/dashboard",
    actionLabel: "Launch Console →",
    icon: <Rocket className="w-5 h-5 text-cyan-400" />,
    description:
      "Generates custom mobile micro-sites, personalized outreach emails, voice call briefs, and real-time domain watch alerts.",
    glow: "radial-gradient(ellipse at bottom right, rgba(34, 211, 238, 0.25) 0%, transparent 65%)",
  },
  {
    layer: "Layer 1",
    title: "Bright Data Scraper Studio",
    subtitle: "Data Ingestion & Discovery Fleet",
    startAngle: 90, // Bottom (6 o'clock)
    route: "#scraper-control",
    actionLabel: "Explore Platform →",
    icon: <Database className="w-5 h-5 text-sky-400" />,
    description:
      "Manages proxy rotation, rate limits, and multi-source web collection across maps, directories, and business registries.",
    glow: "radial-gradient(ellipse at top left, rgba(56, 189, 248, 0.25) 0%, transparent 65%)",
  },
  {
    layer: "Layer 2",
    title: "Self-Healing CI Engine",
    subtitle: "Autonomous Rule Generation",
    startAngle: 180, // Left (9 o'clock)
    route: "#self-healing",
    actionLabel: "View Self-Healing →",
    icon: <ShieldCheck className="w-5 h-5 text-violet-400" />,
    description:
      "Monitors payload variations, detects broken CSS/DOM paths, and generates automated replacement extraction rules.",
    glow: "radial-gradient(ellipse at top right, rgba(139, 92, 246, 0.25) 0%, transparent 65%)",
  },
];

// Generates 36 smooth orbit coordinates so cards travel in circle with strictly ZERO tilt/slant
function getOrbitalPath(startAngleDeg: number, radiusPercent: number = 43) {
  const steps = 36;
  const lefts: string[] = [];
  const tops: string[] = [];
  for (let i = 0; i <= steps; i++) {
    const currentAngle = (startAngleDeg + (i / steps) * 360) * (Math.PI / 180);
    const x = 50 + radiusPercent * Math.cos(currentAngle);
    const y = 50 + radiusPercent * Math.sin(currentAngle);
    lefts.push(`${x.toFixed(2)}%`);
    tops.push(`${y.toFixed(2)}%`);
  }
  return { lefts, tops };
}

export function Architecture() {
  const ref = useRef(null);

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
          className="text-center mb-10 sm:mb-16 space-y-4 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 30, filter: "blur(10px)" }}
          whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <SectionLabel label="Enterprise Infrastructure" />
          <h2 className="text-3xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Modular. Resilient. <GradientText>Production-Ready.</GradientText>
          </h2>
          <p className="text-sm sm:text-base text-text-secondary max-w-xl mx-auto font-body">
            Four decoupled architecture layers rotating in an autonomous orbital
            system around the AgencyOS core.
          </p>
        </motion.div>

        {/* Circular Orbit Viewport */}
        <div className="relative w-full min-h-[820px] sm:min-h-[920px] md:min-h-[1000px] flex items-center justify-center my-4 py-8">
          {/* Static Center Project Logo */}
          <div className="absolute z-30 flex items-center justify-center pointer-events-none">
            <motion.div
              animate={{ scale: [1, 1.04, 1] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            >
              <img
                src="/images/Main_logo_vibrant.png"
                alt="AgencyOS Main Logo"
                className="w-36 sm:w-48 md:w-56 h-auto object-contain filter drop-shadow-[0_10px_35px_rgba(56,189,248,0.75)] saturate-[1.85] contrast-[1.15]"
              />
            </motion.div>
          </div>

          {/* Background Orbit Line Guide Rings */}
          <div className="relative w-[580px] h-[580px] sm:w-[720px] sm:h-[720px] md:w-[860px] md:h-[860px] flex items-center justify-center pointer-events-none">
            <motion.div
              className="absolute inset-4 sm:inset-6 md:inset-8 rounded-full border border-dashed border-sky-400/20"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 60, ease: "linear" }}
            />
            <div className="absolute inset-10 sm:inset-14 md:inset-16 rounded-full border border-white/20 shadow-[0_0_20px_rgba(56,189,248,0.15)] opacity-60" />
            <div className="absolute inset-20 sm:inset-28 rounded-full border border-white/10 opacity-30" />
          </div>

          {/* 4 Orbiting Cards — Moving in Circular Orbit while remaining 100% Vertically Straight */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div className="relative w-[580px] h-[580px] sm:w-[720px] sm:h-[720px] md:w-[860px] md:h-[860px] pointer-events-auto">
              {ARCHITECTURE_LAYERS.map((layer) => {
                const path = getOrbitalPath(layer.startAngle, 43);
                const isInternalLink = layer.route.startsWith("/");

                const CardBody = (
                  <motion.div
                    whileHover={{ scale: 1.06, y: -4 }}
                    transition={{ duration: 0.2 }}
                    className="w-52 sm:w-60 md:w-68 min-h-[250px] sm:min-h-[270px] p-5 sm:p-6 rounded-2xl flex flex-col justify-between glass-liquid border border-white/30 shadow-2xl backdrop-blur-2xl transition-all duration-300 group hover:border-sky-400/80 hover:shadow-sky-500/25 cursor-pointer overflow-hidden relative select-none"
                    style={{
                      boxShadow:
                        "0 20px 45px rgba(0, 0, 0, 0.45), inset 0 1px 2px rgba(255, 255, 255, 0.5)",
                      transform: "none", // Strictly 0deg rotation, vertically straight
                    }}
                  >
                    {/* Radial Glow */}
                    <div
                      className="absolute inset-0 pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ background: layer.glow }}
                    />
                    <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

                    {/* Top Header */}
                    <div className="relative z-10 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-sky-300/35 bg-sky-500/10 text-sky-100 backdrop-blur-md">
                          {layer.layer}
                        </span>
                        <div className="p-1.5 sm:p-2 rounded-xl bg-white/10 border border-white/20 shadow-md group-hover:border-sky-400/60 group-hover:bg-sky-500/20 transition-all shrink-0">
                          {layer.icon}
                        </div>
                      </div>

                      <h3 className="text-base sm:text-lg font-bold font-display text-white group-hover:text-sky-300 transition-colors leading-tight flex items-center justify-between">
                        <span>{layer.title}</span>
                        <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity text-sky-400 shrink-0 ml-1" />
                      </h3>
                      <div className="text-[10px] sm:text-xs font-mono text-cyan-300 font-semibold">
                        {layer.subtitle}
                      </div>
                    </div>

                    {/* Body Description */}
                    <p className="relative z-10 text-[11px] sm:text-xs font-body leading-relaxed text-slate-300/90 my-2 line-clamp-4">
                      {layer.description}
                    </p>

                    {/* Interactive Route Pill */}
                    <div className="relative z-10 mt-2 pt-2.5 border-t border-white/10 flex items-center justify-between text-[10px] sm:text-xs font-mono text-sky-300 font-semibold group-hover:text-white transition-colors">
                      <span>{layer.actionLabel}</span>
                    </div>
                  </motion.div>
                );

                return (
                  <motion.div
                    key={layer.layer}
                    className="absolute -translate-x-1/2 -translate-y-1/2 z-20"
                    animate={{
                      left: path.lefts,
                      top: path.tops,
                    }}
                    transition={{
                      duration: 40,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                    style={{
                      rotate: 0, // Guarantees zero tilt/slant at all times
                    }}
                  >
                    {isInternalLink ? (
                      <Link href={layer.route} className="block no-underline">
                        {CardBody}
                      </Link>
                    ) : (
                      <a href={layer.route} className="block no-underline">
                        {CardBody}
                      </a>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
