'use client'
import { GradientText } from '@/components/ui/GradientText'

export function Footer() {
  return (
    <footer
      className="border-t py-12 relative overflow-hidden"
      style={{
        borderColor: 'rgba(255,255,255,0.08)',
        backgroundColor: '#05050A',
      }}
    >
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Left wordmark */}
        <div className="flex items-center gap-3">
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
        </div>

        {/* Center note */}
        <div className="text-xs font-mono text-center" style={{ color: '#A1A1B5' }}>
          Self-Healing Web Intelligence + AI Sales Platform · Hackathon Project 2026
        </div>

        {/* Right copyright */}
        <div className="text-xs font-mono" style={{ color: '#A1A1B5' }}>
          Built with Bright Data Scraper Studio & Gemini AI
        </div>
      </div>
    </footer>
  )
}
