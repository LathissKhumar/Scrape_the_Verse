'use client'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { useEffect, useState } from 'react'
import { Navbar } from '@/components/sections/Navbar'
import { Hero } from '@/components/sections/Hero'
import { WebDatabase } from '@/components/sections/WebDatabase'
import { Pipeline } from '@/components/sections/Pipeline'
import { LeadDiscovery } from '@/components/sections/LeadDiscovery'
import { ParallelResearch } from '@/components/sections/ParallelResearch'
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

export default function Home() {
  const { scrollYProgress } = useScroll()
  const smoothProgress = useSpring(scrollYProgress, { stiffness: 100, damping: 20 })
  const [percent, setPercent] = useState<number>(0)

  // Sync scroll percentage text
  useEffect(() => {
    return smoothProgress.on('change', (latest) => {
      setPercent(Math.round(latest * 100))
    })
  }, [smoothProgress])

  // Dynamic glass frame padding and radius based on scroll
  const framePadding = useTransform(smoothProgress, [0, 0.05, 0.95, 1], ['1.5rem', '0.5rem', '0.5rem', '1.5rem'])
  const frameRadius = useTransform(smoothProgress, [0, 0.05, 0.95, 1], ['2rem', '1rem', '1rem', '2rem'])

  return (
    <div className="relative min-h-screen bg-[#07090D] text-text-primary selection:bg-violet-accent selection:text-void font-body overflow-x-hidden">
      {/* 1. Fixed Crisp Background Image (Glowing Cabin in Foggy Forest) */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat filter brightness-110 saturate-[1.2]"
          style={{
            backgroundImage: "url('/images/foggy_cabin_background.jpg')",
          }}
        />
      </div>

      {/* 2. Floating Crystal-Clear Glass Container Frame */}
      <motion.div
        className="relative z-10 min-h-screen transition-all duration-300"
        style={{
          padding: framePadding,
        }}
      >
        <motion.div
          className="relative min-h-screen bg-[#07090D]/05 backdrop-blur-sm border border-white/30 shadow-2xl overflow-hidden transition-all duration-300"
          style={{
            borderRadius: frameRadius,
            boxShadow: '0 30px 100px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.4)',
          }}
        >
          {/* Top Glass Specular Shine */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent pointer-events-none z-50" />

          {/* All 16 Page Components */}
          <Navbar />
          <main>
            <Hero />
            <WebDatabase />
            <Pipeline />
            <LeadDiscovery />
            <ParallelResearch />
            <SelfHealingDemo />
            <SelfHealingCI />
            <StructuredData />
            <SalesAutomation />
            <Monitoring />
            <ScraperControlCenter />
            <Architecture />
            <WhyScrapeVerse />
            <FinalCTA />
          </main>
          <Footer />
        </motion.div>
      </motion.div>

      {/* 3. Floating Scroll Percentage Indicator */}
      <motion.div
        className="fixed bottom-6 left-8 z-50 pointer-events-none hidden sm:block"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="glass-level-3 px-5 py-2.5 rounded-full border border-white/35 shadow-2xl flex items-center gap-3 backdrop-blur-2xl bg-[#07090D]/60">
          <span className="w-2 h-2 rounded-full bg-violet-accent animate-pulse" />
          <span className="font-mono text-2xl font-bold tracking-tight text-text-primary tabular-nums" suppressHydrationWarning>
            {percent}%
          </span>
        </div>
      </motion.div>
    </div>
  )
}
