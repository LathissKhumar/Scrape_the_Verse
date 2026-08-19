'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Layers, ArrowRight } from 'lucide-react'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

const NAV_LINKS = [
  { label: 'Product', href: '#hero' },
  { label: 'How It Works', href: '#pipeline' },
  { label: 'Self-Healing', href: '#self-healing' },
  { label: 'Platform', href: '#scraper-control' },
  { label: 'Developers', href: '#architecture' },
]

export function Navbar() {
  const { scrollY } = useScroll()
  const shadowOpacity = useTransform(scrollY, [0, 50], [0.3, 0.6])

  return (
    <header
      className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-2.5rem)] max-w-6xl font-body transition-all duration-300 pointer-events-auto"
      suppressHydrationWarning
    >
      <motion.div
        className="relative h-16 px-6 lg:px-8 flex items-center justify-between bg-[#07090D]/50 backdrop-blur-2xl border border-white/20 rounded-2xl shadow-2xl overflow-hidden"
        style={{
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.3)',
        }}
      >
        {/* Top Specular Glass Shine */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent pointer-events-none" />

        {/* Brand Logo */}
        <a href="#" className="flex items-center gap-3 group shrink-0" id="nav-logo">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md shadow-violet-accent/20 transition-transform group-hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #6D28D9 0%, #8B5CF6 50%, #38BDF8 100%)',
            }}
          >
            <Layers className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight font-display text-off-white">
            <GradientText>SCRAPE-VERSE</GradientText>
          </span>
        </a>

        {/* Navigation Links */}
        <ul className="hidden md:flex items-center gap-8" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-xs font-medium text-text-secondary hover:text-text-primary transition-colors duration-200"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Right CTA */}
        <div className="flex items-center gap-4 shrink-0">
          <a
            href="#hero"
            className="hidden sm:inline-block text-xs font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            Sign In
          </a>
          <Button id="nav-cta" variant="primary" className="!text-xs !px-4 !py-2 flex items-center gap-1.5 shadow-lg shadow-violet-accent/20">
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </motion.div>
    </header>
  )
}
