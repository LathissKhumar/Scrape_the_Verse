"use client";

import Link from "next/link";

const NAV_LINKS = [
  { label: "Product", href: "#hero" },
  { label: "How It Works", href: "#pipeline" },
  { label: "Self-Healing", href: "#self-healing" },
  { label: "Platform", href: "#scraper-control" },
  { label: "Developers", href: "#architecture" },
];

export function Navbar() {
  return (
    <header
      className="fixed top-3 sm:top-5 lg:top-6 left-3 sm:left-5 lg:left-6 right-3 sm:right-5 lg:right-6 z-50 font-body transition-all duration-300 pointer-events-auto max-w-[1780px] mx-auto rounded-t-[2.5rem] bg-transparent backdrop-blur-[2px] border-b border-white/10"
      suppressHydrationWarning
    >
      <div className="w-full px-6 sm:px-10 lg:px-14 py-3.5 sm:py-4 flex items-center justify-between">
        {/* Far Left Component: Brand Logo */}
        <Link
          href="/"
          className="flex items-center gap-3 group shrink-0"
          id="nav-logo"
        >
          <img
            src="/images/AgencyOS_Logo.png"
            alt="AgencyOS Logo"
            className="w-8 h-8 object-contain transition-transform group-hover:scale-105"
          />
          <span className="font-extrabold text-lg sm:text-xl tracking-tight font-display text-white">
            AgencyOS
          </span>
        </Link>

        {/* Center Aligned Middle Components: Navigation Links */}
        <ul
          className="hidden md:flex items-center justify-center gap-8 lg:gap-11 mx-auto"
          role="list"
        >
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium text-white/80 hover:text-white transition-colors duration-200"
              >
                {link.label}
              </a>
            </li>
          ))}
          <li>
            <Link
              href="/dashboard"
              className="text-sm font-semibold text-sky-400 hover:text-sky-300 transition-colors duration-200"
            >
              AI Dashboard
            </Link>
          </li>
        </ul>

        {/* Far Right Component: Solid White CTA Button */}
        <div className="shrink-0">
          <Link
            href="/dashboard"
            id="nav-cta"
            className="inline-flex items-center justify-center px-5 py-2 rounded-full text-xs sm:text-sm font-bold font-body transition-all duration-200 shadow-lg hover:opacity-95 text-[#07090D] bg-white hover:bg-slate-100 hover:shadow-sky-500/20"
          >
            Launch Console
          </Link>
        </div>
      </div>
    </header>
  );
}
