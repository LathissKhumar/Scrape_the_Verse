"use client";
import { motion } from "framer-motion";

type BadgeVariant = "healthy" | "running" | "healing" | "failed" | "info";

const STYLES: Record<
  BadgeVariant,
  { dot: string; text: string; bg: string; border: string }
> = {
  healthy: {
    dot: "#34D399",
    text: "#34D399",
    bg: "rgba(52, 211, 153, 0.08)",
    border: "rgba(52, 211, 153, 0.25)",
  },
  running: {
    dot: "#38BDF8",
    text: "#38BDF8",
    bg: "rgba(56, 189, 248, 0.08)",
    border: "rgba(56, 189, 248, 0.25)",
  },
  healing: {
    dot: "#8B5CF6",
    text: "#8B5CF6",
    bg: "rgba(139, 92, 246, 0.08)",
    border: "rgba(139, 92, 246, 0.25)",
  },
  failed: {
    dot: "#FB7185",
    text: "#FB7185",
    bg: "rgba(251, 113, 133, 0.08)",
    border: "rgba(251, 113, 133, 0.25)",
  },
  info: {
    dot: "#A7AFBD",
    text: "#A7AFBD",
    bg: "rgba(167, 175, 189, 0.08)",
    border: "rgba(167, 175, 189, 0.25)",
  },
};

export function NeonBadge({
  label,
  variant = "info",
}: {
  label: string;
  variant?: BadgeVariant;
}) {
  const s = STYLES[variant];
  return (
    <span
      className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-mono font-medium border backdrop-blur-md"
      style={{ color: s.text, backgroundColor: s.bg, borderColor: s.border }}
    >
      <motion.span
        className="w-1.5 h-1.5 rounded-full shrink-0"
        style={{ backgroundColor: s.dot }}
        animate={{ opacity: [1, 0.4, 1] }}
        transition={{ duration: 1.8, repeat: Infinity }}
      />
      {label}
    </span>
  );
}
