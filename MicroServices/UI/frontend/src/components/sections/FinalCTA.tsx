"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { useEffect, useRef } from "react";
import { ArrowRight, Calendar, Sparkles } from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import Link from "next/link";

export function FinalCTA() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const magneticWrapRef = useRef<HTMLDivElement>(null);
  const magneticBtnRef = useRef<HTMLButtonElement>(null);

  // 1. Parallax Scrolling Background Text at 0.3x speed
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });
  const parallaxY = useTransform(scrollYProgress, [0, 1], [-80, 80]);

  // 2. Magnetic CTA button with lerp cursor attraction within 80px radius
  useEffect(() => {
    const wrap = magneticWrapRef.current;
    const btn = magneticBtnRef.current;
    if (!wrap || !btn) return;

    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    let animId: number;
    const RADIUS = 85;

    const onMouseMove = (e: MouseEvent) => {
      const rect = wrap.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const dx = e.clientX - centerX;
      const dy = e.clientY - centerY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < RADIUS) {
        const pull = (RADIUS - distance) / RADIUS;
        targetX = dx * pull * 0.55;
        targetY = dy * pull * 0.55;
      } else {
        targetX = 0;
        targetY = 0;
      }
    };

    const render = () => {
      currentX += (targetX - currentX) * 0.12;
      currentY += (targetY - currentY) * 0.12;
      btn.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
      animId = requestAnimationFrame(render);
    };

    window.addEventListener("mousemove", onMouseMove, { passive: true });
    animId = requestAnimationFrame(render);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <section
      id="final-cta"
      ref={sectionRef}
      className="py-20 md:py-28 relative overflow-hidden bg-transparent border-b border-white/5 font-body"
      aria-label="Final Call to Action"
    >
      {/* Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-[radial-gradient(ellipse_at_center,rgba(56,189,248,0.18)_0%,transparent_70%)] pointer-events-none" />

      {/* Large Parallax Background Text */}
      <motion.div
        style={{ y: parallaxY }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 select-none pointer-events-none whitespace-nowrap z-0 will-change-transform opacity-30 text-center"
      >
        <span
          className="text-7xl sm:text-9xl md:text-[140px] font-black uppercase tracking-tighter"
          style={{
            WebkitTextStroke: "1.5px rgba(255, 255, 255, 0.15)",
            color: "transparent",
          }}
        >
          LET&apos;S BUILD
        </span>
      </motion.div>

      <div className="relative max-w-4xl mx-auto px-6 text-center z-10 space-y-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.88, y: 45 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-8"
        >
          <div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-sky-400/60 bg-white/15 text-xs font-mono font-bold text-white backdrop-blur-xl shadow-lg shadow-sky-500/20"
            data-cursor-hover
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span>BUILT FOR HACKATHON 2026</span>
          </div>

          <h2 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-display leading-[1.1] tracking-tight text-text-primary">
            We don&apos;t stop at finding leads.
            <br />
            <GradientText>
              We tell you what they need, what to sell, and what to build.
            </GradientText>
          </h2>

          <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto font-body leading-relaxed">
            AgencyOS is the AI-powered lead-to-opportunity engine for web and
            SEO agencies. Discover leads, audit sites, detect opportunities,
            generate specs, and close deals — automatically.
          </p>

          {/* Magnetic CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-4">
            {/* Magnetic Button Container */}
            <div ref={magneticWrapRef} className="relative inline-block">
              <Link href="/dashboard">
                <button
                  ref={magneticBtnRef}
                  id="final-cta-primary"
                  data-cursor-hover
                  className="relative inline-flex items-center gap-3 px-10 py-5 rounded-full font-display font-bold text-base text-white bg-[#07090D] shadow-2xl shadow-sky-500/30 transition-all duration-300 group cursor-pointer will-change-transform overflow-hidden"
                >
                  {/* Rotating Conic Gradient Border */}
                  <span
                    className="absolute -inset-[2px] rounded-full z-[-1] animate-spin"
                    style={{
                      background:
                        "conic-gradient(from 0deg, #38BDF8, #818CF8, #34D399, #38BDF8)",
                      animationDuration: "3.5s",
                    }}
                  />
                  {/* Button Inner Surface */}
                  <span className="absolute inset-[1.5px] rounded-full bg-[#0B0F19] z-[-1] backdrop-blur-md group-hover:bg-[#121B2A] transition-colors" />

                  <span className="relative z-10 tracking-wide">
                    Launch Command Center
                  </span>
                  <ArrowRight className="w-5 h-5 text-cyan-300 relative z-10 group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>
            </div>

            <Link href="/dashboard">
              <button
                id="final-cta-secondary"
                data-cursor-hover
                className="inline-flex items-center gap-2.5 px-8 py-4 rounded-full text-base font-semibold text-slate-200 bg-white/10 hover:bg-white/15 border border-white/25 hover:border-sky-400/50 backdrop-blur-xl shadow-xl transition-all cursor-pointer"
              >
                <Calendar className="w-4 h-4 text-sky-400" />
                <span>Explore Live Hubs</span>
              </button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
