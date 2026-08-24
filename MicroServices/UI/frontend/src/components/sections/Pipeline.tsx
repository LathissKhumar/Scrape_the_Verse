"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Search, Zap, ShieldCheck, BrainCircuit, Rocket } from "lucide-react";
import { GradientText } from "@/components/ui/GradientText";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { PIPELINE_STAGES } from "@/lib/mock-data";

const STAGE_ICONS: Record<string, React.ReactNode> = {
  search: <Search className="w-5 h-5 text-sky-400" />,
  zap: <Zap className="w-5 h-5 text-indigo-400" />,
  "shield-check": <ShieldCheck className="w-5 h-5 text-emerald-400" />,
  "brain-circuit": <BrainCircuit className="w-5 h-5 text-sky-400" />,
  rocket: <Rocket className="w-5 h-5 text-indigo-400" />,
};

export function Pipeline() {
  const sectionRef = useRef<HTMLElement>(null);
  const lineSvgRef = useRef<SVGSVGElement>(null);
  const linePathRef = useRef<SVGLineElement>(null);
  const pulseDotRef = useRef<HTMLDivElement>(null);
  const stagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Register GSAP Plugins
    gsap.registerPlugin(ScrollTrigger);

    const section = sectionRef.current;
    const linePath = linePathRef.current;
    const pulseDot = pulseDotRef.current;
    const container = stagesContainerRef.current;

    if (!section || !linePath || !pulseDot || !container) return;

    // Create GSAP Context for safe cleanup
    const ctx = gsap.context(() => {
      // ─────────────────────────────────────────────────────────────
      // 1. TIMELINE LINE ANIMATION (SVG stroke-dashoffset + Pulse Dot)
      // ─────────────────────────────────────────────────────────────
      // Use exact container offsetHeight so strokeDasharray covers the entire 7-agent timeline height
      const pathLength = container.offsetHeight || 3500;

      // Initialize main vertical line
      gsap.set(linePath, {
        strokeDasharray: pathLength,
        strokeDashoffset: pathLength,
      });

      // Initialize pulse dot at start
      gsap.set(pulseDot, {
        y: 0,
        opacity: 0,
        scale: 0,
      });

      // Animate line drawing & moving pulse dot tied to scroll
      ScrollTrigger.create({
        trigger: container,
        start: "top 70%",
        end: "bottom 80%",
        scrub: 0.5,
        onUpdate: (self) => {
          const progress = self.progress;
          const currentLength = container.offsetHeight || pathLength;
          // Animate stroke-dashoffset from currentLength down to 0
          gsap.to(linePath, {
            strokeDashoffset: currentLength * (1 - progress),
            duration: 0.1,
            overwrite: "auto",
          });

          // Animate pulse dot down the vertical line
          const currentY = progress * currentLength;
          gsap.to(pulseDot, {
            y: currentY,
            opacity: progress > 0.01 && progress < 0.99 ? 1 : 0,
            scale: progress > 0.01 && progress < 0.99 ? 1 : 0,
            duration: 0.1,
            overwrite: "auto",
          });
        },
      });

      // ─────────────────────────────────────────────────────────────
      // 2. STAGE NODES & ALTERNATING CARDS SCROLLTRIGGERS
      // ─────────────────────────────────────────────────────────────
      const stageRows = container.querySelectorAll<HTMLElement>(
        ".timeline-stage-row",
      );

      stageRows.forEach((row, idx) => {
        const isEven = idx % 2 === 0;
        const node = row.querySelector<HTMLElement>(".timeline-node");
        const nodeIcon = row.querySelector<HTMLElement>(".node-icon");
        const card = row.querySelector<HTMLElement>(".timeline-card");
        const connector = row.querySelector<SVGLineElement>(
          ".timeline-connector-line",
        );
        const subAgents = row.querySelectorAll<HTMLElement>(".sub-agent-item");
        const compatibleBox = row.querySelector<HTMLElement>(".compatible-box");
        const producesBox = row.querySelector<HTMLElement>(".produces-box");
        const activeChars = row.querySelectorAll<HTMLElement>(".active-char");
        const readyLabel = row.querySelector<HTMLElement>(".ready-label");
        const stageHeading = row.querySelector<HTMLElement>(".stage-heading");
        const stageTitle = row.querySelector<HTMLElement>(".card-title");

        // ── Performance: initialize starting transforms ──
        if (node) {
          gsap.set(node, {
            scale: 0,
            opacity: 0,
            rotation: -180,
            willChange: "transform, opacity",
          });
        }

        if (card) {
          gsap.set(card, {
            x: isEven ? -80 : 80,
            opacity: 0,
            rotateY: isEven ? 15 : -15,
            transformPerspective: 1000,
            willChange: "transform, opacity",
          });
        }

        if (connector) {
          const connLength = connector.getTotalLength() || 60;
          gsap.set(connector, {
            strokeDasharray: connLength,
            strokeDashoffset: isEven ? connLength : -connLength,
          });
        }

        if (subAgents.length) {
          gsap.set(subAgents, { x: -15, opacity: 0 });
        }

        if (compatibleBox) {
          gsap.set(compatibleBox, { y: 10, opacity: 0 });
        }

        if (producesBox) {
          gsap.set(producesBox, { scale: 0.95, opacity: 0 });
        }

        if (activeChars.length) {
          gsap.set(activeChars, { opacity: 0 });
        }

        if (readyLabel) {
          gsap.set(readyLabel, { x: 20, opacity: 0 });
        }

        if (stageHeading && stageTitle) {
          gsap.set([stageHeading, stageTitle], { y: 20, opacity: 0 });
        }

        // ── Timeline reveal for this stage (Node → Connector → Card → Micro-animations) ──
        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: row,
            start: "top 78%",
            toggleActions: "play none none none",
          },
        });

        // 1. Node Circle Overshoot Bounce Entrance
        if (node) {
          tl.to(node, {
            scale: 1,
            opacity: 1,
            rotation: 0,
            duration: 0.6,
            ease: "back.out(1.7)",
            onComplete: () => {
              node.classList.add("timeline-node-active");
            },
          });
        }

        // 2. Node Icon 360deg Rotation
        if (nodeIcon) {
          tl.to(
            nodeIcon,
            {
              rotation: 360,
              duration: 0.4,
              ease: "power2.out",
            },
            "-=0.4",
          );
        }

        // 3. Horizontal Connector Line Draw
        if (connector) {
          tl.to(
            connector,
            {
              strokeDashoffset: 0,
              duration: 0.35,
              ease: "power2.out",
            },
            "-=0.2",
          );
        }

        // 4. Alternating Liquid Glass Card Entry
        if (card) {
          tl.to(
            card,
            {
              x: 0,
              opacity: 1,
              rotateY: 0,
              duration: 0.8,
              ease: "expo.out",
            },
            "-=0.15",
          );

          // 5. Card Border Glow Flash
          tl.to(
            card,
            {
              boxShadow:
                "0 0 30px rgba(0, 212, 255, 0.8), inset 0 1.5px 2px rgba(255, 255, 255, 0.6)",
              duration: 0.3,
              ease: "power2.out",
            },
            "-=0.6",
          ).to(card, {
            boxShadow:
              "0 15px 35px rgba(0, 0, 0, 0.35), inset 0 1px 1.5px rgba(255, 255, 255, 0.45)",
            duration: 0.4,
            ease: "power2.inOut",
          });
        }

        // 6. Card Interior: Stage Number and Title Slide-Up
        if (stageHeading && stageTitle) {
          tl.to(
            [stageHeading, stageTitle],
            {
              y: 0,
              opacity: 1,
              duration: 0.5,
              stagger: 0.1,
              ease: "power2.out",
            },
            "-=0.4",
          );
        }

        // 7. Sub-agent chips stagger entrance
        if (subAgents.length) {
          tl.to(
            subAgents,
            {
              x: 0,
              opacity: 1,
              duration: 0.35,
              stagger: 0.07,
              ease: "power2.out",
            },
            "-=0.3",
          );
        }

        // 8. Compatible tools box entrance
        if (compatibleBox) {
          tl.to(
            compatibleBox,
            {
              y: 0,
              opacity: 1,
              duration: 0.3,
              ease: "power2.out",
            },
            "-=0.2",
          );
        }

        // 9. Produces output box entrance
        if (producesBox) {
          tl.to(
            producesBox,
            {
              scale: 1,
              opacity: 1,
              duration: 0.4,
              ease: "back.out(1.5)",
            },
            "-=0.2",
          );
        }

        // 10. Card Interior: "ACTIVE PIPELINE NODE" Letter Stagger
        if (activeChars.length) {
          tl.to(
            activeChars,
            {
              opacity: 1,
              duration: 0.05,
              stagger: 0.03,
              ease: "power1.out",
            },
            "-=0.2",
          );
        }

        // 11. Card Interior: "READY →" Slide-in
        if (readyLabel) {
          tl.to(
            readyLabel,
            {
              x: 0,
              opacity: 1,
              duration: 0.4,
              ease: "power2.out",
            },
            "+=0.1",
          );
        }
      });

      // Sync trigger points
      setTimeout(() => {
        ScrollTrigger.refresh();
      }, 300);
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="pipeline"
      ref={sectionRef}
      className="py-10 md:py-14 relative border-b border-white/5 bg-transparent font-body overflow-hidden"
      aria-label="Vertical 5-Stage Pipeline Timeline"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20 space-y-3">
          <SectionLabel label="THE PIPELINE" />
          <h2 className="text-3xl md:text-5xl font-bold font-display tracking-tight text-text-primary">
            Meet the Agents <GradientText>Behind the Automation</GradientText>
          </h2>
          <p className="text-sm sm:text-base text-text-secondary max-w-2xl mx-auto font-body leading-relaxed">
            Scrape-Verse is not one AI — it is a pipeline of specialized agents,
            each with a defined role, working in sequence to convert a raw
            business listing into a complete, evidence-backed sales opportunity.
          </p>
        </div>

        {/* Vertical Pipeline Timeline Container */}
        <div
          ref={stagesContainerRef}
          className="relative max-w-5xl mx-auto py-10"
        >
          {/* 1. Main Vertical Center Line (SVG with Glow Filter) */}
          <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-8 -translate-x-1/2 z-0 pointer-events-none">
            <svg
              ref={lineSvgRef}
              className="w-full h-full"
              style={{ filter: "drop-shadow(0 0 6px #00d4ff)" }}
            >
              {/* Background Ambient Line Track — Always visible connecting all agent nodes */}
              <line
                x1="50%"
                y1="0%"
                x2="50%"
                y2="100%"
                stroke="rgba(0, 212, 255, 0.3)"
                strokeWidth="2"
                strokeLinecap="round"
              />
              {/* Active Scroll-Driven Progress Line */}
              <line
                ref={linePathRef}
                x1="50%"
                y1="0%"
                x2="50%"
                y2="100%"
                stroke="#00d4ff"
                strokeWidth="3"
                strokeLinecap="round"
                className="timeline-line"
              />
            </svg>
          </div>

          {/* 2. Moving Cyan Pulse Dot (Travels down in sync with scroll) */}
          <div
            ref={pulseDotRef}
            className="hidden lg:block absolute left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-[#00d4ff] z-20 pointer-events-none timeline-pulse-dot"
            style={{
              top: 0,
              boxShadow: "0 0 12px #00d4ff",
            }}
          />

          {/* 3. Seven Vertical Timeline Agent Stages (Alternating Left & Right) */}
          <div className="flex flex-col gap-16 lg:gap-24 relative z-10">
            {PIPELINE_STAGES.map((stage, idx) => {
              const isEven = idx % 2 === 0;
              const activeNodeText = "ACTIVE PIPELINE NODE";

              return (
                <div
                  key={stage.stage}
                  className={`timeline-stage-row flex flex-col lg:flex-row items-center gap-6 lg:gap-0 ${
                    isEven ? "lg:flex-row" : "lg:flex-row-reverse"
                  } relative w-full`}
                  style={{ perspective: "1000px" }}
                >
                  {/* Stage Liquid Glass Card (Left on even, Right on odd) */}
                  <div
                    className={`flex-1 w-full ${
                      isEven
                        ? "lg:pr-14 lg:text-right"
                        : "lg:pl-14 lg:text-left"
                    }`}
                  >
                    <div
                      className={`timeline-card ${
                        isEven ? "card-left" : "card-right"
                      } glass-liquid p-6 sm:p-7 inline-block w-full max-w-lg text-left space-y-3.5 rounded-2xl border border-white/30 hover:border-sky-400/80 shadow-2xl backdrop-blur-2xl transition-all duration-300 group relative overflow-hidden`}
                      style={{
                        boxShadow:
                          "0 15px 35px rgba(0, 0, 0, 0.35), inset 0 1px 1.5px rgba(255, 255, 255, 0.45)",
                      }}
                      data-cursor-hover
                    >
                      {/* Top Specular Shine Accent */}
                      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

                      {/* Header Badge */}
                      <div className="stage-heading flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="stage-label text-xs font-mono font-bold tracking-widest text-sky-400 flex items-center gap-1.5">
                            <span className="timeline-bullet-active w-2 h-2 rounded-full bg-sky-400" />
                            Agent {stage.stage}
                          </span>
                          <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border border-sky-400/30 bg-sky-500/10 text-sky-300">
                            {stage.roleBadge}
                          </span>
                        </div>
                        <span className="lg:hidden p-1.5 rounded-lg bg-white/10">
                          {STAGE_ICONS[stage.icon]}
                        </span>
                      </div>

                      {/* Title & Subtitle */}
                      <div>
                        <h3 className="card-title text-xl sm:text-2xl font-bold font-display text-text-primary group-hover:text-sky-300 transition-colors">
                          {stage.title}
                        </h3>
                        {stage.subtitle && (
                          <p className="text-xs font-mono text-cyan-300 font-semibold mt-0.5">
                            {stage.subtitle}
                          </p>
                        )}
                      </div>

                      {/* Description */}
                      <p className="card-description text-xs sm:text-sm font-body leading-relaxed text-slate-200/90">
                        {stage.description}
                      </p>

                      {/* Nested Sub-agents Chips (if present) */}
                      {stage.subAgents && stage.subAgents.length > 0 && (
                        <div className="space-y-1.5 pt-1">
                          <span className="text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
                            Sub-agents:
                          </span>
                          <div className="flex flex-col gap-1">
                            {stage.subAgents.map((sub, sIdx) => (
                              <div
                                key={sIdx}
                                className="text-[11px] font-body bg-white/5 border border-white/10 rounded-lg p-1.5 text-slate-300 flex items-start gap-1.5"
                              >
                                <span className="text-sky-400 font-mono">
                                  →
                                </span>
                                <div>
                                  <strong className="text-white font-semibold">
                                    {sub.name}
                                  </strong>{" "}
                                  — {sub.desc}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Compatible With list (if present) */}
                      {stage.compatibleWith && (
                        <div className="text-[11px] font-mono bg-white/5 border border-sky-400/20 rounded-lg p-2 text-cyan-300">
                          <span className="text-slate-400">
                            Compatible with:{" "}
                          </span>
                          <span className="font-semibold">
                            {stage.compatibleWith}
                          </span>
                        </div>
                      )}

                      {/* Output Section */}
                      <div className="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-[11px] font-mono space-y-0.5">
                        <span className="text-emerald-400 font-bold tracking-wider uppercase block">
                          Produces →
                        </span>
                        <span className="text-slate-200 block font-sans">
                          {stage.output}
                        </span>
                      </div>

                      {/* Card Bottom Meta Bar with SplitText Stagger */}
                      <div className="pt-3 flex items-center justify-between text-[10px] font-mono border-t border-white/15">
                        <div className="active-label flex items-center gap-1 text-emerald-400 font-semibold">
                          <span className="timeline-bullet-active">●</span>
                          <span className="flex">
                            {activeNodeText.split("").map((char, charIdx) => (
                              <span
                                key={charIdx}
                                className="active-char inline-block"
                              >
                                {char === " " ? "\u00A0" : char}
                              </span>
                            ))}
                          </span>
                        </div>
                        <span className="ready-label text-sky-400 font-bold group-hover:translate-x-0.5 transition-transform">
                          READY &rarr;
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Horizontal SVG Connector Line (From Node to Card) */}
                  <div
                    className={`hidden lg:flex items-center w-14 h-4 pointer-events-none ${
                      isEven ? "justify-end" : "justify-start"
                    }`}
                  >
                    <svg
                      className="w-14 h-2 overflow-visible"
                      style={{ filter: "drop-shadow(0 0 5px #00d4ff)" }}
                    >
                      <line
                        x1={isEven ? "100%" : "0%"}
                        y1="50%"
                        x2={isEven ? "0%" : "100%"}
                        y2="50%"
                        stroke="#00d4ff"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        className="timeline-connector-line"
                      />
                    </svg>
                  </div>

                  {/* Circular Icon Node on Central Line */}
                  <div
                    className="timeline-node hidden lg:flex w-14 h-14 rounded-full border-2 border-sky-400 items-center justify-center text-xl shrink-0 z-20 shadow-lg shadow-sky-500/40 backdrop-blur-xl cursor-pointer bg-[#07090D]/80 hover:border-white transition-all relative group"
                    style={{
                      boxShadow:
                        "0 0 14px rgba(0, 212, 255, 0.5), inset 0 0 8px rgba(0, 212, 255, 0.4)",
                    }}
                    data-cursor-hover
                  >
                    <div className="node-icon">{STAGE_ICONS[stage.icon]}</div>
                  </div>

                  {/* Spacer for opposite column on desktop */}
                  <div className="flex-1 hidden lg:block" />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
