'use client'
import { motion } from 'framer-motion'
import { NeonBadge } from './NeonBadge'
import type { CollectorStatus } from '@/lib/types'

const HEALTH_COLOR: Record<string, string> = {
  healthy: '#00E5FF',
  running: '#60A5FA',
  healing: '#EC0AFF',
  failed: '#FF1744',
}

export function CollectorCard({ collector }: { collector: CollectorStatus }) {
  const color = HEALTH_COLOR[collector.health] ?? '#A1A1B5'

  return (
    <motion.div
      className="glass-card p-6 space-y-4 flex flex-col justify-between h-full"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -3 }}
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3">
          <span className="text-base font-bold font-display text-off-white truncate">
            {collector.displayName}
          </span>
          <NeonBadge
            label={collector.health.toUpperCase()}
            variant={collector.health}
          />
        </div>

        <div>
          <div
            className="text-3xl font-black font-display tabular-nums"
            style={{ color }}
          >
            {collector.recordsToday.toLocaleString()}
          </div>
          <div className="text-xs font-mono text-muted mt-1">
            records extracted today
          </div>
        </div>
      </div>

      {collector.lastEvent && (
        <div className="text-xs font-mono text-muted border-t border-white/10 pt-3 truncate">
          <span className="text-off-white">{collector.lastEventTime}</span> — {collector.lastEvent}
        </div>
      )}
    </motion.div>
  )
}
