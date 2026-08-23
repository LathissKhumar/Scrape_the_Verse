import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800', '900'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'AgencyOS — Self-Healing Web Intelligence Platform',
  description:
    'Self-healing web intelligence for discovering, understanding, and converting business opportunities across the web.',
  icons: {
    icon: '/images/AgencyOS_Logo.png',
    shortcut: '/images/AgencyOS_Logo.png',
    apple: '/images/AgencyOS_Logo.png',
  },
  keywords: [
    'AgencyOS',
    'web scraping',
    'self-healing scrapers',
    'Bright Data',
    'sales intelligence',
    'AI agents',
    'lead generation',
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} font-sans`}
      suppressHydrationWarning
    >
      <body suppressHydrationWarning>{children}</body>
    </html>
  )
}
