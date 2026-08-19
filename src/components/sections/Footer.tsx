'use client'
import { Layers } from 'lucide-react'

export function Footer() {
  return (
    <footer className="py-16 relative bg-transparent border-t border-white/10 font-body">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
        {/* Brand in Solid White */}
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md shadow-violet-accent/20"
            style={{
              background: 'linear-gradient(135deg, #6D28D9 0%, #8B5CF6 50%, #38BDF8 100%)',
            }}
          >
            <Layers className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight font-display text-white">
            SCRAPE-VERSE
          </span>
        </div>

        {/* Links */}
        <div className="text-xs font-mono text-text-secondary flex flex-wrap justify-center gap-6">
          <a href="#hero" className="hover:text-text-primary transition-colors">Product</a>
          <a href="#pipeline" className="hover:text-text-primary transition-colors">How It Works</a>
          <a href="#self-healing" className="hover:text-text-primary transition-colors">Self-Healing</a>
          <a href="#scraper-control" className="hover:text-text-primary transition-colors">Platform</a>
          <a href="#architecture" className="hover:text-text-primary transition-colors">Developers</a>
        </div>

        {/* Copyright */}
        <div className="text-xs font-mono text-muted">
          © 2026 Scrape-Verse Inc. Self-Healing Web Intelligence Platform.
        </div>
      </div>
    </footer>
  )
}
