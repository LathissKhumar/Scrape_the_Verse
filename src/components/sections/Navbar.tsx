'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Layers, ArrowRight } from 'lucide-react'
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
  const shadowOpacity = useTransform(scrollY, [0, 50], [0.4, 0.7])

  return (
    <header
      className="fixed top-5 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-2rem)] max-w-7xl font-body transition-all duration-300 pointer-events-auto"
      suppressHydrationWarning
    >
      <motion.div
        className="relative h-16 px-6 sm:px-8 lg:px-10 flex items-center justify-between bg-gradient-to-r from-white/[0.12] via-[#07090D]/50 to-white/[0.12] backdrop-blur-3xl border border-white/30 rounded-2xl overflow-hidden"
        style={{
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5), inset 0 1.5px 1.5px rgba(255, 255, 255, 0.45)',
        }}
      >
        {/* Top Specular Glass Refraction Line */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent pointer-events-none" />

        {/* Brand Logo in Solid Crisp White */}
        <a href="#" className="flex items-center gap-3 group shrink-0" id="nav-logo">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-lg shadow-violet-accent/25 transition-transform group-hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #6D28D9 0%, #8B5CF6 50%, #38BDF8 100%)',
            }}
          >
            <Layers className="w-5 h-5 text-white" />
          </div>
          <span className="font-extrabold text-xl tracking-tight font-display text-white">
            SCRAPE-VERSE
          </span>
        </a>

        {/* Navigation Links */}
        <ul className="hidden md:flex items-center gap-9" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-semibold text-text-primary/90 hover:text-white transition-colors duration-200"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Right CTA */}
        <div className="flex items-center gap-5 shrink-0">
          <a
            href="#hero"
            className="hidden sm:inline-block text-sm font-semibold text-text-primary/90 hover:text-white transition-colors"
          >
            Sign In
          </a>
          <Button id="nav-cta" variant="primary" className="!text-xs !font-bold !px-5 !py-2.5 flex items-center gap-1.5 shadow-xl shadow-violet-accent/25">
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </motion.div>
    </header>
  )
}
