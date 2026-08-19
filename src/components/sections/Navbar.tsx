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
  const bgOpacity = useTransform(scrollY, [0, 50], [0.75, 0.95])

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      suppressHydrationWarning
    >
      <motion.div
        className="absolute inset-0 bg-[#07090D] backdrop-blur-xl border-b border-white/10"
        style={{ opacity: bgOpacity }}
      />
      <nav className="relative max-w-7xl mx-auto px-6 lg:px-8 h-20 flex items-center justify-between font-body">
        {/* Brand Logo */}
        <a href="#" className="flex items-center gap-3 group" id="nav-logo">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-lg shadow-violet-accent/20 transition-transform group-hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #6D28D9 0%, #8B5CF6 50%, #38BDF8 100%)',
            }}
          >
            <Layers className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight font-display text-off-white">
            <GradientText>SCRAPE-VERSE</GradientText>
          </span>
        </a>

        {/* Links */}
        <ul className="hidden md:flex items-center gap-8" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors duration-200"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Auth CTA */}
        <div className="flex items-center gap-4">
          <a
            href="#hero"
            className="hidden sm:inline-block text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            Sign In
          </a>
          <Button id="nav-cta" variant="primary" className="!text-xs !px-5 !py-2.5 flex items-center gap-2">
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </nav>
    </header>
  )
}
