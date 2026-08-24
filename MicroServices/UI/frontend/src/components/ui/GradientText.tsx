"use client";
import { type ReactNode } from "react";

type GradientVariant =
  "brand" | "signature" | "violet" | "blue" | "emerald" | "rose";

const GRADIENTS: Record<GradientVariant, string> = {
  brand: "linear-gradient(135deg, #38BDF8 0%, #60A5FA 50%, #818CF8 100%)",
  signature: "linear-gradient(135deg, #38BDF8 0%, #60A5FA 50%, #818CF8 100%)",
  violet: "linear-gradient(135deg, #818CF8 0%, #C084FC 100%)",
  blue: "linear-gradient(135deg, #38BDF8 0%, #60A5FA 100%)",
  emerald: "linear-gradient(135deg, #34D399 0%, #38BDF8 100%)",
  rose: "linear-gradient(135deg, #FB7185 0%, #38BDF8 100%)",
};

interface GradientTextProps {
  children: ReactNode;
  className?: string;
  gradient?: GradientVariant;
}

export function GradientText({
  children,
  className = "",
  gradient = "signature",
}: GradientTextProps) {
  return (
    <span
      className={`inline-block bg-clip-text text-transparent ${className}`}
      style={{ backgroundImage: GRADIENTS[gradient] }}
    >
      {children}
    </span>
  );
}
