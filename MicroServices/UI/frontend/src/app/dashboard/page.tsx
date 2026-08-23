import { Metadata } from 'next';
import { DashboardShell } from '@/components/pages';

export const metadata: Metadata = {
  title: 'AI SDR Command Center | Scrape-the-Verse',
  description: 'Autonomous AI SDR agent swarm executing lead discovery, deep parallel analysis, proposal generation, and live AI voice outreach.',
};

export default function DashboardPage() {
  return <DashboardShell />;
}
