'use client'
import { motion, useReducedMotion } from 'framer-motion'

type BadgeVariant = 'healthy' | 'running' | 'healing' | 'failed' | 'info'

const STYLES: Record<BadgeVariant, { dot: string; text: string; border: string }> = {
  healthy: { dot: '#00E5FF', text: '#00E5FF', border: 'rgba(0,229,255,0.3)' },
  running: { dot: '#60A5FA', text: '#60A5FA', border: 'rgba(96,165,250,0.3)' },
  healing: { dot: '#EC0AFF', text: '#EC0AFF', border: 'rgba(236,10,255,0.3)' },
  failed:  { dot: '#FF1744', text: '#FF1744', border: 'rgba(255,23,68,0.3)' },
  info:    { dot: '#A1A1B5', text: '#A1A1B5', border: 'rgba(161,161,181,0.3)' },
}

export function NeonBadge({
  label,
  variant = 'info',
}: {
  label: string
  variant?: BadgeVariant
}) {
  const prefersReduced = useReducedMotion()
  const s = STYLES[variant]
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-mono border"
      style={{ color: s.text, borderColor: s.border }}
    >
      <motion.span
        className="w-1.5 h-1.5 rounded-full shrink-0"
        style={{ backgroundColor: s.dot }}
        animate={!prefersReduced ? { opacity: [1, 0.3, 1] } : {}}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      {label}
    </span>
  )
}
