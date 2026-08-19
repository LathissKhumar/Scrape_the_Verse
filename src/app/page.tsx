'use client'
import { Navbar } from '@/components/sections/Navbar'
import { Hero } from '@/components/sections/Hero'
import { PinnedHorizontalPillars } from '@/components/sections/PinnedHorizontalPillars'
import { WebDatabase } from '@/components/sections/WebDatabase'
import { Pipeline } from '@/components/sections/Pipeline'
import { LeadDiscovery } from '@/components/sections/LeadDiscovery'
import { ParallelResearch } from '@/components/sections/ParallelResearch'
import { ImageDistortionSection } from '@/components/sections/ImageDistortionSection'
import { StaggeredGridReveal } from '@/components/sections/StaggeredGridReveal'
import { SelfHealingDemo } from '@/components/sections/SelfHealingDemo'
import { SelfHealingCI } from '@/components/sections/SelfHealingCI'
import { StructuredData } from '@/components/sections/StructuredData'
import { SalesAutomation } from '@/components/sections/SalesAutomation'
import { Monitoring } from '@/components/sections/Monitoring'
import { ScraperControlCenter } from '@/components/sections/ScraperControlCenter'
import { Architecture } from '@/components/sections/Architecture'
import { WhyScrapeVerse } from '@/components/sections/WhyScrapeVerse'
import { FinalCTA } from '@/components/sections/FinalCTA'
import { Footer } from '@/components/sections/Footer'
import { CustomCursor } from '@/components/ui/CustomCursor'
import { SmoothScrollProvider } from '@/components/providers/SmoothScrollProvider'

export default function Home() {
  return (
    <SmoothScrollProvider>
      <div className="relative min-h-screen bg-[#07090D] text-text-primary selection:bg-sky-400 selection:text-[#07090D] font-body overflow-x-hidden">
        {/* Custom Lagging Magnetic Cursor */}
        <CustomCursor />

        {/* 1. Single Unified Full-Viewport Cold Twilight Background Image */}
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat filter brightness-110 saturate-[1.2]"
            style={{
              backgroundImage: "url('/images/cold_theme_background.png')",
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
            href="/images/cold_theme_background.png"
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
            <Hero />

            {/* §2 Core Pillars Continuous Stream */}
            <PinnedHorizontalPillars />

            {/* Web Database Showcase */}
            <WebDatabase />

            {/* Pipeline Architecture (Continuous Upward Stream) */}
            <Pipeline />

            {/* §6 3x3 Staggered Grid with 3D Flip & Tilt */}
            <StaggeredGridReveal />

            {/* Lead Discovery Console */}
            <LeadDiscovery />

            {/* Parallel Research Fleet */}
            <ParallelResearch />

            {/* §5 Scroll-Driven Image Distortion (Clip-Path Circle -> Star -> Inset) */}
            <ImageDistortionSection />

            {/* Interactive Self-Healing Demo */}
            <SelfHealingDemo />

            {/* Self-Healing CI Logic */}
            <SelfHealingCI />

            {/* Structured Data Extraction */}
            <StructuredData />

            {/* Sales Automation */}
            <SalesAutomation />

            {/* §4 Counter / Stats with Animated SVG Progress Rings */}
            <Monitoring />

            {/* Scraper Control Center */}
            <ScraperControlCenter />

            {/* Architecture Overview */}
            <Architecture />

            {/* §3 Kinetic Typography Manifesto (Word-by-word reveal) */}
            <WhyScrapeVerse />

            {/* §7 Footer Parallax + Magnetic Conic-Gradient CTA Button */}
            <FinalCTA />
          </main>

          {/* Footer */}
          <Footer />
        </div>
      </div>
    </SmoothScrollProvider>
  )
}
