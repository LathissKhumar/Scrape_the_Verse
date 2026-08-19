'use client'
import { motion, useScroll, useTransform, useReducedMotion } from 'framer-motion'
import { GradientText } from '@/components/ui/GradientText'
import { Button } from '@/components/ui/Button'

const NAV_LINKS = [
  { label: 'Scraping Engine', href: '#scraper-control' },
  { label: 'Self-Healing', href: '#self-healing' },
  { label: 'AI Agents', href: '#sales-automation' },
  { label: 'Architecture', href: '#architecture' },
]

export function Navbar() {
  const { scrollY } = useScroll()
  const bgOpacity = useTransform(scrollY, [0, 80], [0, 0.95])

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 border-b border-white/5"
      suppressHydrationWarning
    >
      <motion.div
        className="absolute inset-0 backdrop-blur-md bg-[#05050A]"
        style={{ opacity: bgOpacity }}
      />
      <nav className="relative max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Wordmark */}
        <a href="#" className="flex items-center gap-2" id="nav-logo">
          <div
            className="w-7 h-7 rounded flex items-center justify-center text-xs font-bold"
            style={{
              background:
                'linear-gradient(135deg, #240044 0%, #6D28D9 22%, #EC0AFF 45%, #FF1744 68%, #00E5FF 100%)',
              color: '#05050A',
            }}
          >
            SV
          </div>
          <span
            className="font-bold text-lg tracking-tight"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            <GradientText>SCRAPE-VERSE</GradientText>
          </span>
        </a>

        {/* Links */}
        <ul className="hidden md:flex items-center gap-6" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm transition-colors hover:text-white"
                style={{ color: '#A1A1B5', fontFamily: 'var(--font-body)' }}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <Button id="nav-cta" variant="primary" className="!text-xs !px-4 !py-2">
          Launch Scrape-Verse
        </Button>
      </nav>
    </header>
  )
}
