'use client'
import { motion } from 'framer-motion'
import { NeonBadge } from './NeonBadge'
import type { CollectorStatus } from '@/lib/types'
import { formatNumber } from '@/lib/utils'

const HEALTH_COLOR: Record<string, string> = {
  healthy: '#34D399',
  running: '#38BDF8',
  healing: '#818CF8',
  failed: '#FB7185',
}

export function CollectorCard({ collector }: { collector: CollectorStatus }) {
  const color = HEALTH_COLOR[collector.health] ?? '#A7AFBD'

  return (
    <motion.div
      className="p-6 space-y-5 flex flex-col justify-between h-full relative overflow-hidden group rounded-3xl border border-white/18 bg-white/[0.08] shadow-[0_20px_50px_rgba(0,0,0,0.35),inset_0_1px_1px_rgba(255,255,255,0.22)] backdrop-blur-3xl hover:border-white/30 hover:bg-white/[0.12] transition-all"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{
        y: -4,
        scale: 1.01,
      }}
    >
      {/* Top Ambient Glow */}
      <div
        className="absolute -top-12 -right-12 w-28 h-28 rounded-full pointer-events-none opacity-0 group-hover:opacity-20 transition-opacity duration-500 blur-xl"
        style={{ backgroundColor: color }}
      />

      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3.5">
          <span className="text-base font-bold font-display text-text-primary truncate">
            {collector.displayName}
          </span>
          <NeonBadge
            label={collector.health.toUpperCase()}
            variant={collector.health}
          />
        </div>

        <div>
          <motion.div
            className="text-3xl font-bold font-display tabular-nums tracking-tight"
            style={{ color }}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
            suppressHydrationWarning
          >
            {formatNumber(collector.recordsToday)}
          </motion.div>
          <div className="text-xs font-mono text-muted mt-1">
            records processed today
          </div>
        </div>
      </div>

      {collector.lastEvent && (
        <div className="text-xs font-mono text-muted border-t border-white/10 pt-3.5 flex items-center justify-between gap-2">
          <span className="text-text-primary shrink-0">{collector.lastEventTime}</span>
          <span className="truncate">{collector.lastEvent}</span>
        </div>
      )}
    </motion.div>
  )
}
