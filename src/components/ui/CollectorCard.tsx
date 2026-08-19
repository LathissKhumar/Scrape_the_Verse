'use client'
import { motion, useReducedMotion } from 'framer-motion'
import { NeonBadge } from './NeonBadge'
import type { CollectorStatus } from '@/lib/types'

const HEALTH_COLOR: Record<string, string> = {
  healthy: '#00E5FF',
  running: '#60A5FA',
  healing: '#EC0AFF',
  failed: '#FF1744',
}

export function CollectorCard({ collector }: { collector: CollectorStatus }) {
  const prefersReduced = useReducedMotion()
  const color = HEALTH_COLOR[collector.health] ?? '#A1A1B5'

  return (
    <motion.div
      className="comic-panel bg-[#080810]/80 p-4 space-y-2"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={
        !prefersReduced
          ? { y: -2, boxShadow: '0 0 30px rgba(109,40,217,0.3)' }
          : {}
      }
    >
      <div className="flex items-center justify-between gap-2">
        <span
          className="text-sm font-mono truncate"
          style={{ color: '#F8FAFC' }}
        >
          {collector.displayName}
        </span>
        <NeonBadge
          label={collector.health.toUpperCase()}
          variant={collector.health}
        />
      </div>
      <div
        className="text-2xl font-bold tabular-nums"
        style={{ color, fontFamily: 'var(--font-display)' }}
      >
        {collector.recordsToday.toLocaleString()}
      </div>
      <div className="text-xs font-mono" style={{ color: '#A1A1B5' }}>
        records today
      </div>
      {collector.lastEvent && (
        <div
          className="text-xs font-mono border-t pt-2 truncate"
          style={{ color: '#A1A1B5', borderColor: 'rgba(255,255,255,0.05)' }}
        >
          {collector.lastEventTime} — {collector.lastEvent}
        </div>
      )}
    </motion.div>
  )
}
