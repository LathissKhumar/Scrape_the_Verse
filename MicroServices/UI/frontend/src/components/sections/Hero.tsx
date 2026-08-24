"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useScroll } from "framer-motion";
import { ArrowRight, Sparkles, Shield, Cpu, Zap, Layers } from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { Button } from "@/components/ui/Button";
import Link from "next/link";

const GLYPHS = "!<>-_\\/[]{}=+*^?#01~%";

export function Hero() {
  const [headingText, setHeadingText] = useState(
    "BRIGHT DATA × SELF-HEALING AI",
  );
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { scrollYProgress } = useScroll();

  // 1. Text Scramble Effect
  useEffect(() => {
    const target = "BRIGHT DATA × SELF-HEALING AI";
    let frame = 0;
    const totalFrames = 36;
    let animId: number;

    const timeout = setTimeout(() => {
      const tick = () => {
        const progress = frame / totalFrames;
        const result = target
          .split("")
          .map((char, idx) => {
            if (char === " ") return " ";
            if (idx < Math.floor(progress * target.length)) return char;
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          })
          .join("");

        setHeadingText(result);
        frame++;

        if (frame <= totalFrames) {
          animId = requestAnimationFrame(tick);
        } else {
          setHeadingText(target);
        }
      };
      tick();
    }, 300);

    return () => {
      clearTimeout(timeout);
      cancelAnimationFrame(animId);
    };
  }, []);

  // 2. Interactive Canvas Particles that collapse to center on scroll
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const NUM_PARTICLES = 50;
    const particles = Array.from({ length: NUM_PARTICLES }, () => {
      const x = Math.random() * window.innerWidth;
      const y = Math.random() * window.innerHeight;
      return {
        ox: x,
        oy: y,
        angle: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.35 + 0.15,
        size: Math.random() * 2.2 + 0.6,
        color:
          Math.random() > 0.5 ? "rgba(56, 189, 248," : "rgba(129, 140, 248,",
        alpha: Math.random() * 0.5 + 0.25,
      };
    });

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      const p = scrollYProgress.get();

      particles.forEach((pt) => {
        pt.angle += pt.speed * 0.015;
        const driftX = pt.ox + Math.cos(pt.angle) * 35;
        const driftY = pt.oy + Math.sin(pt.angle) * 35;

        const currentX = driftX + (cx - driftX) * p * p;
        const currentY = driftY + (cy - driftY) * p * p;
        const opacity = Math.max(0.05, pt.alpha * (1 - p * 0.8));
        const radius = Math.max(0.5, pt.size * (1 - p * 0.4));

        ctx.beginPath();
        ctx.arc(currentX, currentY, radius, 0, Math.PI * 2);
        ctx.fillStyle = `${pt.color}${opacity})`;
        ctx.fill();
      });

      animId = requestAnimationFrame(render);
    };
    render();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animId);
    };
  }, [scrollYProgress]);

  const subtitleWords =
    "Built specifically for freelance website builders and SEO analysts who want to close $3k–$10k client retainers without the manual grunt work. Powered by Bright Data Scraper Studio’s unblockable residential proxy fleet and our autonomous Self-Healing Scraping Engine that auto-repairs DOM mutations on the fly, AgencyOS discovers high-intent businesses, audits technical SEO bottlenecks, and generates instant v0, Bolt.new, and Lovable prompts while you just vibe.".split(
      " ",
    );

  return (
    <section
      id="hero"
      className="relative min-h-[88vh] flex items-center justify-center pt-28 pb-20 px-6 lg:px-12 overflow-hidden border-b border-white/10 bg-transparent font-body"
      aria-label="Hero — Autonomous Web Agency & SEO Intelligence"
    >
      {/* Background Interactive Canvas Particles with Scroll Implosion */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none z-0 opacity-60"
      />

      {/* Dynamic Ambient Background Glow */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] h-[720px] rounded-full pointer-events-none opacity-25 blur-[140px]"
        style={{
          background:
            "radial-gradient(circle, #38BDF8 0%, #818CF8 50%, transparent 75%)",
        }}
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.2, 0.35, 0.2],
        }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Hero Content — Clean Centered Layout */}
      <div className="relative z-10 max-w-5xl mx-auto text-center flex flex-col items-center justify-center space-y-6 w-full my-auto">
        <motion.div
          className="space-y-6 flex flex-col items-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="space-y-4 flex flex-col items-center">
            {/* Main Brand Logo */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mb-1"
            >
              <img
                src="/images/Main_logo_vibrant.png"
                alt="AgencyOS Main Logo"
                className="w-72 sm:w-[420px] md:w-[500px] lg:w-[560px] h-auto object-contain filter drop-shadow-[0_15px_40px_rgba(56,189,248,0.6)] saturate-[1.85] contrast-[1.15] transition-transform hover:scale-[1.03] duration-300"
              />
            </motion.div>

            {/* Bright Data & Self-Healing Badge */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-sky-400/30 bg-sky-500/10 text-xs font-mono tracking-[0.2em] text-cyan-300 uppercase font-bold backdrop-blur-md shadow-lg shadow-sky-500/10"
            >
              <Sparkles className="w-3.5 h-3.5 text-sky-400 animate-pulse" />
              <span>{headingText}</span>
            </motion.div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display leading-[1.14] tracking-tight text-text-primary max-w-4xl">
              Automate Your Entire Web Agency & SEO Pipeline{" "}
              <GradientText className="py-0.5">
                While You Just Vibe.
              </GradientText>
            </h1>
          </div>

          {/* Subtitle with staggered word entrance */}
          <div className="flex flex-wrap justify-center gap-x-1.5 gap-y-1 text-sm sm:text-base font-body leading-relaxed text-text-secondary max-w-3xl mx-auto">
            {subtitleWords.map((word, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.5,
                  delay: 0.3 + i * 0.02,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="inline-block"
              >
                {word}
              </motion.span>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3.5 pt-3">
            <Link href="/dashboard" className="no-underline">
              <Button
                id="hero-cta-primary"
                variant="primary"
                className="!text-sm !px-7 !py-3.5 shadow-xl shadow-sky-500/25 flex items-center gap-2 cursor-pointer"
                data-cursor-hover
              >
                <span>Launch Agency Console</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <a href="#self-healing" className="no-underline">
              <Button
                id="hero-cta-secondary"
                variant="secondary"
                className="!text-sm !px-7 !py-3.5 cursor-pointer"
                data-cursor-hover
              >
                Explore Self-Healing Engine →
              </Button>
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
