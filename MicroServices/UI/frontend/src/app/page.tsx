'use client'

import {
  Navbar,
  Hero,
  ProblemSection,
  HorizontalPipeline,
  PinnedHorizontalPillars,
  WebDatabase,
  Pipeline,
  LeadDiscovery,
  ParallelResearch,
  SelfHealingDemo,
  SelfHealingCI,
  StructuredData,
  SalesAutomation,
  LeadScoring,
  Monitoring,
  ScraperControlCenter,
  Architecture,
  TechStackSection,
  WhyScrapeVerse,
  FinalCTA,
  Footer,
} from '@/components/sections'
import { CustomCursor } from '@/components/ui'
import { SmoothScrollProvider } from '@/components/providers'
import { useEffect, useState } from 'react'

function ScrollProgressBar() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) return

    let rafId = 0

    const updateProgress = () => {
      const scrollTop = window.scrollY
      const docHeight = document.body.scrollHeight - window.innerHeight
      const next = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      setProgress(Math.min(Math.max(next, 0), 100))
    }

    const handleScroll = () => {
      cancelAnimationFrame(rafId)
      rafId = requestAnimationFrame(updateProgress)
    }

    updateProgress()
    window.addEventListener('scroll', handleScroll, { passive: true })
    window.addEventListener('resize', handleScroll, { passive: true })

    return () => {
      cancelAnimationFrame(rafId)
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('resize', handleScroll)
    }
  }, [])

  return (
    <div className="fixed inset-x-0 top-0 z-[9999] h-[3px] w-full bg-transparent">
      <div
        id="scroll-progress-bar"
        className="h-full bg-gradient-to-r from-sky-400 via-cyan-300 to-indigo-400 shadow-[0_0_18px_rgba(56,189,248,0.8)] transition-[width] duration-150 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}

export default function Home() {
  return (
    <SmoothScrollProvider>
      <ScrollProgressBar />
      <div className="relative min-h-screen bg-[#07090D] text-text-primary selection:bg-sky-400 selection:text-[#07090D] font-body overflow-x-hidden">
        {/* Custom Lagging Magnetic Cursor */}
        <CustomCursor />

        {/* 1. Single Unified Full-Viewport Cold Twilight Background Image */}
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat filter brightness-110 saturate-[1.2]"
            style={{
              backgroundImage: "url('/images/custom_bg.jpeg')",
            }}
          />
          {/* Subtle translucent dark overlay for contrast */}
          <div className="absolute inset-0 bg-[#060911]/30 backdrop-blur-[1px]" />
        </div>

        {/* 2. Pixel-Perfect SVG Margin Mask Overlay (Seamlessly overlays identical full-screen background in outer margins so scrolling content cannot appear outside the frame) */}
        <svg
          className="fixed inset-0 w-full h-full z-30 pointer-events-none max-w-[1780px] mx-auto"
          preserveAspectRatio="none"
        >
          <defs>
            <filter id="glass-filter" x="-20%" y="-20%" width="140%" height="140%">
              <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" result="noise" />
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="3" xChannelSelector="R" yChannelSelector="G" />
            </filter>
            <mask id="frame-margin-mask">
              {/* Cover everywhere with white (reveals background in margins) */}
              <rect width="100%" height="100%" fill="white" />
              {/* Cut out the inner frame area with black (lets website content show inside the glass frame) */}
              <rect
                x="1.5rem"
                y="1.5rem"
                width="calc(100% - 3rem)"
                height="calc(100% - 3rem)"
                rx="2.5rem"
                ry="2.5rem"
                fill="black"
              />
            </mask>
          </defs>
          {/* Pixel-perfect synchronized full-viewport background image rendered ONLY in the margins */}
          <image
            href="/images/custom_bg.jpeg"
            width="100%"
            height="100%"
            preserveAspectRatio="xMidYMid slice"
            mask="url(#frame-margin-mask)"
            filter="brightness(1.1) saturate(1.2)"
          />
          <rect
            width="100%"
            height="100%"
            fill="#060911"
            opacity="0.3"
            mask="url(#frame-margin-mask)"
          />
        </svg>

        {/* 3. THE SINGLE FIXED FLOATING GLASS VIEWPORT FRAME (Always visible on screen with top & bottom rounded glass borders) */}
        <div
          className="fixed inset-3 sm:inset-5 lg:inset-6 z-40 pointer-events-none rounded-[2.5rem] border border-white/35 shadow-2xl max-w-[1780px] mx-auto"
          style={{
            boxShadow:
              '0 30px 100px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.15), inset 0 1.5px 2px rgba(255, 255, 255, 0.55), inset 0 -1.5px 2px rgba(255, 255, 255, 0.35)',
          }}
        >
          {/* Top Glass Specular Shine Accent */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />
          {/* Bottom Glass Specular Shine Accent */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/50 to-transparent pointer-events-none" />
        </div>

        {/* 4. Fixed Navbar at top inside frame */}
        <Navbar />

        {/* 5. Smooth Scrollable Content Track (Flows naturally within the frame window) */}
        <div className="relative z-10 w-full max-w-[1780px] mx-auto px-4 sm:px-8 lg:px-12 pt-3 pb-16">
          <main className="w-full">
            {/* §1 Hero with Horizontal Text Scramble + Particle Collapse */}
            <div data-scroll-reveal className="reveal-panel">
              <Hero />
            </div>

            {/* §2 The Problem — Two-Column Comparison */}
            <div data-scroll-reveal className="reveal-panel">
              <ProblemSection />
            </div>

            {/* §3 Horizontal Scroll Pipeline Overview */}
            <div data-scroll-reveal className="reveal-panel">
              <HorizontalPipeline />
            </div>

            {/* §4 Core Pillars Continuous Stream */}
            <div data-scroll-reveal className="reveal-panel">
              <PinnedHorizontalPillars />
            </div>

            {/* Web Database Showcase */}
            <div data-scroll-reveal className="reveal-panel">
              <WebDatabase />
            </div>

            {/* Pipeline Architecture (Continuous Upward Stream) */}
            <div data-scroll-reveal className="reveal-panel">
              <Pipeline />
            </div>


            {/* Lead Discovery Console */}
            <div data-scroll-reveal className="reveal-panel">
              <LeadDiscovery />
            </div>

            {/* Parallel Research Fleet */}
            <div data-scroll-reveal className="reveal-panel">
              <ParallelResearch />
            </div>



            {/* Interactive Self-Healing Demo */}
            <div data-scroll-reveal className="reveal-panel">
              <SelfHealingDemo />
            </div>

            {/* Self-Healing CI Logic */}
            <div data-scroll-reveal className="reveal-panel">
              <SelfHealingCI />
            </div>

            {/* Structured Data Extraction */}
            <div data-scroll-reveal className="reveal-panel">
              <StructuredData />
            </div>

            {/* Sales Automation */}
            <div data-scroll-reveal className="reveal-panel">
              <SalesAutomation />
            </div>

            {/* §7 Lead Scoring */}
            <div data-scroll-reveal className="reveal-panel">
              <LeadScoring />
            </div>

            {/* §8 Counter / Stats with Animated SVG Progress Rings */}
            <div data-scroll-reveal className="reveal-panel">
              <Monitoring />
            </div>

            {/* Scraper Control Center */}
            <div data-scroll-reveal className="reveal-panel">
              <ScraperControlCenter />
            </div>

            {/* Architecture Overview */}
            <div data-scroll-reveal className="reveal-panel">
              <Architecture />
            </div>

            {/* Tech Stack Section */}
            <div data-scroll-reveal className="reveal-panel">
              <TechStackSection />
            </div>

            {/* §9 Kinetic Typography Manifesto (Word-by-word reveal) */}
            <div data-scroll-reveal className="reveal-panel">
              <WhyScrapeVerse />
            </div>

            {/* §7 Footer Parallax + Magnetic Conic-Gradient CTA Button */}
            <div data-scroll-reveal className="reveal-panel">
              <FinalCTA />
            </div>
          </main>

          {/* Footer */}
          <Footer />
        </div>
      </div>
    </SmoothScrollProvider>
  )
}
