import { Navbar } from '@/components/sections/Navbar'
import { Hero } from '@/components/sections/Hero'
import { WebDatabase } from '@/components/sections/WebDatabase'
import { Pipeline } from '@/components/sections/Pipeline'
import { LeadDiscovery } from '@/components/sections/LeadDiscovery'
import { ParallelResearch } from '@/components/sections/ParallelResearch'
import { SelfHealingDemo } from '@/components/sections/SelfHealingDemo'
import { SelfHealingCI } from '@/components/sections/SelfHealingCI'
import { StructuredData } from '@/components/sections/StructuredData'
import { SalesAutomation } from '@/components/sections/SalesAutomation'
import { Monitoring } from '@/components/sections/Monitoring'
import { ScraperControlCenter } from '@/components/sections/ScraperControlCenter'
import { Architecture } from '@/components/sections/Architecture'
import { WhyScrapeVerse } from '@/components/sections/WhyScrapeVerse'
import { FinalCTA } from '@/components/sections/FinalCTA'
import { Footer } from '@/components/sections/Footer'

export default function Home() {
  return (
    <div className="relative min-h-screen bg-void text-off-white selection:bg-magenta selection:text-void overflow-x-hidden">
      <Navbar />
      <main>
        <Hero />
        <WebDatabase />
        <Pipeline />
        <LeadDiscovery />
        <ParallelResearch />
        <SelfHealingDemo />
        <SelfHealingCI />
        <StructuredData />
        <SalesAutomation />
        <Monitoring />
        <ScraperControlCenter />
        <Architecture />
        <WhyScrapeVerse />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  )
}
