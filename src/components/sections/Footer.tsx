'use client'
import { GradientText } from '@/components/ui/GradientText'

export function Footer() {
  return (
    <footer
      className="py-16 relative bg-void border-t border-white/10"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
        {/* Left wordmark */}
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-mono font-bold shadow-md shadow-magenta/20"
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
        </div>

        {/* Center note */}
        <div className="text-xs font-mono text-muted text-center max-w-md">
          Self-Healing Web Intelligence + AI Sales Automation Platform
          <br />
          Built with Bright Data Scraper Studio & Gemini AI
        </div>

        {/* Right copyright */}
        <div className="text-xs font-mono text-muted">
          © 2026 Scrape-Verse. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
