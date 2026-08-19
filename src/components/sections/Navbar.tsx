'use client'
import { motion, useScroll, useTransform } from 'framer-motion'
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
  const borderOpacity = useTransform(scrollY, [0, 50], [0.08, 0.2])

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 bg-[#05050A]/80 backdrop-blur-xl transition-colors duration-300"
      suppressHydrationWarning
    >
      <motion.div
        className="absolute bottom-0 left-0 right-0 h-px bg-white/10"
        style={{ opacity: borderOpacity }}
      />
      <nav className="relative max-w-7xl mx-auto px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-3 group" id="nav-logo">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-mono font-bold shadow-lg shadow-magenta/20 transition-transform group-hover:scale-105"
            style={{
              background:
                'linear-gradient(135deg, #240044 0%, #6D28D9 30%, #EC0AFF 70%, #00E5FF 100%)',
              color: '#05050A',
            }}
          >
            SV
          </div>
          <span
            className="font-bold text-xl tracking-tight font-display"
          >
            <GradientText>SCRAPE-VERSE</GradientText>
          </span>
        </a>

        {/* Links */}
        <ul className="hidden md:flex items-center gap-8" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium font-body text-muted hover:text-white transition-colors duration-200"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <Button id="nav-cta" variant="primary" className="!text-xs !px-5 !py-2.5 shadow-lg shadow-magenta/20">
          Launch Scrape-Verse
        </Button>
      </nav>
    </header>
  )
}
