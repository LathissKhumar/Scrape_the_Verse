'use client'
import { motion } from 'framer-motion'
import { Star, ArrowRight, Sparkles, ShieldCheck } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'
import { WebCanvas } from '@/components/ui/WebCanvas'
import { BUSINESS_INTEL_EXAMPLE } from '@/lib/mock-data'

const HERO_NODES = [
  { x: 0.5, y: 0.5, color: '#8B5CF6', radius: 8 },
  { x: 0.18, y: 0.22, label: 'Google Maps', color: '#38BDF8', radius: 5 },
  { x: 0.78, y: 0.18, label: 'Directories', color: '#8B5CF6', radius: 5 },
  { x: 0.12, y: 0.72, label: 'Reviews', color: '#34D399', radius: 5 },
  { x: 0.82, y: 0.78, label: 'Social Signals', color: '#38BDF8', radius: 5 },
  { x: 0.62, y: 0.1, label: 'Competitors', color: '#8B5CF6', radius: 4 },
  { x: 0.28, y: 0.85, label: 'Websites', color: '#38BDF8', radius: 4 },
]

const HERO_EDGES = [
  { from: 0, to: 1, color: '#38BDF8', animated: true },
  { from: 0, to: 2, color: '#8B5CF6', animated: true },
  { from: 0, to: 3, color: '#34D399', animated: true },
  { from: 0, to: 4, color: '#38BDF8', animated: true },
  { from: 0, to: 5, color: '#8B5CF6', animated: true },
  { from: 0, to: 6, color: '#38BDF8', animated: true },
]

export function Hero() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center pt-32 pb-24 overflow-hidden border-b border-white/10 bg-transparent font-body"
      aria-label="Hero — Scrape-Verse web intelligence"
    >
      {/* Background Canvas Particles */}
      <div className="absolute inset-0 opacity-35 pointer-events-none">
        <WebCanvas nodes={HERO_NODES} edges={HERO_EDGES} />
      </div>

      {/* Dynamic Ambient Background Glow */}
      <motion.div
        className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full pointer-events-none opacity-20 blur-[140px]"
        style={{
          background: 'radial-gradient(circle, #8B5CF6 0%, #38BDF8 60%, transparent 80%)',
        }}
        animate={{
          scale: [1, 1.08, 1],
          opacity: [0.18, 0.25, 0.18],
        }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Content Grid */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 grid lg:grid-cols-12 gap-12 lg:gap-16 items-center w-full">
        {/* Left Column */}
        <motion.div
          className="lg:col-span-7 space-y-8"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-accent/30 bg-violet-accent/10 text-xs font-mono font-medium text-violet-accent backdrop-blur-md shadow-sm">
            <ShieldCheck className="w-3.5 h-3.5 text-violet-accent" />
            <span>SELF-HEALING WEB INTELLIGENCE</span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-display leading-[1.08] tracking-tight text-text-primary">
            The web changes.
            <br />
            <GradientText className="py-1">
              Your intelligence adapts.
            </GradientText>
          </h1>

          <p className="text-lg sm:text-xl font-body leading-relaxed text-text-secondary max-w-xl">
            Scrape-Verse continuously discovers, researches and monitors businesses across the web — while self-healing when websites change.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <Button id="hero-cta-primary" variant="primary" className="!text-sm !px-7 !py-3.5 shadow-xl shadow-violet-accent/20 flex items-center gap-2">
              <span>Explore the Intelligence Engine</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button id="hero-cta-secondary" variant="secondary" className="!text-sm !px-7 !py-3.5">
              See How It Works
            </Button>
          </div>
        </motion.div>

        {/* Right Column — Floating Glass Card */}
        <motion.div
          className="lg:col-span-5"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <motion.div
            className="glass-level-3 p-8 space-y-6 relative overflow-hidden group"
            animate={{
              y: [0, -6, 0],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            whileHover={{
              scale: 1.02,
              borderColor: 'rgba(56, 189, 248, 0.4)',
              boxShadow: '0 30px 80px rgba(56, 189, 248, 0.15)',
            }}
          >
            {/* Top Shine Accent */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-accent/40 to-transparent" />

            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <span className="font-mono text-xs tracking-widest text-muted uppercase flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-accent" />
                <span>LEAD INTELLIGENCE</span>
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-success/10 text-emerald-success border border-emerald-success/20">
                HIGH OPPORTUNITY
              </span>
            </div>

            {/* Business Info */}
            <div className="space-y-1">
              <h3 className="font-bold font-display text-2xl text-text-primary">
                {BUSINESS_INTEL_EXAMPLE.businessName}
              </h3>
              <p className="text-xs font-mono text-muted">
                {BUSINESS_INTEL_EXAMPLE.location}
              </p>
            </div>

            {/* Metrics Breakdown */}
            <div className="space-y-3 border-t border-b border-white/10 py-4 font-mono text-xs">
              <div className="flex justify-between items-center">
                <span className="text-muted">Website:</span>
                <span className="text-rose-error font-medium flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-error animate-ping" />
                  Not detected
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Rating:</span>
                <span className="text-text-primary font-semibold flex items-center gap-1">
                  <span>{BUSINESS_INTEL_EXAMPLE.rating}</span>
                  <Star className="w-3.5 h-3.5 text-amber-warning fill-amber-warning inline" />
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Reviews:</span>
                <span className="text-text-primary font-semibold">{BUSINESS_INTEL_EXAMPLE.reviews} verified</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Digital Presence:</span>
                <span className="text-blue-accent font-bold">{BUSINESS_INTEL_EXAMPLE.digitalPresenceScore} / 100</span>
              </div>
            </div>

            {/* AI Recommendation */}
            <div className="space-y-2">
              <span className="text-xs font-mono text-muted uppercase">AI Recommendation</span>
              <p className="text-xs font-body text-text-secondary leading-relaxed bg-white/5 p-3.5 rounded-xl border border-white/5">
                &quot;{BUSINESS_INTEL_EXAMPLE.recommendation}&quot;
              </p>
            </div>

            {/* Action Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 rounded-xl font-mono text-xs font-semibold text-blue-accent bg-blue-accent/10 border border-blue-accent/30 hover:bg-blue-accent/20 transition-colors cursor-pointer flex items-center justify-center gap-2"
            >
              <span>View Intelligence Profile</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </motion.button>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-6 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-5 h-9 rounded-full border border-white/15 flex justify-center pt-2 backdrop-blur-sm">
          <div className="w-1 h-2 rounded-full bg-violet-accent" />
        </div>
      </motion.div>
    </section>
  )
}
