'use client'

export function Footer() {
  return (
    <footer className="py-16 relative bg-transparent border-t border-white/10 font-body">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
        {/* Brand in Solid White */}
        <div className="flex items-center gap-3">
          <img src="/images/AgencyOS_Logo.png" alt="AgencyOS Logo" className="w-8 h-8 object-contain" />
          <span className="font-bold text-xl tracking-tight font-display text-white">
            AgencyOS
          </span>
        </div>

        {/* Links */}
        <div className="text-xs font-mono text-text-secondary flex flex-wrap justify-center gap-6">
          <a href="#hero" className="hover:text-text-primary transition-colors">Product</a>
          <a href="#pipeline" className="hover:text-text-primary transition-colors">The Agents</a>
          <a href="#tech-stack-marquee" className="hover:text-text-primary transition-colors">Tech Stack</a>
          <a href="#lead-scoring" className="hover:text-text-primary transition-colors">Lead Scoring</a>
          <a href="#final-cta" className="hover:text-text-primary transition-colors">Get Started</a>
        </div>

        {/* Copyright */}
        <div className="text-xs font-mono text-muted text-center space-y-1">
          <p>AI-powered lead-to-opportunity engine for web and SEO agencies.</p>
          <p>© 2026 AgencyOS · Built for Hackathon 2026</p>
        </div>
      </div>
    </footer>
  )
}
